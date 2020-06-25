#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-06-20 14:38
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : test_05_add.py
# @Software: PyCharm

import unittest
import ddt
import json

from middlerware.handler import Handler
from common.http_handler import visit
from common.excel_handler import ExcelHandler

logger = Handler.logger
yaml = Handler.yaml
sheet_name = yaml['excel']['addsheet']
test_data = Handler.excel.get_data(sheet_name)


@ddt.ddt
class TestAdd(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logger.info('**********TestAddBegin**********')
        # 获取用户token以及member_id
        cls.token = Handler().token
        cls.member_id = Handler().member_id

    def setUp(self) -> None:
        self.sql = "select count(*) from futureloan.loan where member_id={};".format(self.member_id)
        self.db = Handler.database_cls()
        self.before_add = self.db.query(self.sql)['count(*)']
        logger.info("sql connect,建立项目前,数据库的项目数量为{} ".format(self.before_add))
        self.excel = ExcelHandler(Handler.excel_path)

    @ddt.data(*test_data)
    def test01_add(self, case_data):
        """添加项目接口测试"""
        global case_result
        logger.info('**********正在获取第%d条<%s>用例**********' % (case_data['case_id'], case_data['title']))
        data = case_data['data']
        headers = case_data['headers']
        if ("#member_id#" in data) or ("#token#" in headers):
            data = data.replace("#member_id#", str(self.member_id))
            headers = headers.replace("#token#", self.token)

        response = visit(
            url=yaml['host'] + case_data['url'],
            method=case_data['method'],
            json=json.loads(data),
            headers=json.loads(headers)
        )

        expected = json.loads(case_data['expected'])
        try:
            for key, value in expected.items():
                self.assertEqual(response.json()[key], value)
            if response.json()['code'] == 0:
                # 如果是创建成功的用例,则进一步查询数据库数量是否增加1条
                self.after_add = self.db.query(sql=self.sql)['count(*)']
                logger.info("建立项目后,数据库的项目数量为{} ".format(self.after_add))
                self.assertTrue(self.before_add + 1 == self.after_add)
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

    def tearDown(self) -> None:
        logger.info("sql disconnect")
        self.db.close()

    @classmethod
    def tearDownClass(cls) -> None:
        logger.info('**********TestAddOver**********')


if __name__ == '__main__':
    unittest.main()
