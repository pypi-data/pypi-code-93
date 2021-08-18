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
import pandas as pd

from config42 import ConfigManager
from sc_analyzer_base import BaseSummaryDiffAnalyzer


class ManagerSummaryDiffAnalyzer(BaseSummaryDiffAnalyzer):
    """
    客户经理汇总差异分析类
    """

    def __init__(self, *, config: ConfigManager, is_first_analyzer=False):
        super().__init__(config=config, is_first_analyzer=is_first_analyzer)

    def _read_config(self, *, config: ConfigManager):
        super()._read_config(config=config)

        # 生成的Excel中Sheet的名称
        self._target_sheet_name = config.get("diff.manager_summary.target_sheet_name")
        # Sheet名称
        self._sheet_name = config.get("diff.manager_summary.sheet_name")
        # 表头行索引
        self._header_row = config.get("diff.manager_summary.header_row")
        # 索引列名称（Excel中列名必须唯一）
        self._index_column_name = config.get("diff.manager_summary.manager_name_column_name")
        # 待分析差异列名称列表（Excel中列名必须唯一）
        diff_column_dict: dict = config.get("diff.manager_summary.diff_column_list")
        if diff_column_dict is not None and type(diff_column_dict) is dict:
            self._diff_column_dict.update(diff_column_dict)

    def _init_result_data_frame(self):
        # 所有列
        all_columns = list()
        all_columns.append(self._index_column_name)
        all_columns.append(self._target_compare_type_column_name)
        all_columns.extend(self._diff_column_dict)
        result = pd.DataFrame(columns=all_columns)

        # 所有索引值
        all_index_values = set(list(self._current_day_data[self._index_column_name].values))
        # 初始化基础数据
        for index_value in all_index_values:
            for key in self._compare_types:
                result = result.append({
                    self._index_column_name: index_value,
                    self._target_compare_type_column_name: key,
                }, ignore_index=True)

        return result
