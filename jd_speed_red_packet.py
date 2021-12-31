#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File         : jd_speed_red_packet.py
# @Project      : jd_scripts
# @Time         : 2021-09-20 10:18:08
# @Cron         : 20 0,22 * * *
# @Desc         : 京东极速版红包-自动提现微信现金


import asyncio

import aiohttp
from jd_speed_sign import JdSpeedSign
from utils.console import println
from utils.process import process_start


class JdSpeedRedPocket(JdSpeedSign):
    """京东极速版签到红包

    Args:
        JdSpeedSign ([type]): [description]
    """
    headers = {
        "Host": "api.m.jd.com",
        'Origin': 'https://daily-redpacket.jd.com',
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "User-Agent": "jdltapp;iPhone;3.3.2;14.5.1network/wifi;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone13,2;addressid/137923973;hasOCPay/0;appBuild/1047;supportBestPay/0;pv/467.11;apprpd/MyJD_Main;",
        "Accept-Language": "zh-Hans-CN;q=1, en-CN;q=0.9, zh-Hant-CN;q=0.8",
        'Referer': 'https://daily-redpacket.jd.com/?activityId=9WA12jYGulArzWS7vcrwhw',
        "Accept-Encoding": "gzip, deflate, br"
    }
    linkId = "9wdf1YTT2L59Vr-meKskLA"
    signLinkId = '9WA12jYGulArzWS7vcrwhw'

    async def sign_withdraw(self, session):
        """极速版签到提现
        """
        body = {
            "linkId": self.signLinkId,
            "serviceName": "dayDaySignGetRedEnvelopeSignService",
            "business": 1
        }
        data = await self.request(session, 'apSignIn_day', body, 'POST')
        try:
            if data['retCode'] == 0:
                println(f'{self.account}, 极速版签到提现：签到成功!')
            else:
                println('{}, 极速版签到提现：签到失败({})'.format(self.account, data['retMessage']))
        except Exception as e:
            println('{}, 极速版签到提现：签到异常 {} ({})!'.format(self.account, e.args, data))
                
    async def reward_query(self, session):
        """查询 天天开红包
        """        
        body = {
            "inviter": "" if self.sort == 0 else "6BiQpD6BRBeIyFFIZD7M9A",
            'linkId': self.linkId
        }
        data = await self.request(session, 'spring_reward_query', body)
        try:
            if data['remainChance'] > 0:
                times = data['remainChance']
                println(f'{self.account}, 你还有{times}次机会...')
                while times > 0:
                    println('{}, 第{}次开始开启红包'.format(self.account, data['remainChance'] - times + 1))
                    await self.red_packet(session)
                    await asyncio.sleep(1)
                    times -= 1
            else:
                println('{}, 已经没有开启红包机会'.format(self.account))
        except Exception as e:
            println('{}, 签到 {} ({})!'.format(self.account, e.args, data))

    async def red_packet(self, session):
        """天天红包-开红包
        """
        body = body = {
            'inviter': '' if self.sort == 0 else '6BiQpD6BRBeIyFFIZD7M9A',
            'linkId': self.linkId
        }
        data = await self.request(session, 'spring_reward_receive', body)
        try:
            if data['received']['prizeType'] != 1:
                println('{}, 获得{}'.format(self.account, data['received']['prizeDesc']))
            else:
                println('{}, 获得优惠券'.format(self.account))
        except Exception as e:
            println('{}, 异常 {} ({})!'.format(self.account, e.args, data))

    async def get_packet_list(self, session):
        """获取天天开红包列表
        """
        body = {
            "pageNum": 1,
            "pageSize": 20,
            'linkId': self.linkId,
            "inviter": ""
        }
        data = await self.request(session, 'spring_reward_list', body)
        try:
            for red in data['items']:
                if red['prizeType'] != 4:
                    continue
                println('{}, 去提现{}微信现金'.format(self.account, red['amount']))
                await self.cash_out(session, red['id'],red['poolBaseId'],red['prizeGroupId'], red['prizeBaseId'])
        except Exception as e:
            println('{}, 异常 {} ({})!'.format(self.account, e.args, data))

    async def cash_out(self, session, id, poolBaseId, prizeGroupId, prizeBaseId):
        """提现微信红包
        """
        body = {
            "businessSource": "SPRING_FESTIVAL_RED_ENVELOPE",
            "base": {
                "id": id,
                "business": None,
                "poolBaseId": poolBaseId,
                "prizeGroupId": prizeGroupId,
                "prizeBaseId": prizeBaseId,
                "prizeType": 4
            },
            'linkId': self.linkId,
            "inviter": ""
        }
        data = await self.request(session, 'apCashWithDraw', body, 'POST')
        try:
            if data['status'] == 310:
                println('{}, 提现成功'.format(self.account))
            else:
                println('{}, 提现失败 {}'.format(self.account, data['message']))
        except Exception as e:
            println('{}, 提现异常 {} ({})!'.format(self.account, e.args, data))

    async def sign_prize_detail_list(self, session):
        """签到提现-奖品列表
        """
        body = {
            "linkId": self.signLinkId,
            "serviceName": "dayDaySignGetRedEnvelopeSignService",
            "business": 1,
            "pageSize": 20,
            "page": 1
        }
        data = await self.request(session, 'signPrizeDetailList', body, 'POST')
        try:
            if data['code'] == 0:
                for item in data['prizeDrawBaseVoPageBean']['items']:
                    if item['prizeType'] != 4 or item['prizeStatus'] != 0:
                        continue
                    println('{}, 极速版签到提现，去提现{}现金'.format(self.account, item['prizeValue']))
                    await self.ap_cash_with_draw(session, item['id'], item['poolBaseId'], item['prizeGroupId'], item['prizeBaseId'])
            else:
                println('{}, 极速版签到查询奖品：失败{}'.format(self.account, data['message']))
        except Exception as e:
            println('{}, 极速版签到查询奖品：失败 {} ({})!'.format(self.account, e.args, data))

    async def ap_cash_with_draw(self, session, id, poolBaseId, prizeGroupId, prizeBaseId):
        """ 签到现金-微信提现红包
        """
        body = body = {
            "linkId": self.signLinkId,
            "businessSource": "DAY_DAY_RED_PACKET_SIGN",
            "base": {
                "prizeType": 4,
                "business": "dayDayRedPacket",
                "id": id,
                "poolBaseId": poolBaseId,
                "prizeGroupId": prizeGroupId,
                "prizeBaseId": prizeBaseId
            }
        }
        data = await self.request(session, 'apCashWithDraw', body, 'POST')
        try:
            if data['status'] == 310:
                println('{}, 提现成功'.format(self.account))
            else:
                println('{}, 提现失败 {}'.format(self.account, data['message']))
        except Exception as e:
            println('{}, 提现异常 {} ({})!'.format(self.account, e.args, data))

    async def run(self):
        """run
        """
        async with aiohttp.ClientSession(cookies=self.cookies) as session:
            await self.sign_withdraw(session)
            await self.reward_query(session)
            await self.get_packet_list(session)
            await self.sign_prize_detail_list(session)

        
if __name__ == '__main__':
    # from config import JD_COOKIES
    # app = JdSpeedRedPocket(**JD_COOKIES[0])
    # asyncio.run(app.run())

    process_start(JdSpeedRedPocket, '京东极速版红包签到')