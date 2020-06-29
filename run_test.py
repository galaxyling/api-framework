#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-06-06 21:26
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : run_test.py
# @Software: PyCharm

import unittest

from middlerware.handler import Handler
from library.HTMLTestRunnerNew import HTMLTestRunner

'''
脚本运行主文件
'''

read_yaml = Handler.yaml
logger = Handler.logger

with open(Handler.file_name, 'wb') as file:
    logger.info('**********正在加载测试用例**********')
    # 加载测试用例
    loader = unittest.TestLoader()
    # 用例收集器
    suite = loader.discover(Handler.fPath.CASE_PATH)

    runner = HTMLTestRunner(
        file,
        title=read_yaml['report']['title'],
        description=read_yaml['report']['description'],
        tester=read_yaml['report']['tester']
    )
    runner.run(suite)
