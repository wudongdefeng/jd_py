#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/16 9:17 上午
# @File    : jd_cnl.py
# @Project : jd_scripts
# @Cron    : 21 6,18 * * *
# @Desc    : 京东APP-送你钞能力

from utils.jd_common import JdCommon
from config import USER_AGENT

CODE_KEY = 'jd_cnl'


class JdCnl(JdCommon):
    """
    众筹许愿池
    """
    appid = '1FFRWxaY'

    code_key = CODE_KEY

    # 请求头
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://h5.m.jd.com/babelDiy/Zeus/YgnrqBaEmVHWppzCgW8zjZj3VjV/index.html',
        'User-Agent': USER_AGENT
    }


if __name__ == '__main__':
    from utils.process import process_start
    process_start(JdCnl, '送你钞能力', code_key=CODE_KEY)



