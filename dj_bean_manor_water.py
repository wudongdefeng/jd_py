#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/28 5:58 下午
# @File    : dj_bean_manor_water.py
# @Project : jd_scripts
# @Cron    : */40 * * * *
# @Desc    : 京东APP->京东到家->签到->鲜豆庄园, 定时领水滴/浇水
import aiohttp

from dj_bean_manor import DjBeanManor
from utils.process import process_start
from utils.console import println


class DjBeanManorWater(DjBeanManor):
    """
    到家庄园收水滴/浇水
    """
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
            activity_info = await self.get_activity_info(session)
            if not activity_info:
                println('{}, 获取活动ID失败, 退出程序!'.format(self.account))
                return
            await self.collect_watter(session)
            await self.watering(session)


if __name__ == '__main__':
    process_start(DjBeanManorWater, '鲜豆庄园领水/浇水')
