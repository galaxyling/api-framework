#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-05-30 16:06
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : my_log.py
# @Software: PyCharm

import logging
import os
import time


class MyLog(logging.Logger):
    def __init__(self, name, level):
        super().__init__(name, level)
        self.setLevel(level)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        self.addHandler(stream_handler)

        '''设置log存放路径并以时间命名log文件'''
        dirs_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_path = os.path.join(dirs_name, 'logs')  # /Users/mymacbook/Desktop/auto-framework/logs

        logfile_name = time.strftime("%Y-%m-%d")
        now_file = os.path.join(log_path, logfile_name)

        if not os.path.exists(now_file):
            os.mkdir(now_file)
        log_name = time.strftime("%Y%m%d %H:%M") + '.log'
        end_path = log_path + '/' + logfile_name + '/' + log_name
        # 配置log文件输出
        file_handler = logging.FileHandler(end_path, encoding='utf8')
        file_handler.setLevel(level)
        self.addHandler(file_handler)

        fmt = logging.Formatter('%(asctime)s - [%(filename)s--line:%(lineno)d - %(levelname)s]:%(message)s')
        stream_handler.setFormatter(fmt)
        file_handler.setFormatter(fmt)

        logging.basicConfig()


if __name__ == '__main__':
    logger = MyLog('run.txt', 'DEBUG')

    logger.debug('debug信息')
    logger.info('info信息')
    logger.warning('warning信息')
    logger.error('error信息')
    logger.critical('critical信息')
