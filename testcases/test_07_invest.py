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
from middlerware.handler import Handler
from common.http_handler import visit

yaml = Handler.yaml
excel = Handler.excel
logger = Handler.logger
sheet_name = yaml['excel']['investsheet']
test_data = excel.get_data(sheet_name)


@ddt.ddt
class TestInvest(unittest.TestCase):
    # @classmethod
    # def setUpClass(cls) -> None:
    #     cls.token = Handler.token
    #     cls.member_id = Handler.member_id
    def setUp(self) -> None:
        self.db = Handler.database_cls()
        # 判断投资用户的金额是否充足,若小于20W则调用充值接口
        self.amount_sql = "select leave_amount from futureloan.member where id = {}".format(Handler().member_id)
        self.before_money = self.db.query(self.amount_sql)['leave_amount']

    def tearDown(self) -> None:
        self.db.close()

    @ddt.data(*test_data)
    def test_01_invest(self, case_data):
        """投资接口测试"""
        # 调用正则表达式,替换数据中所有的以##表示的动态数据,并进行替换对应的属性
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

        response = visit(
            url=yaml['host'] + case_data['url'],
            method=case_data['method'],
            json=json.loads(case_data['data']),
            headers=json.loads(case_data['headers'])
        )

        expected = json.loads(case_data['expected'])
        data = json.loads(case_data['data'])

        try:
            self.assertEqual(response.json()["code"], expected["code"])
            if response.json()["code"] == 0:
                sql = "select `status` from futureloan.loan where id={}".format(data["loan_id"])
                after_status = self.db.query(sql)['status']
                # 投资成功用例,查看数据库对应项目状态是否发生改变
                self.assertEqual(expected["status"], after_status)
                # 充值成功的用例,查询投资账户金额是否响应减少
                self.invest_after_money = self.db.query(self.amount_sql)['leave_amount']
                self.assertTrue(self.before_money - Decimal(str(data['amount'])) == self.invest_after_money)

        except AssertionError as error:
            raise error
