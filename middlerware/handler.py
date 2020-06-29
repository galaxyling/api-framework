#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-06-14 14:01
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : handler.py
# @Software: PyCharm
import random
import time
import jsonpath
import re

from pymysql.cursors import DictCursor

import filePath
import os
from common import yaml_handler, excel_handler, my_log
from common.mysql_handler import MysqlHandler
from common.http_handler import visit


class MysqlHandlerMidWare(MysqlHandler):
    def __init__(self):
        sql_conf = Handler.yaml['sql']
        # 重写
        super().__init__(
            host=sql_conf['host'],
            port=sql_conf['port'],
            user=sql_conf['user'],
            password=sql_conf['password'],
            charset=sql_conf['charset'],
            cursorclass=DictCursor
        )
        self.cursor = self.conn.cursor()


class Handler:
    """
    初始化所有数据;
    在其他模块中使用;
    是从common当中实例化对象;
    """
    # 加载文件路径配置项,其他文件只需导入此文件就可以使用file path配置了
    fPath = filePath

    # 加载yaml数据配置项
    __yaml_path = fPath.CONF_PATH
    yaml = yaml_handler.get_yaml_data(os.path.join(__yaml_path, 'conf.yaml'))

    # 加载Excel数据,生成ExcelHandler对象,赋值给excel属性
    __excel_path = fPath.DATA_PATH
    __excel_file = yaml['excel']['excelname']
    excel_path = os.path.join(__excel_path, __excel_file)
    excel = excel_handler.ExcelHandler(os.path.join(__excel_path, __excel_file))
    excel_write = excel_handler.ExcelHandler(excel_path)

    # 初始化log,初始化MyLog,并赋值给logger属性
    __log_name = yaml['log']['name']
    __log_level = yaml['log']['level']
    logger = my_log.MyLog(name=__log_name, level=__log_level)

    # 创建以时间为名称的文件夹,并将测试报告生成在里面
    __now = time.strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(os.path.join(fPath.REPORT_PATH, __now)):
        os.mkdir(os.path.join(fPath.REPORT_PATH, __now))
    file_name = filePath.REPORT_PATH + '/' + __now + '/' + yaml['report']['file']

    # 将数据库查询这个类(不是对象!),赋值给handler中的一个变量,用于方便管理.也可以不用添加
    database_cls = MysqlHandlerMidWare

    @staticmethod
    def random_phone():
        """随机获取一个不存在数据库的手机号码"""
        while True:
            start_num = ["137", "150", "136", "131"]

            phone = start_num[random.randint(0, len(start_num) - 1)]
            for i in range(0, 8):
                phone += str(random.randint(0, 9))

            watch_phone = Handler.database_cls().query(
                sql="select * from futureloan.member where mobile_phone= {}".format(phone)
            )
            if not watch_phone:
                return phone
            else:
                pass

    def recharge_cls(self):
        """充值接口"""
        response = visit(
            url=Handler.yaml['host'] + '/member/recharge',
            method='post',
            json={'member_id': self.member_id, 'amount': 500000},
            headers={'X-Lemonban-Media-Type': 'lemonban.v2', "Authorization": self.token}
        )
        return response.json()

    def withdraw(self):
        """
        取现接口
        :return: leave_mount
        """
        response = visit(
            url=self.yaml['host'] + "/member/withdraw",
            method='post',
            json={"member_id": self.member_id, "amount": 200000},
            headers={'X-Lemonban-Media-Type': 'lemonban.v2', "Authorization": self.token}
        )
        return jsonpath.jsonpath(response.json(), '$..leave_mount')

    def login(self, data):
        """登陆账号"""
        response = visit(
            url=self.yaml['host'] + '/member/login',
            method='post',
            json=data,
            headers={'X-Lemonban-Media-Type': 'lemonban.v2'}
        )
        token_type = jsonpath.jsonpath(response.json(), '$..token_type')[0]
        token_value = jsonpath.jsonpath(response.json(), '$..token')[0]
        token = ' '.join([token_type, token_value])
        member_id = jsonpath.jsonpath(response.json(), '$..id')[0]

        return {"token": token, "member_id": member_id}

    def add_loan(self):
        """
        使用测试账号调用添加项目接口获取loan_id
        :return: loan_id
        """
        data = {
            "member_id": self.member_id,
            "title": "凌的投资项目",
            "amount": 200000,
            "loan_rate": 12.0,
            "loan_term": 1,
            "loan_date_type": 1,
            "bidding_days": 5
        }
        response = visit(
            url=self.yaml['host'] + '/loan/add',
            method='post',
            json=data,
            headers={'X-Lemonban-Media-Type': 'lemonban.v2', "Authorization": self.token}
        )
        return response.json()

    def audit_loan(self):
        data = {
            "loan_id": self.loan_id,
            "approved_or_not": True
        }
        response = visit(
            url=self.yaml['host'] + '/loan/audit',
            method='patch',
            json=data,
            headers={'X-Lemonban-Media-Type': 'lemonban.v2', "Authorization": self.admin_token}
        )
        return data["loan_id"]

    @property
    def token(self):
        data = Handler().login(self.yaml['user'])
        return data['token']

    @property
    def member_id(self):
        data = Handler().login(self.yaml['user'])
        return data['member_id']

    @property
    def admin_token(self):
        data = Handler().login(self.yaml['admin_user'])
        return data['token']

    @property
    def loan_id(self):
        loan_id = jsonpath.jsonpath(self.add_loan(), "$..id")[0]
        return loan_id

    @property
    def pass_loan_id(self):
        """已经审批通过的项目loan_id"""
        return self.audit_loan()

    def replace_data(self, data):
        """使用正则查找用例数据中需要替换的动态数据,将其替换成mid中封装的属性"""
        pattern = r"#(.*?)#"
        while re.search(pattern, data):
            key = re.search(pattern, data).group(1)
            # value = getattr(self, key, "can't find attr")
            data = re.sub(pattern, str(getattr(self, key, "can't find attr")), data, count=1)
        return data


if __name__ == '__main__':
    # data_path = Handler.fPath.DATA_PATH
    #     # print(data_path)
    #     #
    #     # yaml = Handler.yaml
    #     # print(yaml['report']['title'])
    #     #
    #     # login_excel = Handler.excel.get_data('login')
    #     # print(login_excel)
    #     #
    #     # logger = Handler.logger
    #     # # logger.info('test')
    #     # print(logger)

    # test = MysqlHandlerMidWare().query(
    #     sql='select * from futureloan.member LIMIT 10;'
    # )
    # test2 = MysqlHandlerMidWare().query(
    #     sql='select leave_amount from futureloan.member where mobile_phone=15080382968;')
    # test2 = MysqlHandlerMidWare().query(
    #     sql='select count(*) from futureloan.loan where member_id=160246;')['count(*)']
    # # )
    # # print(test)
    # print(test2)
    # print(Handler().token)
    # print(Handler().member_id)
    # print(Handler().admin_token)
    # print(Handler().token)
    # print(Handler().member_id)
    # print(Handler().admin_token)
    # print(Handler().login(Handler.yaml['user']).json())
    # print(Handler.recharge_cls())
    # print(Handler().login(Handler.yaml['admin_user']).json())
    # print(Handler().admin_token)
    # print(Handler().login(Handler.yaml['admin_user']))

    # print(Handler().loan_id())
    # print(Handler().loan_id)

    # print(Handler().audit_loan())
    # test = Handler()
    # print(test.add_loan())
    # print(test.audit_loan())

    print(Handler().pass_loan_id)
