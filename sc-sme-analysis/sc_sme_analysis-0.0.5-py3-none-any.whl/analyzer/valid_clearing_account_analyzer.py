#  The MIT License (MIT)
#
#  Copyright (c) 2021. Scott Lau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import logging

import numpy as np
import pandas as pd
from config42 import ConfigManager
from sc_analyzer_base import BaseAnalyzer, ManifestUtils, BranchUtils


class ValidClearingAccountAnalyzer(BaseAnalyzer):
    """
    有效结算户分析
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter):
        super().__init__(config=config, excel_writer=excel_writer)
        self._key_enabled = "sme.valid_clearing_account.enabled"
        self._key_business_type = "sme.valid_clearing_account.business_type"
        self._key_export_column_list = "sme.valid_clearing_account.sheet_config.export_column_list"

    def _read_config(self, *, config: ConfigManager):
        # 有效结算户文件路径
        self._src_filepath = config.get("sme.valid_clearing_account.source_file_path")
        # 管理机构筛选广州分行
        manage_branch_filter_list: list = config.get("sme.valid_clearing_account.manage_branch_filter_list")
        self._manage_branch_filter_list: list = list()
        if manage_branch_filter_list is not None and type(manage_branch_filter_list) == list:
            self._manage_branch_filter_list.extend(manage_branch_filter_list)
        # Sheet名称
        self._sheet_name = config.get("sme.valid_clearing_account.sheet_name")
        # Sheet名称
        self._account_valid_daily_balance_threshold = config.get(
            "sme.valid_clearing_account.account_valid_daily_balance_threshold")
        # 表头行索引
        self._header_row = config.get("sme.valid_clearing_account.sheet_config.header_row")
        # 机构名称列索引
        self._branch_column = config.get("sme.valid_clearing_account.sheet_config.branch_column")
        # 账户名称列索引
        self._account_name_column = config.get(
            "sme.valid_clearing_account.sheet_config.account_name_column")
        # 累计日均数列索引
        self._accumulated_daily_balance_column = config.get(
            "sme.valid_clearing_account.sheet_config.accumulated_daily_balance_column")
        # 上级机构列索引
        self._manage_branch_column = config.get(
            "sme.valid_clearing_account.sheet_config.manage_branch_column")
        # 生成的Excel中是否有效结算户的列名
        self._target_is_valid_clearing_account_column_name = config.get(
            "sme.valid_clearing_account.sheet_config.target_is_valid_clearing_account_column_name")
        # 生成的Excel中所在部门的列名
        self._target_branch_column_name = config.get(
            "sme.valid_clearing_account.sheet_config.target_branch_column_name")
        # 默认机构的名称
        self._default_branch_value = config.get("sme.valid_clearing_account.default_branch_value")

    def _read_src_file(self) -> pd.DataFrame:
        logging.getLogger(__name__).info("读取源文件：{}".format(self._src_filepath))
        data = pd.read_excel(self._src_filepath, sheet_name=self._sheet_name, header=self._header_row)
        self._selected_columns: list = list()
        self._branch_column_name = data.columns[self._branch_column]
        self._selected_columns.append(self._branch_column_name)
        self._account_name_column_name = data.columns[self._account_name_column]
        self._selected_columns.append(self._account_name_column_name)
        self._accumulated_daily_balance_column_name = data.columns[self._accumulated_daily_balance_column]
        self._selected_columns.append(self._accumulated_daily_balance_column_name)
        self._manage_branch_column_name = data.columns[self._manage_branch_column]
        self._selected_columns.append(self._manage_branch_column_name)
        return data

    def _add_export_column_manifest_branch(self, origin_data: pd.DataFrame):
        if origin_data is None or origin_data.empty:
            return origin_data
        # 原始报表与花名册整合，添加花名册所在部门一列
        data = origin_data.merge(
            ManifestUtils.get_name_branch_data_frame(),
            how="left",
            left_on=[self._branch_column_name],
            right_on=[ManifestUtils.get_name_column_name()]
        )
        # 替换机构名称
        mapping = BranchUtils.get_branch_name_mapping()
        data[ManifestUtils.get_manifest_branch_column_name()] = data[self._branch_column_name]
        data = data.replace({ManifestUtils.get_manifest_branch_column_name(): mapping})
        return data

    def _pre_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # 筛选相关的列
        data = data[self._selected_columns].copy()
        # 筛选上级机构满足条件的
        criterion = data[self._manage_branch_column_name].map(lambda x: x in self._manage_branch_filter_list)
        data = data[criterion].copy()

        # 替换机构名称
        mapping = BranchUtils.get_branch_name_mapping()
        data = data.replace({self._branch_column_name: mapping})
        # 添加所在部门列
        data[self._target_branch_column_name] = self._default_branch_value
        return data

    def _pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        index_columns = [self._target_branch_column_name, self._account_name_column_name]
        value_columns = [self._accumulated_daily_balance_column_name]
        if data.empty:
            return pd.DataFrame(columns=index_columns + value_columns)
        table = pd.pivot_table(data, values=value_columns,
                               index=index_columns,
                               aggfunc=np.sum, fill_value=0)
        return table

    def _is_valid_clearing_account(self, balance):
        """
        是不是有效结算户
        :return : 如果大于或等于相应的阈值，则返回1，否则返回0
        """
        try:
            return 1 if float(balance) >= self._account_valid_daily_balance_threshold else 0
        except Exception:
            return 0

    def _after_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # 添加生成的Excel中是否有效结算户的列名
        data[self._target_is_valid_clearing_account_column_name] = data.apply(
            lambda x: self._is_valid_clearing_account(x),
            axis=1,
        )
        return data.reset_index()

    def _merge_with_previous_result(self, data: pd.DataFrame, previous_data: pd.DataFrame) -> pd.DataFrame:
        # 无客户经理，直接返回上一次的分析数据
        return previous_data
