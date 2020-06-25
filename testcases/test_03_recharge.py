#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-06-16 23:05
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : test_03_recharge.py
# @Software: PyCharm
import unittest
import ddt
import json
from decimal import Decimal
from middlerware.handler import Handler
from common.http_handler import visit
from common.excel_handler import ExcelHandler

yaml = Handler.yaml
excel = Handler.excel
logger = Handler.logger
sheet_name = yaml['excel']['rechargesheet']
test_data = excel.get_data(sheet_name)


@ddt.ddt
class TestRecharge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logger.info('**********TestRechargeBegin**********')
        cls.token = Handler().token
        cls.member_id = Handler().member_id
        logger.info('SQL connect')
        cls.db = Handler.database_cls()
        cls.excel = ExcelHandler(Handler.excel_path)

    def setUp(self) -> None:
        # 充值之前查询数据库余额
        self.sql = 'select leave_amount from futureloan.member where id={};'.format(self.member_id)
        self.before_money = self.db.query(self.sql)['leave_amount']

    @ddt.data(*test_data)
    def test_01_recharge(self, case_data):
        """用户充值接口测试"""
        global case_result
        logger.info('**********正在获取第%d条<%s>用例**********' % (case_data['case_id'], case_data['title']))
        data = case_data['data']
        if '#member_id#' in case_data['data']:
            data = data.replace('#member_id#', str(self.member_id))

        headers = case_data['headers']
        if '#token#' in case_data['headers']:
            headers = headers.replace('#token#', self.token)

        response = visit(
            url=yaml['host'] + case_data['url'],
            method=case_data['method'],
            json=json.loads(data),
            headers=json.loads(headers)
        )

        try:
            for key, value in json.loads(case_data['expected']).items():
                self.assertEqual(response.json()[key], value)
            if response.json()['code'] == 0:
                logger.info('查询数据库,是否充值成功')
                # 查询充值后的余额,用于比对
                after_money = self.db.query(self.sql)['leave_amount']
                self.assertTrue(self.before_money + Decimal(str(json.loads(data)['amount'])) == after_money)
            logger.info('**********第%d条<%s>用例测试结束**********' % (case_data['case_id'], case_data['title']))
            case_result = 'pass'

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
    def tearDownClass(cls) -> None:
        cls.db.close()
        logger.info('SQL disconnect')
        logger.info('**********TestRechargeOver**********')


if __name__ == '__main__':
    unittest.main()
