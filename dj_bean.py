#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/28 2:06 下午
# @File    : dj_bean.py
# @Project : jd_scripts
# @Cron    : 45 7,12,19 * * *
# @Desc    : 京东APP->京东到家->签到->所有任务
import aiohttp
import asyncio
from utils.console import println
from utils.dj_init import dj_init
from utils.logger import logger


@dj_init
class DjBean:
    """
    京东到家相关活动基类
    """
    has_sign = False  # 是否已签到
    points = 0  # 当前鲜豆数量
    already_sign_days = 0  # 当前已签到天数

    @logger.catch
    async def get_task_award(self, session, task):
        """
        获取任务奖励鲜豆
        :param task:
        :param session:
        :return:
        """
        body = {
            "modelId": task['modelId'],
            "taskId": task['taskId'],
            "taskType": task['taskType'],
            "plateCode": 3
        }
        res = await self.get(session, 'task/sendPrize', body)
        if res['code'] != '0':
            println('{}, 无法领取任务:《{}》奖励!'.format(self.account, task['taskName']))
        else:
            println('{}, 成功领取任务: 《{}》奖励!'.format(self.account, task['taskName']))

    @logger.catch
    async def init(self, session):
        """
        :return:
        """
        body = {
            "cityId": "1601",
            "platform": 4,
            "longitude": self.lng,
            "latitude": self.lat,
            "source": "H5",
            "ifCIC": 0
        }
        res = await self.get(session, 'signin/showSignInMsgNew', body)

        if res['code'] != '0':
            println('{}, 无法初始化数据!'.format(self.account))
            return False

        user_info = res['result']['userInfoResponse']

        self.points = user_info.get('points', 0)
        self.has_sign = user_info['hasSign']
        self.already_sign_days = user_info['alreadySignInDays']

        return True

    @logger.catch
    async def daily_sign(self, session):
        """
        每日签到
        :param session:
        :return:
        """
        if self.has_sign:
            println('{}, 今日已签到, 已连续签到{}天!'.format(self.account, self.already_sign_days))
            return
        body = {
            "channel": "qiandao_indexball",
            "cityId": self.city_id,
            "longitude": self.lng,
            "latitude": self.lat,
            "ifCic": 0
        }
        res = await self.get(session, 'signin/userSigninNew',  body)

        if res['code'] != '0':
            println('{}, 签到失败!'.format(self.account))
        else:
            println('{}, 签到成功!'.format(self.account))

    @logger.catch
    async def do_task(self, session):
        """
        做任务
        :param session:
        :return:
        """
        res = await self.get(session, 'task/list', {"modelId": "M10001","plateCode": 3})
        if res['code'] != '0':
            println('{}, 获取任务列表失败!'.format(self.account))
            return

        task_list = res['result']['taskInfoList']

        for task in task_list:
            task_type = task['taskType']
            task_name = task['taskName']

            if task['status'] == 2:
                await self.get_task_award(session, task)
                continue

            if task['status'] == 3:
                println('{}, 任务:《{}》今日已完成!'.format(self.account, task_name))
                continue

            if task_type in [506, 513, 801]:  # 下单返鲜豆 7天三单任务
                println('{}, 任务:《{}》无法完成, 请手动完成!'.format(self.account, task_name))
                continue
            elif task_type in [901, 310]:
                await self.browse_task(session, task)
                await asyncio.sleep(1)
                await self.get_task_award(session, task)
            else:
                await self.receive_task(session, task)

    async def run(self):
        """
        程序入口
        :return:
        """
        async with aiohttp.ClientSession(cookies=self.cookies, headers=self.headers) as session:
            dj_cookies = await self.login(session)
            if not dj_cookies:
                return
            println('{}, 登录成功...'.format(self.account))

        async with aiohttp.ClientSession(cookies=dj_cookies, headers=self.headers) as session:
            success = await self.init(session)
            if not success:
                println('{}, 初始化失败, 退出程序!'.format(self.account))
                return
            await self.daily_sign(session)
            await self.do_task(session)


if __name__ == '__main__':
    from utils.process import process_start
    process_start(DjBean, '京东到家-赚鲜豆')
