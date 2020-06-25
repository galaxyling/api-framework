#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-06-11 23:09
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : test_02_login.py
# @Software: PyCharm
import unittest
import ddt
import json

from middlerware.handler import Handler
from common import http_handler
from common.excel_handler import ExcelHandler

logger = Handler.logger
excel = Handler.excel
yaml = Handler.yaml
sheet_name = yaml['excel']['loginsheet']
# 从conf.yaml读取用例excel文件名,以及sheet页
test_data = excel.get_data(sheet_name)


@ddt.ddt
class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info('**********LoginBegin**********')
        cls.excel = ExcelHandler(Handler.excel_path)

    @ddt.data(*test_data)
    def test01_login(self, case_data):
        """用户登陆接口测试"""
        global case_result
        logger.info('**********正在获取第%d条<%s>用例**********' % (case_data['case_id'], case_data['title']))
        response = http_handler.visit(
            url=yaml['host'] + case_data['url'],
            method=case_data['method'],
            json=json.loads(case_data['data']),
            headers=json.loads(case_data['headers'])
        )

        expected = json.loads(case_data['expected'])
        try:
            for key, value in expected.items():
                self.assertEqual(response.json()[key], value)
            logger.info('**********第%d条用例测试结束**********' % case_data['case_id'])
            case_result = "pass"

        except AssertionError as error:
            logger.error("第{}用例出现异常,异常为{}".format(case_data['case_id'], error))
            case_result = 'fail'
            raise error

        finally:
            # 最后执行用例回写操作
            row = case_data['case_id'] + 1
            self.excel.excel_write(name=sheet_name, row=row, column=len(case_data), value=case_result)
            self.excel.excel_write(name=sheet_name, row=row, column=len(case_data) - 1, value=str(response.json()))
            logger.info("Write the response and result: %s " % case_result)

    @classmethod
    def tearDownClass(cls):
        logger.info('**********LoginOver**********')


if __name__ == '__main__':
    unittest.main()
