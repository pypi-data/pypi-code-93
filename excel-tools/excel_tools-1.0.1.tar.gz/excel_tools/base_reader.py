# -*- coding: utf-8 -*-
import warnings
from typing import Optional, Union


class ExcelBaseObject(object):
    def __init__(self, name: str, path: Optional[str] = ''):
        self._name = name
        self._path = path

        self._xl = None
        self._sheet = None

    def get_rows(self):
        """ 获取所有列的单元格 """

    def get_row(self, rowx: int):
        """
        获取对应行的所有单元格

        Args:
            rowx: 行数

        Returns:
            返回这一行所有单元格
        """

    def get_row_len(self, rowx: int):
        """
        获取对应行有效单元格的数量

        Args:
            rowx: 行数

        Returns:
            有效单元格数量
        """

    def get_row_value(self, rowx: int, start_colx: Optional[int] = 0, end_colx: int = None):
        """
        获取表格内对应行中的所有单元格的数据

        Args:
            rowx: 行数
            start_colx: 左切片列数
            end_colx: 右切片列数

        Returns:
            返回这一行所有数据组成的列表
        """

    def get_colx(self):
        """ 获取所有行的单元格 """

    def get_col(self, colx: int):
        """ 获取对应列的所有单元格 """

    def get_col_value(self, colx: int, start_rowx: Optional[int] = 0, end_rowx: Optional[int] = None):
        """
        获取表格内对应列中的所有单元格的数据

        Args:
            colx: 行数
            start_rowx: 左切片行数
            end_rowx: 右切片行数

        Returns:
            返回这一列所有数据组成的列表
        """

    def get_cell(self, rowx, colx):
        """
        获取单元格

        Args:
            rowx: 列数
            colx: 行数

        Returns:
            行列对应单元格
        """

    def get_cell_value(self, rowx, colx):
        """
        获取单元格内数据

        Args:
            rowx: 列数
            colx: 行数

        Returns:
            行列对应单元格中的数据
        """