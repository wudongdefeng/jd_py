#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 1:21 下午
# @File    : jd_cute_pet.py
# @Project : jd_scripts
# @Cron    : 35 6-18/6 * * *
# @Desc    : 京东APP->我的->东东萌宠
import aiohttp
import asyncio
import json
from datetime import datetime
from config import USER_AGENT
from urllib.parse import quote
from utils.logger import logger
from utils.console import println
from utils.process import process_start
from utils.jd_init import jd_init
from db.model import Code

# 东东萌宠助力码
CODE_CUT_PET = 'cut_pet'


@jd_init
class JdCutePet:
    """
    东东萌宠
    """
    headers = {
        'user-agent': USER_AGENT,
        'content-type': 'application/x-www-form-urlencoded',
        'x-requested-with': 'com.jingdong.app.mall',
        'sec-fetch-mode': 'cors',
        'origin': 'https://carry.m.jd.com',
        'sec-fetch-site': 'same-site',
        'referer': 'https://carry.m.jd.com/babelDiy/Zeus/3KSjXqQabiTuD1cJ28QskrpWoBKT/index.html'
    }

    share_code = None  # 互助码
    invite_code = None  # 邀请码

    async def request(self, session, function_id, body=None, wait_time=3):
        """
        :param wait_time:
        :param session:
        :param function_id:
        :param body:
        :return:
        """
        if body is None:
            body = {}
        body["version"] = 2
        body["channel"] = 'app'
        url = 'https://api.m.jd.com/client.action?functionId={}' \
              '&body={}&appid=wh5&loginWQBiz=pet-town&clientVersion=9.0.4'.format(function_id, quote(json.dumps(body)))
        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)

            if wait_time > 0:
                await asyncio.sleep(wait_time)

            if data['code'] != '0':
                return {
                    'resultCode': '-500',
                    'message': '获取数据失败!',
                }
            elif data['resultCode'] != '0':
                return data
            else:
                data['result']['resultCode'] = '0'
                return data['result']

        except Exception as e:
            println('{}, 访问服务器异常:{}!'.format(self.account, e.args))
    
    @logger.catch
    async def help_friend(self, session, max_count=5):
        """
        助力好友
        :param max_count:
        :param session:
        :return:
        """
        item_list = Code.get_code_list(CODE_CUT_PET)
        count = 0
        for item in item_list:
            if count >= max_count:
                break
            friend_account, friend_code = item.get('account'), item.get('code')
            if self.account == friend_account:
                continue
            data = await self.request(session, 'slaveHelp', {
                'shareCode': friend_code
            })
            if data['resultCode'] != '0':
                println('{}, 无法助力好友:{}, {}!'.format(self.account, friend_account, data['message']))
            else:
                count += 1
                println('{}, 成功助力好友:{}!'.format(self.account, friend_account))

    @logger.catch
    async def init(self, session):
        """
        初始化
        :return:
        """
        println('{}, 正在初始化数据...'.format(self.account))
        data = await self.request(session, 'initPetTown')
        if data['resultCode'] != '0':
            println('{}, 无法获取活动首页数据, {}!'.format(self.account, data['message']))
            return False

        if data['userStatus'] == 0:
            println('{}, 萌宠活动未开启, 请手动去京东APP开启活动入口：我的->游戏与互动->查看更多开启！'.format(self.account))

        if 'goodsInfo' not in data:
            println('{}, 暂未选购商品!'.format(self.account))
            self.message += '【商品状态】暂未选择商品!\n'

        self.share_code = data['shareCode']
        self.invite_code = data['inviteCode']
        println('{}的互助码为:{}'.format(self.account, self.share_code))
        println('{}的邀请码为:{}'.format(self.account, self.invite_code))

        if self.share_code: # 保存助力码
            Code.insert_code(code_key=CODE_CUT_PET, code_val=self.share_code, account=self.account, sort=self.sort)

        if data['petStatus'] == 5:
            println('{}, 已可兑换商品!'.format(self.account))
            self.message += '【商品状态】已可兑换商品\n'

        if data['petStatus'] == 6:
            println('{}, 已领取红包, 但未继续领养新的物品!'.format(self.account))
            self.message += '【商品状态】暂未领取新的物品!'

        return True
    
    @logger.catch
    async def get_task_list(self, session):
        """
        获取任务列表
        :param session:
        :return:
        """
        data = await self.request(session, 'taskInit', {'version': 1})
        if data['resultCode'] != '0':
            println('{}, 获取任务列表失败!'.format(self.account))
            return []
        task_list = dict()

        for key in data['taskList']:
            task_list[key] = data[key]

        return task_list
    
    @logger.catch
    async def sign(self, session, task):
        """
        签到任务
        :param session:
        :param task:
        :return:
        """
        if task['finished']:
            println('{}, 今日已完成签到!'.format(self.account))
            return
        data = await self.request(session, 'getSignReward')

        if data['resultCode'] != '0':
            println('{}, 签到失败!'.format(self.account))
        else:
            println('{}, 签到成功, 获得狗粮: {}g!'.format(self.account, data['signReward']))
    
    @logger.catch
    async def first_feed(self, session, task):
        """
        首次喂食
        :param session:
        :param task:
        :return:
        """
        if task['finished']:
            println('{}, 今日已完成首次喂食任务!'.format(self.account))
            return

        data = await self.request(session, 'feedPets')

        if data['resultCode'] != '0':
            println('{}, 首次喂食任务失败!'.format(self.account))
        else:
            println('{}, 完成首次喂食任务, 获得狗粮: {}g!'.format(self.account, data['firstFeedReward']))
    
    @logger.catch
    async def three_meal(self, session, task):
        """
        每日三餐开福袋
        :param session:
        :param task:
        :return:
        """
        cur_hour = datetime.now().hour
        can_do = False

        for i in range(len(task['threeMealTimes'])):
            item_range = [int(n) for n in task['threeMealTimes'][i].split('-')]
            if item_range[0] <= cur_hour <= item_range[1]:
                can_do = True

        if not can_do or task['finished']:
            println('{}, 当前不在每日三餐任务时间范围内或者任务已完成!'.format(self.account))
            return

        data = await self.request(session, 'getThreeMealReward')

        if data['resultCode'] != '0':
            println('{}, 每日三餐任务完成失败!'.format(self.account))
        else:
            println('{}, 完成每日三餐任务成功, 获得狗粮:{}g!'.format(self.account, data['threeMealReward']))
    
    @logger.catch
    async def feed_food_again(self, session):
        """
        再次喂食
        :param session:
        :return:
        """
        println('{}, 再次进行喂食!'.format(self.account))
        data = await self.request(session, 'initPetTown')
        if data['resultCode'] != '0':
            println('{}, 获取活动数据失败!'.format(self.account))
            return

        food_amount = data.get('foodAmount', 0)  # 狗粮总数
        keep_amount = 80  # 保留80狗粮用于完成明天的10次喂食任务

        if (int(food_amount) - keep_amount) > 10:
            times = int((int(food_amount) - keep_amount) / 10)

            for i in range(times):
                println('{}, 正在进行第{}次喂食!'.format(self.account, i+1))
                data = await self.request(session, 'feedPets')
                if data['resultCode'] != '0':
                    println('{}, 第{}次喂食失败, 停止喂食!'.format(self.account, i+1))
                else:
                    println('{}, 第{}次喂食成功!'.format(self.account, i+1))
        else:
            println('{}, 当前狗粮(剩余狗粮{}-保留狗粮{})不足10g ,无法喂食!'.format(self.account, food_amount, keep_amount))

    @logger.catch
    async def feed_reach_hundred(self, session, task):
        """
        每日喂食到100g狗粮
        :param session:
        :param task:
        :return:
        """
        if task['finished']:
            println('{}, 今日已完成喂狗粮{}g任务!'.format(self.account, task['feedReachAmount']))
            return

        had_feed_count = int(task['hadFeedAmount'] / 10)
        need_feed_count = int(task['feedReachAmount'] / 10)

        println('{}, 当前喂食任务进度:{}/{}!'.format(self.account, had_feed_count, need_feed_count))

        for i in range(had_feed_count, need_feed_count):
            data = await self.request(session, 'feedPets')

            if data['resultCode'] != '0':
                if data['resultCode'] == '3003':
                    println('{}, 第{}次喂食失败!, 狗粮剩余不足，退出喂食!'.format(self.account, i+1))
                    break
                else:
                    println('{}, 第{}次喂食失败!'.format(self.account, i + 1))
            else:
                println('{}, 第{}次喂食成功, 进度:{}/{}!'.format(self.account, i + 1, i + 1, need_feed_count))
    
    @logger.catch
    async def browser_task(self, session, task):
        """
        浏览任务
        :param session:
        :param task:
        :return:
        """
        if task['finished']:
            println('{}, 今日已完成浏览任务:{}!'.format(self.account, task['title']))
            return

        body = {
            "index": task['index'], "version": 1, "type": 1
        }
        data = await self.request(session, 'getSingleShopReward', body)

        if data['resultCode'] != '0':
            if data['resultCode'] == '5000':
                println('{}, 已领取浏览任务:{}!'.format(self.account, task['title']))
            else:
                println('{}, 领取浏览任务:{}失败!'.format(self.account, task['title']))
                return
        else:
            println('{}, 领取浏览任务:{}成功!'.format(self.account, task['title']))

        body = {
            "index": task['index'], "version": 1, "type": 2
        }
        data = await self.request(session, 'getSingleShopReward', body)

        if data['resultCode'] != '0':
            println('{}, 完成浏览任务:{}失败!'.format(self.account, task['title']))
        else:
            println('{}, 完成浏览任务:{}成功, 获得{}g狗粮!'.format(self.account, task['title'], data['reward']))
    
    @logger.catch
    async def do_tasks(self, session, task_list):
        """
        做任务
        :param session:
        :param task_list:
        :return:
        """
        func_map = {
            'signInit': self.sign,  # 签到
            'firstFeedInit': self.first_feed,  # 首次喂食
            'threeMealInit': self.three_meal,  # 三餐
            'feedReachInit': self.feed_reach_hundred,  # 投喂百次
            'browseSingleShopInit': self.browser_task,  # 浏览任务
        }
        for key, task in task_list.items():
            if 'browseSingleShopInit' in key:
                await func_map['browseSingleShopInit'](session, task)
            else:
                await func_map[key](session, task)
    
    @logger.catch
    async def pet_sport(self, session):
        """
        遛狗10次
        :param session:
        :return:
        """
        times = 0
        println('{}, 正在遛狗...'.format(self.account))
        while True:
            times += 1
            data = await self.request(session, 'petSport')

            if data['resultCode'] != '0':
                if data['resultCode'] == '1013':
                    println('{}, 第{}次遛狗失败, 有未领取奖励, 去领取!'.format(self.account, times))
                elif data['resultCode'] == '3001':
                    println('{}, 第{}次遛狗失败, 达到宠物运动次数上限!'.format(self.account, times))
                    break
                else:
                    println('{}, 第{}次遛狗失败, 结束遛狗!'.format(self.account, times))
                    break
            food_reward = data['foodReward']

            println('{}, 完成一次遛狗, 正在领取遛狗奖励!'.format(self.account))

            data = await self.request(session, 'getSportReward')

            if data['resultCode'] != '0':
                println('{}, 领取第{}次遛狗奖励失败, 结束遛狗!'.format(self.account, times))
            else:
                println('{}, 成功领取第{}次遛狗奖励, 获得狗粮:{}g, 当前狗粮:{}g!'.format(self.account, times,
                                                                       food_reward, data['foodAmount']))
    
    @logger.catch
    async def collect_energy(self, session):
        """
        收取好感度
        :param session:
        :return:
        """
        println('{}, 正在收取好感度...'.format(self.account))

        data = await self.request(session, 'energyCollect')
        if data['resultCode'] != '0':
            println('{}, 收取好感度失败!'.format(self.account))
            return

        message = '【第{}块勋章完成进度】{}%，' \
                  '还需收集{}好感度!\n'.format(data['medalNum'] + 1, data['medalPercent'], data['needCollectEnergy'])
        message += '【已获得勋章】{}块，还需收集{}块即可兑换奖品!\n'.format(data['medalNum'], data['needCollectMedalNum'])

        self.message += message
        println('{}, 收集好感度成功!{}'.format(self.account, message))
    
    @logger.catch
    async def get_friend_help_award(self, session):
        """
        获取好友助力奖励
        :param session:
        :return:
        """
        data = await self.request(session, 'masterHelpInit')
        if data['resultCode'] != '0':
            println('{}, 无法获取好友助力信息!'.format(self.account))
            return

        if int(data['reward']) > 50:
            println('{}, 好友助力额外奖励已领取!'.format(self.account))
            return

        if not data['helpLimitFlag']:
            println('{}, 好友助力不满{}人, 无法领取奖励!'.format(self.account, data['helpLimit']))
            return

        data = await self.request(session, 'getHelpAddedBonus')

        if data['resultCode'] != '0':
            println('{}, 领取好友助力奖励失败!'.format(self.account))
            return

        println('{}, 领取好友助力奖励成功, 获得狗粮:{}g!'.format(self.account, data['reward']))

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self.cookies, headers=self.headers) as session:
            self.message = '【活动名称】东东萌宠\n【京东账号】{}\n'.format(self.account)
            is_success = await self.init(session)
            if not is_success:
                println('{}, 初始化失败, 退出程序!'.format(self.account))
                return
            task_list = await self.get_task_list(session)
            await self.do_tasks(session, task_list)
            await self.pet_sport(session)
            await self.feed_food_again(session)  # 再次喂食
            await self.collect_energy(session)
            await self.get_friend_help_award(session)
            self.message = None

    async def run_help(self):
        """
        助力入口
        :return:
        """
        async with aiohttp.ClientSession(cookies=self.cookies, headers=self.headers) as session:
            await self.help_friend(session)


if __name__ == '__main__':
    process_start(JdCutePet, '东东萌宠', code_key=CODE_CUT_PET)
