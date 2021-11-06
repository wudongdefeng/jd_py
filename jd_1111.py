#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/16 9:17 上午
# @File    : jd_cnl.py
# @Project : jd_scripts
# @Cron    : 21 7,22 * * *
# @Desc    : 京东APP-1111点心动

from utils.jd_common import JdCommon
from config import USER_AGENT

CODE_KEY = 'jd_1111'


class Jd1111(JdCommon):
    """
    1111点心动
    """
    appid = '1FFVQyqw'

    code_key = CODE_KEY

    # 请求头
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://h5.m.jd.com/babelDiy/Zeus/YgnrqBaEmVHWppzCgW8zjZj3VjV/index.html',
        'User-Agent': USER_AGENT
    }


if __name__ == '__main__':
    from utils.process import process_start
    process_start(Jd1111, '1111点心动', code_key=CODE_KEY)






# 1FFVQyqw