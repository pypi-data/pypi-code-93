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
from sc_analyzer_base import BranchUtils, ManifestUtils

from sc_retail_analysis.analyzer.base_analyzer import BaseAnalyzer


class HuNanClientAnalyzer(BaseAnalyzer):
    """
    湘籍客户分析
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter):
        super().__init__(config=config, excel_writer=excel_writer)
        self._key_enabled = "retail.hn_client.enabled"
        self._key_business_type = "retail.hn_client.business_type"

    def _read_config(self, *, config: ConfigManager):
        # 生成的Excel中湘籍客户数的列名
        self._target_hn_client_column_name = config.get("retail.hn_client.target_hn_client_column_name")
        # 生成的Excel中机构列的列名
        self._target_branch_column_name = config.get("retail.hn_client.target_branch_column_name")
        # 湘籍客户身份证前缀
        self._hn_client_id_prefix = config.get("retail.hn_client.hn_client_id_prefix")
        # 湘籍客户文件路径
        self._personal_src_filepath = config.get("retail.hn_client.personal.source_file_path")
        # 表头行索引
        self._personal_header_row = config.get("retail.hn_client.personal.sheet_config.header_row")
        # 二级分支机构列索引
        self._personal_branch_column = config.get("retail.hn_client.personal.sheet_config.branch_column")
        # 客户姓名列索引
        self._personal_name_column = config.get("retail.hn_client.personal.sheet_config.name_column")
        # 客户身份证号码列索引
        self._personal_client_id_column = config.get("retail.hn_client.personal.sheet_config.client_id_column")

        # 湘籍企业客户清单文件路径
        self._corporate_src_filepath = config.get("retail.hn_client.corporate.source_file_path")
        # Sheet名称
        self._corporate_sheet_name = config.get("retail.hn_client.corporate.sheet_name")
        # 表头行索引
        self._corporate_header_row = config.get("retail.hn_client.corporate.sheet_config.header_row")
        # 户数列索引
        self._corporate_total_client_column = config.get("retail.hn_client.corporate.sheet_config.total_client_column")
        # 其中湘籍客户数列索引
        self._corporate_hn_client_column = config.get("retail.hn_client.corporate.sheet_config.hn_client_column")
        # 归属支行/团队列索引
        self._corporate_attribute_branch_column = config.get(
            "retail.hn_client.corporate.sheet_config.attribute_branch_column")
        # 上门网点列索引
        self._corporate_service_branch_column = config.get(
            "retail.hn_client.corporate.sheet_config.service_branch_column")
        # 是否湘籍客户列索引
        self._corporate_is_hn_client_column = config.get("retail.hn_client.corporate.sheet_config.is_hn_client_column")

    def _replace_illegal_client_name(self):
        """
        替换不符合csv语法的客户姓名
        :return:
        """
        filename = self._personal_src_filepath
        with open(filename, 'r', encoding='utf-8') as inp:
            content = inp.read()

        content = content.replace("LEE JUN JIE,LEROY", "LEE JUN JIE;LEROY")
        with open(filename, 'w', encoding='utf-8') as outp:
            outp.write(content)

    def _read_src_file(self) -> pd.DataFrame:
        logging.getLogger(__name__).info("读取湘籍个人客户源文件：{}".format(self._personal_src_filepath))

        self._replace_illegal_client_name()

        self._personal_data = pd.read_csv(self._personal_src_filepath, header=self._personal_header_row)
        self._personal_branch_column_name = self._personal_data.columns[self._personal_branch_column]
        self._personal_name_column_name = self._personal_data.columns[self._personal_name_column]
        self._personal_client_id_column_name = self._personal_data.columns[self._personal_client_id_column]

        logging.getLogger(__name__).info("读取湘籍企业客户源文件：{}".format(self._corporate_src_filepath))
        self._corporate_data = pd.read_excel(
            self._corporate_src_filepath,
            sheet_name=self._corporate_sheet_name,
            header=self._corporate_header_row
        )
        self._corporate_total_client_column_name = self._corporate_data.columns[self._corporate_total_client_column]
        self._corporate_hn_client_column_name = self._corporate_data.columns[self._corporate_hn_client_column]
        self._corporate_attribute_branch_column_name = self._corporate_data.columns[
            self._corporate_attribute_branch_column]
        self._corporate_service_branch_column_name = self._corporate_data.columns[self._corporate_service_branch_column]
        self._corporate_is_hn_client_column_name = self._corporate_data.columns[self._corporate_is_hn_client_column]
        return self._personal_data

    def _pre_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # 过滤身份证为湖南的客户
        criterion = data[self._personal_client_id_column_name].map(lambda x: x.startswith(self._hn_client_id_prefix))
        data = data[criterion].copy()

        mapping = BranchUtils.get_branch_name_mapping()
        # 替换机构名称
        data = data.replace({self._personal_branch_column_name: mapping})
        # 替换机构名称
        self._corporate_data = self._corporate_data.replace({self._corporate_attribute_branch_column_name: mapping})
        # 替换机构名称
        self._corporate_data = self._corporate_data.replace({self._corporate_service_branch_column_name: mapping})
        return data

    def _pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("按 {} 透视数据项：{}".format(
            self._personal_branch_column_name,
            self._personal_name_column_name,
        ))
        # 对湘籍个人客户数进行统计
        table = pd.pivot_table(
            data,
            values=[self._personal_name_column_name],
            index=[self._personal_branch_column_name],
            aggfunc='count', fill_value=0
        )
        return table

    def _after_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data = data.reset_index()
        # 重命名列名
        data = data.rename(columns={
            self._personal_branch_column_name: self._target_branch_column_name,
            self._personal_name_column_name: self._target_hn_client_column_name,
        })
        for branch_name in BranchUtils.get_all_business_branch_list():
            if branch_name not in data[self._target_branch_column_name].values.tolist():
                data = data.append({
                    self._target_branch_column_name: branch_name,
                    self._target_hn_client_column_name: 0,
                }, ignore_index=True)
        # 筛选是湘籍企业的数据
        criterion = self._corporate_data[self._corporate_is_hn_client_column_name].map(lambda x: x == "是")
        hn_corporate_data = self._corporate_data[criterion].copy()

        # 加入湘籍企业客户的数量
        for row_i, row in hn_corporate_data.iterrows():
            total_client = row[self._corporate_total_client_column_name]
            hn_client = row[self._corporate_hn_client_column_name]
            attribute_branch = row[self._corporate_attribute_branch_column_name]
            service_branch = row[self._corporate_service_branch_column_name]
            if attribute_branch == service_branch:
                # 如果归属机构与上门机构相同，则全部归属到上门机构
                count = data.loc[
                    data[self._target_branch_column_name] == attribute_branch,
                    self._target_hn_client_column_name
                ]
                count = count + total_client - hn_client
                data.loc[
                    data[self._target_branch_column_name] == attribute_branch,
                    self._target_hn_client_column_name
                ] = count
            else:
                # 如果归属机构与上门机构相同，则全部归属到上门机构
                count_attribute = data.loc[
                    data[self._target_branch_column_name] == attribute_branch,
                    self._target_hn_client_column_name
                ]
                count_attribute = count_attribute + total_client
                data.loc[
                    data[self._target_branch_column_name] == attribute_branch,
                    self._target_hn_client_column_name
                ] = count_attribute
                count_service = data.loc[
                    data[self._target_branch_column_name] == service_branch,
                    self._target_hn_client_column_name
                ]
                count_service = count_service - hn_client
                data.loc[
                    data[self._target_branch_column_name] == service_branch,
                    self._target_hn_client_column_name
                ] = count_service
        return data

    def _merge_with_manifest(self, *, manifest_data: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("与机构清单合并...")
        merge_result = manifest_data.merge(
            data,
            how="left",
            left_on=[ManifestUtils.get_branch_column_name()],
            right_on=[self._target_branch_column_name],
        )
        return merge_result

    def write_origin_data(self):
        # 机构汇总不输出明细数据
        pass

    def _merge_with_previous_result(self, data: pd.DataFrame, previous_data: pd.DataFrame) -> pd.DataFrame:
        if previous_data is None or previous_data.empty:
            return data
        result = previous_data.copy()
        # 在原有基础上增加湘籍客户一列
        result[self._target_hn_client_column_name] = data[self._target_hn_client_column_name]
        return result
