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
from sc_analyzer_base import BaseAnalyzer, ManifestUtils


class InclusiveFinanceBalanceAnalyzer(BaseAnalyzer):
    """
    普惠贷款余额分析
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter):
        super().__init__(config=config, excel_writer=excel_writer)
        self._key_enabled = "sme.inclusive_finance_balance.enabled"
        self._key_business_type = "sme.inclusive_finance_balance.business_type"
        self._key_export_column_list = "sme.inclusive_finance_balance.sheet_config.export_column_list"

    def _read_config(self, *, config: ConfigManager):
        # 文件路径
        self._src_filepath = config.get("sme.inclusive_finance_balance.source_file_path")
        # 管理机构筛选广州分行
        manage_branch_filter_list: list = config.get("sme.inclusive_finance_balance.manage_branch_filter_list")
        self._manage_branch_filter_list: list = list()
        if manage_branch_filter_list is not None and type(manage_branch_filter_list) == list:
            self._manage_branch_filter_list.extend(manage_branch_filter_list)
        # Sheet名称
        self._sheet_name = config.get("sme.inclusive_finance_balance.sheet_name")
        # 表头行索引
        self._header_row = config.get("sme.inclusive_finance_balance.sheet_config.header_row")
        # 客户经理列索引
        self._manager_name_column = config.get("sme.inclusive_finance_balance.sheet_config.manager_name_column")
        # 客户名称列索引
        self._client_name_column = config.get("sme.inclusive_finance_balance.sheet_config.client_name_column")
        # 贷款余额（折人民币）列索引
        self._loan_balance_column = config.get("sme.inclusive_finance_balance.sheet_config.loan_balance_column")
        # 考核口径普惠贷款列索引
        self._is_inclusive_finance_column = config.get(
            "sme.inclusive_finance_balance.sheet_config.is_inclusive_finance_column")
        # 管理机构列索引
        self._manage_branch_column = config.get("sme.inclusive_finance_balance.sheet_config.manage_branch_column")
        # 生成的Excel中普惠贷款余额的列名
        self._target_inclusive_finance_balance_column_name = config.get(
            "sme.inclusive_finance_balance.sheet_config.target_inclusive_finance_balance_column_name")
        # 生成的Excel中客户名称的列名
        self._target_client_name_column_name = config.get(
            "sme.inclusive_finance_balance.sheet_config.target_client_name_column_name")

    def _read_src_file(self) -> pd.DataFrame:
        logging.getLogger(__name__).info("读取源文件：{}".format(self._src_filepath))
        df = pd.read_csv(self._src_filepath, header=self._header_row)
        self._selected_columns: list = list()
        self._manager_name_column_name = df.columns[self._manager_name_column]
        self._selected_columns.append(self._manager_name_column_name)
        self._client_name_column_name = df.columns[self._client_name_column]
        self._selected_columns.append(self._client_name_column_name)
        # 后面会重命名列名，这里添加重命名后的列名
        self._loan_balance_column_name = df.columns[self._loan_balance_column]
        self._selected_columns.append(self._target_inclusive_finance_balance_column_name)
        self._is_inclusive_finance_column_name = df.columns[self._is_inclusive_finance_column]
        self._selected_columns.append(self._is_inclusive_finance_column_name)
        self._manage_branch_column_name = df.columns[self._manage_branch_column]
        self._selected_columns.append(self._manage_branch_column_name)
        return df

    def _add_export_column_manifest_branch(self, origin_data: pd.DataFrame):
        if origin_data is None or origin_data.empty:
            return origin_data
        # 原始报表与花名册整合，添加花名册所在部门一列
        data = origin_data.merge(
            ManifestUtils.get_name_branch_data_frame(),
            how="left",
            left_on=[self._manager_name_column_name],
            right_on=[ManifestUtils.get_name_column_name()]
        )
        return data

    def _rename_target_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        df = data.rename(columns={
            self._loan_balance_column_name: self._target_inclusive_finance_balance_column_name,
        })
        return df

    def _pre_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # 筛选相关的列
        data = data[self._selected_columns].copy()
        # 筛选管理机构
        criterion = data[self._manage_branch_column_name].map(lambda x: x in self._manage_branch_filter_list)
        data = data[criterion].copy()
        # 筛选普惠金融
        criterion = data[self._is_inclusive_finance_column_name].map(lambda x: x == '是')
        data = data[criterion].copy()
        return data

    def _pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        index_columns = [self._manager_name_column_name, self._client_name_column_name]
        value_columns = [self._target_inclusive_finance_balance_column_name]
        if data.empty:
            return pd.DataFrame(columns=index_columns + value_columns)
        table = pd.pivot_table(data, values=value_columns,
                               index=index_columns,
                               aggfunc=np.sum, fill_value=0)
        return table

    def _after_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        return data.reset_index()

    def _merge_with_manifest(self, *, manifest_data: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("与机构清单合并...")
        merge_result = manifest_data.merge(
            data,
            how="left",
            left_on=[ManifestUtils.get_name_column_name()],
            right_on=[self._manager_name_column_name],
        )
        return merge_result

    def _drop_duplicated_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        return data.drop(columns=[self._manager_name_column_name])

    def _summarize(self, data: pd.DataFrame) -> pd.DataFrame:
        group_by_manager = data.groupby(
            by=ManifestUtils.get_name_column_name()
        )[self._target_inclusive_finance_balance_column_name].sum().to_dict()
        data[self._target_inclusive_finance_balance_column_name] = data[
            ManifestUtils.get_name_column_name()
        ].map(group_by_manager)
        data = data.drop(columns=[self._target_client_name_column_name])
        # 去除重复项
        data = data.drop_duplicates()
        return data

    def _merge_with_previous_result(self, data: pd.DataFrame, previous_data: pd.DataFrame) -> pd.DataFrame:
        data = previous_data.merge(
            data,
            how="left",
            on=[
                ManifestUtils.get_id_column_name(),
                ManifestUtils.get_name_column_name(),
                ManifestUtils.get_branch_column_name(),
                ManifestUtils.get_sales_performance_attribution_column_name(),
            ]
        )
        return data

    def _add_target_columns(self) -> None:
        self._add_target_column(self._target_inclusive_finance_balance_column_name)
