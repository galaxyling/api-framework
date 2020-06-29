#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-06-21 23:06
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : test_07_invest.py
# @Software: PyCharm
import json
import unittest
import ddt
from decimal import Decimal

from common.excel_handler import ExcelHandler
from middlerware.handler import Handler
from common.http_handler import visit

yaml = Handler.yaml
excel = Handler.excel
logger = Handler.logger
sheet_name = yaml['excel']['investsheet']
test_data = excel.get_data(sheet_name)


@ddt.ddt
class TestInvest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logger.info("------------------------------TestInvestBegin------------------------------")

    @classmethod
    def tearDownClass(cls) -> None:
        logger.info("------------------------------TestInvestOver------------------------------")

    def setUp(self) -> None:
        # 实例化db以及ExcelHandler对象
        self.db = Handler.database_cls()
        self.excel = ExcelHandler(Handler.excel_path)

        # 执行前前查询金额
        self.amount_sql = "select leave_amount from futureloan.member where id = {}".format(Handler().member_id)
        self.before_money = self.db.query(self.amount_sql)['leave_amount']

        # 执行前查询投资前invest投资记录
        self.invest_num_sql = "select count(*) from futureloan.invest where member_id = {};".format(Handler().member_id)
        self.before_invest_num = self.db.query(self.invest_num_sql)['count(*)']

    def tearDown(self) -> None:
        self.db.close()

    @ddt.data(*test_data)
    def test_01_invest(self, case_data):
        """投资接口测试"""
        global case_result
        logger.info('**********正在获取第%d条<%s>用例**********' % (case_data['case_id'], case_data['title']))

        # 调用正则表达式,替换数据中所有的以##表示的动态数据,并进行替换对应的属性
        # 此处正则替换时会调用接口新增并审核一个项目返回loan_id
        case_data = Handler().replace_data(str(case_data))
        case_data = eval(case_data)
        if "success" in case_data["precondition"]:
            if self.before_money < 200000:
                logger.info("账户余额不足20W,调用充值接口进行充值")
                Handler().recharge_cls()
                self.before_money = self.db.query(self.amount_sql)["leave_amount"]

        else:
            # 投资账户余额不足用例,将账户余额调整至20W以下,保证账户余额的用例可以进行
            while self.before_money > 200000:
                logger.info("账户余额大于20W,调用提现接口进行提现")
                Handler().withdraw()
                self.after_money = self.db.query(self.amount_sql)["leave_amount"]
                if self.after_money < 200000:
                    break

        data = json.loads(case_data['data'])

        response = visit(
            url=yaml['host'] + case_data['url'],
            method=case_data['method'],
            json=data,
            headers=json.loads(case_data['headers'])
        )

        expected = json.loads(case_data['expected'])


        try:
            self.assertEqual(response.json()["code"], expected["code"])
            self.assertEqual(response.json()["msg"], expected["msg"])
            if response.json()["code"] == 0:
                status_sql = "select `status` from futureloan.loan where id={}".format(data["loan_id"])
                after_status = self.db.query(status_sql)['status']

                # 投资成功用例,查看数据库对应项目状态是否发生改变
                self.assertEqual(expected["status"], after_status)

                # 充值成功的用例,查询投资账户金额是否响应减少
                self.invest_after_money = self.db.query(self.amount_sql)['leave_amount']
                self.assertTrue(self.before_money - Decimal(str(data['amount'])) == self.invest_after_money)

                # 断言是否增加一条投资记录
                after_invest_num = self.db.query(self.invest_num_sql)["count(*)"]
                self.assertTrue(self.before_invest_num + 1 == after_invest_num)
            logger.info('**********第%d条<%s>用例测试结束**********' % (case_data['case_id'], case_data['title']))
            case_result = 'pass'

        except AssertionError as error:
            logger.error("第{}用例出现异常,异常为{}".format(case_data['case_id'], error))
            case_result = "fail"
            raise error

        finally:
            # 最后执行用例回写操作
            row = case_data['case_id'] + 1
            self.excel.excel_write(name=sheet_name, row=row, column=len(case_data), value=case_result)
            self.excel.excel_write(name=sheet_name, row=row, column=len(case_data) - 1, value=str(response.json()))
            logger.info("Write the response and result: %s " % case_result)


if __name__ == '__main__':
    unittest.main()
