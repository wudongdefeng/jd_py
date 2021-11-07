#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/22 3:09 下午
# @File    : update_nodejs.py
# @Project : jd_scripts
# @Cron    : 3 3 * * *
# @Desc    : 集成更新nodejs库
import os
import shutil
from config import JS_SCRIPTS_DIR, BASE_DIR


def update():
    """
    :return:
    """
    fake2 = 'https://github.com.cnpmjs.org/shufflewzc/faker2.git'
    hello = 'https://github.com.cnpmjs.org/JDHelloWorld/jd_scripts'

    if os.path.exists(JS_SCRIPTS_DIR):
        os.system('cd {};git reset --hard;git pull;'.format(JS_SCRIPTS_DIR))
    else:
        os.system('git clone {} {};'.format(hello, JS_SCRIPTS_DIR))

    temp_dir = os.path.join(BASE_DIR, 'fake2')

    if os.path.exists(temp_dir):
        os.system('cd {};git pull;'.format(temp_dir))
    else:
        os.system('git clone {} {};'.format(fake2, temp_dir))

    for file in os.listdir(temp_dir):
        if file not in os.listdir(JS_SCRIPTS_DIR):
            if os.path.isdir(os.path.join(temp_dir, file)):
                continue
            shutil.copy(os.path.join(temp_dir, file), os.path.join(JS_SCRIPTS_DIR, file))

    os.system('cd {};npm install;'.format(JS_SCRIPTS_DIR))


if __name__ == '__main__':
    update()
