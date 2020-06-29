#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-06-10 23:23
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : test_01_register.py
# @Software: PyCharm
import unittest
import ddt
import json
import random

from common.excel_handler import ExcelHandler
from middlerware.handler import Handler
from common.http_handler import visit

logger = Handler.logger
yaml = Handler.yaml
excel = Handler.excel
sheet_name = yaml['excel']['registersheet']
test_data = excel.get_data(sheet_name)


@ddt.ddt
class TestUserRegister(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info('------------------------------UserRegisterBegin------------------------------')
        cls.db = Handler.database_cls()
        logger.info('SQL connect')
        cls.excel = ExcelHandler(Handler.excel_path)

    @ddt.data(*test_data)
    def test01_user_register(self, case_data):
        """用户注册接口测试"""
        global case_result
        logger.info('**********正在获取第%d条<%s>用例**********' % (case_data['case_id'], case_data['title']))

        if "#phone#" in case_data['data']:
            new_phone = Handler().random_phone()
            case_data['data'] = case_data['data'].replace('#phone#', new_phone)

        # 重复注册用例的数据标识
        elif "*phone*" in case_data['data']:
            logger.info("重复注册用例,从数据库中随机读取一条mobile_phone用于注册")
            logger.info("正在查询数据库")
            # 从数据库随机提取一个号码用于已注册的用例
            sql_phone = self.db.query(
                sql="select * from futureloan.member LIMIT 20;", one=False)
            sql_data = random.randint(0, len(sql_phone))
            case_data['data'] = case_data['data'].replace("*phone*", str(sql_phone[sql_data]['mobile_phone']))

        reg_phone = json.loads(case_data['data'])
        response = visit(
            url=case_data['url'],
            method=case_data['method'],
            json=reg_phone,
            headers=json.loads(case_data['headers'])
        )
        expected = json.loads(case_data["expected"])

        try:
            for key, value in expected.items():
                self.assertTrue(response.json()[key] == value)
            if expected['code'] == 0:
                sql_code = "select * from futureloan.member where mobile_phone= {}".format(reg_phone['mobile_phone'])
                register_suc = self.db.query(sql=sql_code)
                self.assertTrue(register_suc)
                logger.info("查询数据库,确认数据库有该条注册信息")
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
    def tearDownClass(cls):
        logger.info('SQL connect close')
        cls.db.close()
        logger.info('------------------------------UserRegisterOver------------------------------')


if __name__ == '__main__':
    unittest.main()
