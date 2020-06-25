#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020-05-30 15:08
# @Author  : 小凌
# @Email   : 296054210@qq.com
# @File    : excel_handler.py
# @Software: PyCharm

import openpyxl
import os
import filePath


class ExcelHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.workbook = self.open_excel()

    def open_excel(self):
        """打开excel文件,获取workbook对象"""
        workbook = openpyxl.load_workbook(self.file_path)
        return workbook

    def get_sheet(self, name):
        """获取sheet页"""
        sheet_data = self.workbook[name]

        return sheet_data

    def get_data(self, name):
        """获取测试用例数据,并以列表嵌套字典格式返回"""
        rows = list(self.get_sheet(name))
        case_list = []

        # 获取标题栏
        title = []
        for row in rows[0]:
            title.append(row.value)

        # 获取数据,并将标题为key:数据的字典返回,添加case_list列表中
        for cell in rows[1:]:
            case_dict = {}
            for num, data in enumerate(cell):
                case_dict[title[num]] = data.value
            case_list.append(case_dict)
        self.excel_close()

        return case_list

    def excel_write(self, name, row, column, value):
        sheet_value = self.get_sheet(name)
        sheet_value.cell(row=row, column=column).value = value
        # 修改后需要保存关闭
        self.excel_save()
        self.excel_close()

    def excel_save(self):
        self.workbook.save(self.file_path)

    def excel_close(self):
        self.workbook.close()


if __name__ == '__main__':
    case = os.path.join(filePath.DATA_PATH, 'qcd_case.xlsx')

    test = ExcelHandler(case)
    print(test.get_data('registered'))
    sheet = test.get_data('registered')
    # test.excel_write(
    #     name='registered',
    #     row=2,
    #     column=9,
    #     value='pass'
    # )
