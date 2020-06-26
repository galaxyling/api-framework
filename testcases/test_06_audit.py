#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-06-20 16:15
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : test_06_audit.py
# @Software: PyCharm
import json
import unittest
import ddt

from common.excel_handler import ExcelHandler
from common.http_handler import visit
from middlerware.handler import Handler

logger = Handler.logger
excel = Handler.excel
yaml = Handler.yaml
sheet_name = yaml['excel']['auditsheet']
test_data = excel.get_data(sheet_name)


@ddt.ddt
class TestAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logger.info('------------------------------TestAuditBegin------------------------------')
        cls.admin_token = Handler().admin_token
        cls.token = Handler().token

    def setUp(self) -> None:
        # 封装使用测试号生成的项目,并提取loan_id
        self.loan_id = Handler().loan_id
        self.db = Handler.database_cls()
        self.excel = ExcelHandler(Handler.excel_path)

    @ddt.data(*test_data)
    def test01_audit(self, case_data):
        """审核项目接口测试"""
        global case_result
        logger.info('**********正在获取第%d条<%s>用例**********' % (case_data['case_id'], case_data['title']))
        headers = case_data['headers']
        # 增加一个用户登陆登陆进行审核的失败操作用例
        if ("#admin_token#" in headers) or ("#token#" in headers):
            headers = headers.replace("#admin_token#", self.admin_token)
            headers = headers.replace("#token#", self.token)

        data = case_data['data']
        if "#loan_id#" in data:
            data = data.replace("#loan_id#", str(self.loan_id))

        # 取一个不存在的项目id
        if "#fail_loan_id#" in data:
            data = data.replace("#fail_loan_id#", str(self.loan_id + 1000))

        # 判断是否为已审批的用例,若为已审批的账号则从数据库提取一条status != 1的数据
        if "#approve_loan_id#" in data:
            self.loan_id = self.db.query("select * from futureloan.loan where `status` !=2 limit 1;")['id']
            data = data.replace("#approve_loan_id#", str(self.loan_id))

        response = visit(
            url=yaml['host'] + case_data['url'],
            method=case_data['method'],
            json=json.loads(data),
            headers=json.loads(headers)
        )
        expected = json.loads(case_data["expected"])

        try:
            self.assertEqual(response.json()["code"], expected['code'])
            if response.json()['code'] == 0:
                sql = "select `status` from futureloan.loan where id = {};".format(self.loan_id)
                after_state = self.db.query(sql)['status']
                self.assertEqual(expected['status'], after_state)
            logger.info('**********第%d条<%s>用例测试结束**********' % (case_data['case_id'], case_data['title']))
            case_result = "pass"

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

    def tearDown(self) -> None:
        self.db.close()

    @classmethod
    def tearDownClass(cls) -> None:
        logger.info('------------------------------TestAuditOver------------------------------')


if __name__ == '__main__':
    unittest.main()
