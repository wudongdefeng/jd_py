#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/29 9:41 上午
# @File    : jd_factory_collect.py
# @Project : jd_scripts
# @Cron    : 10 */1 * * *
# @Desc    : 京东APP->京东电器->东东工厂, 定时收电量
import aiohttp

from jd_factory import JdFactory
from utils.console import println
from utils.process import process_start


class JdFactoryCollect(JdFactory):
    """
    东东工厂收电量
    """

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            is_success = await self.init(session)
            if not is_success:
                println('{}, 无法初始化数据, 退出程序!'.format(self.account))
                return
            await self.collect_electricity(session)


if __name__ == '__main__':
    process_start(JdFactoryCollect, '东东工厂-收电量', help=False)