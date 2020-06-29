#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-05-31 19:54
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : filePath.py
# @Software: PyCharm

import os

'''-----一级目录-----'''
all_path = os.path.dirname(os.path.abspath(__file__))  # 当前项目总目录
CASE_PATH = os.path.join(all_path, 'testcases')  # 测试用例路径
DATA_PATH = os.path.join(all_path, 'data')  # 测试数据路径
CONF_PATH = os.path.join(all_path, 'conf')  # 配置文件目录
REPORT_PATH = os.path.join(all_path, 'reports')  # 测试报告存放路径
