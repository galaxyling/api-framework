#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-06-07 20:52
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : http_handler.py
# @Software: PyCharm

import requests
from common.my_log import MyLog

logger = MyLog('http_handler', 'DEBUG')


def visit(url,
          method,
          params=None,
          data=None,
          json=None,
          **kwargs):
    logger.info('正在使用{}请求,访问 {}'.format(method, url))
    res = requests.request(method,
                           url,
                           params=params,
                           data=data,
                           json=json,
                           **kwargs)

    try:
        logger.info('响应结果为: {},耗时: {}'.format(res, res.elapsed.total_seconds()))
        return res
    except Exception as error:
        logger.error('返回数据不是json格式 {}'.format(error))
        return error


if __name__ == '__main__':
    # url = "http://api.keyou.site:8000/user/login/"
    # info = {
    #     'username':None,
    #     'password':'123456'
    # }
    # data = visit(url=url,method='post',json=info)
    # print(data.json())
    url = 'http://120.78.128.25:8766/futureloan/member/register'
    header = {
        "X-Lemonban-Media-Type": "lemonban.v2"
    }
    info = {
        "mobile_phone": "15033332338",
        "pwd": "12345679123",
        "type": 3
    }
    data = visit(url=url, method='post', json=info, headers=header)
    print(data.json())
