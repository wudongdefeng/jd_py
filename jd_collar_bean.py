#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/26 9:55 上午
# @File    : jd_collar_bean.py
# @Project : jd_scripts
# @Cron : 6 1 * * *
# @Desc    : 京东APP首页->领京豆->升级赚京豆
import json
import math
import random
import asyncio
import aiohttp

from urllib.parse import quote
from utils.console import println
from utils.logger import logger
from utils.jd_init import jd_init
from config import USER_AGENT


def random_string(e=40):
    """
    生成随机字符串
    :param e:
    :return:
    """
    t = "abcdefhijkmnprstwxyz123456789"
    len_ = len(t)
    s = ""
    for i in range(e):
        s += t[math.floor(random.random() * len_)]
    return s


@jd_init
class JdCollarBean:
    """
    领京豆
    """
    headers = {
        'User-Agent': USER_AGENT,
        'Host': 'api.m.jd.com',
        'Connection': 'keep-alive',
        'Accept-Language': 'zh-cn',
        'Referer': 'https://h5.m.jd.com/rn/42yjy8na6pFsq1cx9MJQ5aTgu3kX/index.html',
    }

    id = random_string(40)
    
    async def request(self, session, function_id='', body=None, method='GET'):
        """
        请求数据
        :return:
        """
        try:
            if not body:
                body = {}
            url = 'https://api.m.jd.com/client.action?' \
                  'functionId={}&body={}&appid=ld&client=m&' \
                  'uuid={}&openudid={}'.format(function_id, quote(json.dumps(body)), self.id, self.id)
            if method == 'GET':
                response = await session.get(url)
            else:
                response = await session.post(url)
            text = await response.text()
            data = json.loads(text)
            return data
        except Exception as e:
            println('{}, 获取数据失败:{}!'.format(self.account, e.args))
    
    @logger.catch
    async def do_task(self, session):
        """
        做任务
        :param session:
        :return:
        """
        data = await self.request(session, 'beanTaskList', {"viewChannel": "AppHome"})
        if data['code'] != '0':
            println('{}, 获取任务失败!'.format(self.account))
            return
        data = data['data']

        for task in data['taskInfos']:
            task_name = task['taskName']

            if task['status'] == 2:  # 任务已完成
                continue
            if task['taskType'] == 3:
                action_type = 0
            else:
                action_type = 1
            res = await self.request(session, 'beanDoTask', {
                "actionType": action_type,
                "taskToken": task['subTaskVOS'][0]['taskToken']
            })

            if 'errorCode' in res:
                println('{}, 任务:{}, {}'.format(self.account, task_name, res['errorMessage']))
            elif 'data' in res and 'bizMsg' in res['data']:
                println('{}, 任务:{},  {}'.format(self.account, task_name, res['data']['bizMsg']))
            else:
                println('{}, 任务:{}, {}'.format(self.account, task_name, res))

            if task['taskType'] != 3:
                println('{}, 任务:{}等待5秒...'.format(self.account, task_name))
                await asyncio.sleep(5)
                res = await self.request(session, 'beanDoTask',
                                         {"actionType": 0, "taskToken": task['subTaskVOS'][0]['taskToken']})

                if 'data' in res and 'bizMsg' in res['data']:
                    println('{}, 任务:{},  {}'.format(self.account, task_name, res['data']['bizMsg']))
                elif 'errorCode' in res:
                    println('{}, 任务:{}, {}'.format(self.account, task_name, res['errorMessage']))
                else:
                    println('{}, 任务:{}, {}'.format(self.account, task_name, res))

            await asyncio.sleep(3)

    async def run(self):
        """
        入口
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            println('{}, 正在做任务!'.format(self.account))
            for i in range(3):
                await self.do_task(session)
            println('{}, 任务已做完!'.format(self.account))


if __name__ == '__main__':
    from utils.process import process_start
    process_start(JdCollarBean, '领京豆')
