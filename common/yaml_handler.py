#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-05-30 16:03
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : yaml_handler.py
# @Software: PyCharm
import yaml


def get_yaml_data(path):
    """YAML文件获取方法"""
    with open(path, 'r', encoding='utf8') as file:
        data = yaml.load(file, Loader=yaml.SafeLoader)
    return data

# dirs_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# conf_path = os.path.join(dirs_name,'conf/conf.yaml')
#
# test = get_yaml_data(conf_path)
# print(test['log']['level'])
