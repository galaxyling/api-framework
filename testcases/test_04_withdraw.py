#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-06-18 19:45
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : test_04_withdraw.py
# @Software: PyCharm
import json
import unittest
import ddt
import jsonpath
from decimal import Decimal
from middlerware.handler import Handler
from common.http_handler import visit
from common.excel_handler import ExcelHandler

yaml = Handler.yaml
excel = Handler.excel
logger = Handler.logger
sheet_name = yaml['excel']['withdrawsheet']
test_data = excel.get_data(sheet_name)


@ddt.ddt
class TestWithdraw(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # 初始化数据库
        logger.info('**********TestWithdrawBegin**********')
        cls.db = Handler.database_cls()
        logger.info('SQL connect')
        cls.excel = ExcelHandler(Handler.excel_path)
        cls.token = Handler().token
        cls.member_id = Handler().member_id
        cls.sql = 'select leave_amount from futureloan.member where id={}'.format(cls.member_id)

    def setUp(self) -> None:
        self.before_money = self.db.query(self.sql)['leave_amount']

    @ddt.data(*test_data)
    def test01_withdraw(self, case_data):
        """提现接口测试"""
        global case_result
        logger.info('**********正在获取第%d条<%s>用例**********' % (case_data['case_id'], case_data['title']))
        data = case_data['data']
        headers = case_data['headers']

        if ('#member_id#' in data) or ('#token#' in headers):
            data = data.replace('#member_id#', str(self.member_id))
            headers = headers.replace('#token#', self.token)

        # 判断是否为取现成功的用例,提取失败用例则不需要进入该流程
        if 'success' in str(case_data['title']):
            if json.loads(data)['amount']:
                # 判断提取金额是否为空,若不为空:则判断提取金额是否大于余额,大于的话调用充值接口保证提现成功能够正常进行
                if Decimal(json.loads(data)['amount']) > self.before_money:
                    # 执行封装的充值接口
                    Handler().recharge_cls()
                    self.before_money = self.db.query(self.sql)['leave_amount']
                    logger.info('账户{},的初始金额小于50W,充值后金额为{}'.format(self.member_id, self.before_money))
        else:
            # 判断用户上的余额是否大于50W,若大于则循环调用取现接口将余额调整至50W以下,保证余额不足用例可以进行
            while self.before_money > 500000:
                logger.info("账户余额大于50W,调用取现接口将金额降至50W以下")
                Handler().withdraw()
                # 重新进行一次数据库查询
                self.before_money = self.db.query(self.sql)['leave_amount']
                if Handler().withdraw() < 500000 and self.before_money < 500000:
                    break

        response = visit(
            url=yaml['host'] + case_data['url'],
            method=case_data['method'],
            json=json.loads(data),
            headers=json.loads(headers)
        )

        try:
            for key, value in json.loads(case_data['expected']).items():
                self.assertEqual(response.json()[key], value)
                # 提取成功用例,校验提取后的余额是否正常
                if response.json()['code'] == 0:
                    after_money = self.db.query(self.sql)['leave_amount']
                    self.assertTrue(self.before_money - Decimal(str(json.loads(data)['amount'])) == after_money)
            case_result = 'pass'
            logger.info('**********第%d条<%s>用例测试结束**********' % (case_data['case_id'], case_data['title']))

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
        logger.info('**********TestWithdrawOver**********')


if __name__ == '__main__':
    unittest.main()
