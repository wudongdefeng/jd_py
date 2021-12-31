#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/27 2:16 下午
# @File    : jx_sign.py
# @Project : jd_scripts
# @Cron    : 10 10 * * *
# @Desc    : 京喜APP->首页->签到领红包
import asyncio
import json
import re

import aiohttp
from urllib.parse import urlencode
from datetime import datetime


from config import USER_AGENT
from utils.jx_init import jx_init
from utils.console import println
from utils.process import process_start
from utils.logger import logger
from db.model import Code


CODE_KEY = 'jx_sign'


@jx_init
class JxSign:

    headers = {
        'user-agent': USER_AGENT.replace('jdapp;', 'jdpingou;'),
        'referer': 'https://st.jingxi.com/'
    }

    @logger.catch
    async def request(self, session, path, body=None, method='GET'):
        """
        请求数据
        :param session:
        :param path:
        :param body:
        :param method:
        :return:
        """
        try:
            time_ = datetime.now()
            params = {
                'type': 1,
                'signhb_source': 5,
                'smp': '',
                'ispp': 0,
                'tk': '',
                'sqactive': '',
                '_': int(time_.timestamp() * 1000) + 2,
                'sceneval': '2',
                'g_login_type': '1',
                'callback': '',
                'g_ty': 'ls',
            }
            if not body:
                body = dict()
            params.update(body)
            url = 'https://m.jingxi.com/fanxiantask/signhb/{}?'.format(path) + urlencode(params)
            h5st = await self.encrypt(time_, url)
            url += '&h5st=' + h5st
            if method == 'GET':
                response = await session.get(url=url)
            else:
                response = await session.post(url=url)

            text = await response.text()
            try:
                return json.loads(text)
            except:
                text = re.search('\((.*)\);', text, re.S)
                if not text:
                    return None
                text = text.group(1)
                data = json.loads(text)
                return data

        except Exception as e:
            println('{}, 请求服务器数据失败, {}'.format(self.account, e.args))
            return None

    @logger.catch
    async def do_tasks(self, session):
        """
        做任务
        :param session:
        :return:
        """
        item_list = Code.get_code_list(code_key=CODE_KEY)

        if not item_list:
            smp = '261af081174422b9fd98eca682071a09'
        else:
            smp = item_list[0]['code']

        res = await self.request(session, 'query', {
            'smp': smp,
            '_stk': 'ispp,signhb_source,smp,tk,type'
        })
        if not res or res.get('ret') != 0:
            println('{}, 获取任务列表失败!'.format(self.account))
            return

        code = res['smp']
        println('{}, 助力码:{}'.format(self.account, code))
        Code.insert_code(code_key=CODE_KEY, code_val=code, account=self.account, sort=self.sort)
        task_list = res['commontask']

        for task in task_list:
            if task['status'] == 2:
                println('{}, 任务:《{}》已完成!'.format(self.account, task['taskname']))
                continue
            res = await self.request(session, 'dotask', {
                'task': task['task'],
                '_stk': 'ispp,signhb_source,sqactive,task,tk',
            })
            if res.get('ret') == 0:
                println('{}, 完成任务:《{}》, 获得红包:{}'.format(self.account, task['taskname'], res['sendhb']))
            else:
                println('{}, 无法完成任务:《{}》!'.format(self.account, task['taskname']))
            await asyncio.sleep(3)

    @logger.catch
    async def open_box(self, session):
        """
        开宝箱
        :param session:
        :return:
        """
        for i in range(10):
            res = await self.request(session, 'bxdraw')
            if res.get('ret') == 0:
                println('{}, 开宝箱成功, 获得红包:{}'.format(self.account, res['sendhb']))
            else:
                break
            await asyncio.sleep(3)

    async def run(self):
        """
        :return:
        """
        await self.get_encrypt()
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            await self.do_tasks(session)
            await self.open_box(session)


if __name__ == '__main__':
    process_start(JxSign, '京喜-签到领红包')
