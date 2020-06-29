#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-06-13 00:37
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : mysql_handler.py
# @Software: PyCharm
import random
import pymysql
from pymysql.cursors import DictCursor


class MysqlHandler:
    def __init__(self,
                 host=None,
                 port=3306,
                 user=None,
                 password=None,
                 charset=None,
                 cursorclass=DictCursor
                 ):
        """初始化数据库连接对象"""
        self.conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset=charset,
            cursorclass=cursorclass
        )
        # 初始化游标对象
        self.cursor = self.conn.cursor()

    def query(self, sql, one=True):
        """
        表查询方法
        :param sql: 传入sql查询语句
        :param one: 默认查询一条,若需要查询多条传入 one=False
        :return: 根据返回数量,返回查询的结果
        """
        # commit把数据进行更新(提交事务,类似刷新表单)
        self.conn.commit()
        self.cursor.execute(sql)

        # 是否返回多条数据
        if one:
            # self.close()
            return self.cursor.fetchone()
        # self.close()
        return self.cursor.fetchall()

    def close(self):
        """关闭游标以及数据库连接"""
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    conn = MysqlHandler(
        host='120.78.128.25',
        port=3306,
        user='future',
        password='123456',
        charset='utf8',
        cursorclass=DictCursor
    )
    test = conn.query(sql='select * from futureloan.member  LIMIT 10;', one=False)
    test1 = random.randint(0, len(test))
    print(test[test1])
