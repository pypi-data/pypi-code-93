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

import numpy as np
import pandas as pd
from config42 import ConfigManager

from sc_analyzer_base import BaseAnalyzer, ManifestUtils


class BranchSummaryAnalyzer(BaseAnalyzer):
    """
    按机构汇总分析
    """

    def __init__(
            self, *,
            config: ConfigManager,
            manager_summary: pd.DataFrame,
            target_column_list: list,
            excel_writer: pd.ExcelWriter
    ):
        super().__init__(config=config, excel_writer=excel_writer)
        self._manager_summary = manager_summary
        self._key_enabled = "sme.branch_summary.enabled"
        self._key_business_type = "sme.branch_summary.business_type"
        self._target_column_list = list()
        self._target_column_list.extend(target_column_list)

    def _enabled(self):
        """始终启用机构汇总分析"""
        return True

    def _read_config(self, *, config: ConfigManager):
        # 汇总配置
        self._business_type_summary_dict = dict()
        business_type_summary_dict = config.get("sme.branch_summary.business_type_summary")
        if business_type_summary_dict is not None and type(business_type_summary_dict) is dict:
            self._business_type_summary_dict.update(business_type_summary_dict)

    def _read_src_file(self) -> pd.DataFrame:
        return self._manager_summary

    def _pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        table = pd.pivot_table(
            data, values=self._target_column_list,
            index=[ManifestUtils.get_branch_column_name()],
            aggfunc=np.sum,
            fill_value=0,
            # 添加按列合计
            margins=True, margins_name="合计",
        )
        if len(self._target_column_list) > 0:
            # 添加小计
            real_key_list = list()
            for sum_key, column_list in self._business_type_summary_dict.items():
                real_column_list = list()
                for column in column_list:
                    if column in self._target_column_list:
                        real_column_list.append(column)
                key = sum_key + "小计"
                real_key_list.append(key)
                if len(real_column_list) > 0:
                    table[key] = table[real_column_list].apply(lambda x: x.sum(), axis=1)
                else:
                    table[key] = 0
        return table

    def _after_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        return data.reset_index()

    def write_origin_data(self):
        # 机构汇总不输出明细数据，否则会将真正的汇总给覆盖掉
        pass

    def write_detail_report(self, data: pd.DataFrame):
        # 汇总不输出明细数据，否则会将真正的汇总给覆盖掉
        pass
