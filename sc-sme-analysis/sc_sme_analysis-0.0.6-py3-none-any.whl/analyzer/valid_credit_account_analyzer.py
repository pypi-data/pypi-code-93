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

import pandas as pd
from config42 import ConfigManager
from sc_analyzer_base import BaseAnalyzer, ManifestUtils


class ValidCreditAccountAnalyzer(BaseAnalyzer):
    """
    有效授信户分析
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter):
        super().__init__(config=config, excel_writer=excel_writer)
        self._key_enabled = "sme.valid_credit_account.enabled"
        self._key_business_type = "sme.valid_credit_account.business_type"
        self._key_export_column_list = "sme.valid_credit_account.sheet_config.export_column_list"

    def _read_config(self, *, config: ConfigManager):
        # 财富客户数统计文件路径
        self._src_filepath = config.get("sme.valid_credit_account.source_file_path")
        # Sheet名称
        self._sheet_name = config.get("sme.valid_credit_account.sheet_name")
        # 表头行索引
        self._header_row = config.get("sme.valid_credit_account.sheet_config.header_row")
        # 客户经理列索引
        self._manager_name_column = config.get("sme.valid_credit_account.sheet_config.manager_name_column")
        # 客户名称列索引
        self._client_name_column = config.get(
            "sme.valid_credit_account.sheet_config.client_name_column")
        # 生成的Excel中有效授信客户名称的列名
        self._target_client_name_column_name = config.get(
            "sme.valid_credit_account.sheet_config.target_client_name_column_name")
        # 生成的Excel中有效授信户数量的列名
        self._target_client_count_column_name = config.get(
            "sme.valid_credit_account.sheet_config.target_client_count_column_name")

    def _read_src_file(self) -> pd.DataFrame:
        logging.getLogger(__name__).info("读取源文件：{}".format(self._src_filepath))
        df = pd.read_csv(self._src_filepath, header=self._header_row)
        self._manager_name_column_name = df.columns[self._manager_name_column]
        self._client_name_column_name = df.columns[self._client_name_column]
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
        data = data.rename(columns={
            self._client_name_column_name: self._target_client_name_column_name,
        })
        return data

    def _pre_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # 选择客户经理和客户姓名两列
        data = data[[self._manager_name_column_name, self._target_client_name_column_name]]
        # 去除重复项
        data = data.drop_duplicates()
        # 添加有效授信客户数量
        data[self._target_client_count_column_name] = 1
        return data

    def _merge_with_manifest(self, *, manifest_data: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("与机构清单合并...")
        merge_result = manifest_data.merge(
            data,
            how="left",
            left_on=[ManifestUtils.get_name_column_name()],
            right_on=[self._manager_name_column_name],
        )
        # 空的客户名称置空
        merge_result[self._target_client_name_column_name].fillna("", inplace=True)
        # 空的客户数量置0
        merge_result[self._target_client_count_column_name].fillna(0, inplace=True)
        return merge_result

    def _drop_duplicated_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        return data.drop(columns=[self._manager_name_column_name])

    def _add_target_columns(self) -> None:
        self._add_target_column(self._target_client_count_column_name)

    def _summarize(self, data: pd.DataFrame) -> pd.DataFrame:
        if self._target_client_count_column_name not in data.columns:
            return data
        # 按客户经理计数客户数（去重后的）
        group_by_manager = data.groupby(
            by=ManifestUtils.get_name_column_name()
        )[self._target_client_count_column_name].sum().to_dict()
        # 添加按客户经理计数列（列名为配置项）
        data[self._target_client_count_column_name] = data[ManifestUtils.get_name_column_name()].map(group_by_manager)

        data = data.drop(columns=[self._target_client_name_column_name])
        # 去除重复项
        data = data.drop_duplicates()
        return data
