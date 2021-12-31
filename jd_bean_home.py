#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/1 上午11:00
# @Project : jd_scripts
# @File    : jd_bean_home.py
# @Cron    : 45 0 * * *
# @Desc    : 京东APP->我的->签到领京豆->领额外奖励
import asyncio
import json
import random
import time
from urllib.parse import urlencode
from utils.console import println
from utils.process import process_start
from utils.logger import logger
from utils.jd_init import jd_init
import aiohttp

from config import USER_AGENT


def random_string(n=16):
    """
    :param n:
    :return:
    """
    t = "0123456789"
    s = ''

    while len(s) < n:
        s += t[random.randint(0, len(t) - 1)]

    return s


@jd_init
class JdBeanHome:
    """
    领额外京豆
    """

    headers = {
        'referer': 'https://h5.m.jd.com/rn/2E9A2bEeqQqBP9juVgPJvQQq6fJ/index.html',
        'user-agent': USER_AGENT,
        # 'content-type': 'application/x-www-form-urlencoded;'
    }

    eu = random_string(16)
    fv = random_string(16)

    async def request(self, session, function_id='', body=None, method='GET'):
        """
        请求数据
        :param session:
        :param function_id:
        :param body:
        :param method:
        :return:
        """
        try:
            if not body:
                body = {}
            params = {
                'functionId': function_id,
                'appid': 'ld',
                'clientVersion': '10.0.11',
                'client': 'apple',
                'eu': self.eu,
                'fv': self.fv,
                'osVersion': 11,
                'uuid': self.eu + self.fv,
                'openudid': self.eu + self.fv,
                'body': json.dumps(body)
            }
            url = 'https://api.m.jd.com/client.action?' + urlencode(params)
            if method == 'GET':
                response = await session.get(url)
            else:
                response = await session.post(url)

            text = await response.text()
            data = json.loads(text)
            return data

        except Exception as e:
            println(e.args)
            return {
                'code': 999
            }

    @logger.catch
    async def get_award(self, session, source='home'):
        """
        领取奖励
        :param source: 来源
        :param session:
        :return:
        """
        res = await self.request(session, 'beanHomeTask', {"source": source, "awardFlag": True})
        if res['code'] == '0' and 'errorCode' not in res:
            println('{}, 领取京豆奖励, 获得京豆:{}!'.format(self.account, res['data']['beanNum']))
        else:
            message = res.get('errorMessage', '未知')
            println('{}, 领取京豆奖励失败, {}!'.format(self.account, message))

        await asyncio.sleep(2)

    @logger.catch
    async def do_task(self, session):
        """
        :param session:
        :return:
        """
        res = await self.request(session, 'findBeanHome',
                                 {"source": "wojing2", "orderId": 'null', "rnVersion": "3.9", "rnClient": "1"})
        if res['code'] != '0':
            println('{}, 获取首页数据失败!', self.account)
            return False

        if res['data']['taskProgress'] == res['data']['taskThreshold']:
            println('{}, 今日已完成领额外京豆任务!'.format(self.account))
            return

        for i in range(1, 6):
            body = {"type": str(i), "source": "home", "awardFlag": False, "itemId": ""}
            res = await self.request(session, 'beanHomeTask', body)
            if res['code'] == '0' and 'errorCode' not in res:
                println('{}, 领额外京豆任务进度:{}/{}!'.format(self.account, res['data']['taskProgress'],
                                                      res['data']['taskThreshold']))
            else:
                message = res.get('errorMessage', '原因未知')
                println('{}, 第{}个领额外京豆任务完成失败, {}!'.format(self.account, i, message))
            await asyncio.sleep(2)

    @logger.catch
    async def do_goods_task(self, session):
        """
        浏览商品任务
        :return:
        """
        res = await self.request(session, 'homeFeedsList', {"page": 1})
        if res['code'] != '0' or 'errorCode' in res:
            println('{}, 无法浏览商品任务!'.format(self.account))

        if res['data']['taskProgress'] == res['data']['taskThreshold']:
            println('{}, 今日已完成浏览商品任务!'.format(self.account))
            return

        await asyncio.sleep(2)

        for i in range(3):
            body = {
                "skuId": str(random.randint(10000000, 20000000)),
                "awardFlag": False,
                "type": "1",
                "source": "feeds",
                "scanTime": int(time.time() * 1000)
            }
            res = await self.request(session, 'beanHomeTask', body)
            if 'errorCode' in res:
                println('{}, 浏览商品任务, {}!'.format(self.account, res.get('errorMessage', '原因未知')))
                if res['errorCode'] == 'HT203':
                    break
            else:
                println('{}, 完成浏览商品任务, 进度:{}/{}!'.format(self.account, res['data']['taskProgress'],
                                                       res['data']['taskThreshold']))
            await asyncio.sleep(2)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            await self.do_task(session)
            await self.get_award(session)
            await self.do_goods_task(session)
            await self.get_award(session, source='feeds')


if __name__ == '__main__':
    process_start(JdBeanHome, '签到领豆-额外京豆')
