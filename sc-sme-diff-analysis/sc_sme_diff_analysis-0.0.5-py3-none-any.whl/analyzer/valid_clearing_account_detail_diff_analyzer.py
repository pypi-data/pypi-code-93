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


class ValidClearingAccountDetailDiffAnalyzer(BaseSummaryDiffAnalyzer):
    """
    对公结算户考核明细表-差异分析
    """

    def __init__(self, *, config: ConfigManager, is_first_analyzer=False):
        super().__init__(config=config, is_first_analyzer=is_first_analyzer)

    def _read_config(self, *, config: ConfigManager):
        super()._read_config(config=config)
        # 选中需要处理的机构清单
        self._branch_selected_list = config.get("branch.selected_list")

        # 生成的Excel中Sheet的名称
        self._target_sheet_name = config.get("diff.valid_clearing_account_detail.target_sheet_name")
        # Sheet名称
        self._sheet_name = config.get("diff.valid_clearing_account_detail.sheet_name")
        # 表头行索引
        self._header_row = config.get("diff.valid_clearing_account_detail.header_row")
        # 账户名称列名称（Excel中列名必须唯一）
        self._account_name_column_name = config.get("diff.valid_clearing_account_detail.account_name_column_name")
        # 有效结算户的列名
        self._is_valid_clearing_account_column_name = config.get(
            "diff.valid_clearing_account_detail.is_valid_clearing_account_column_name")
        # 所在部门列的列名
        self._index_column_name = config.get("diff.valid_clearing_account_detail.branch_column_name")
        # 新增列的列名
        self._target_added_column_name = config.get("diff.valid_clearing_account_detail.target_added_column_name")
        # 减少列的列名
        self._target_reduced_column_name = config.get("diff.valid_clearing_account_detail.target_reduced_column_name")

    def _init_result_data_frame(self):
        # 所有列
        all_columns = list()
        all_columns.append(self._index_column_name)
        all_columns.append(self._target_compare_type_column_name)
        all_columns.append(self._target_added_column_name)
        all_columns.append(self._target_reduced_column_name)
        result = pd.DataFrame(columns=all_columns)

        # 所有索引值
        all_index_values = set(list(self._current_day_data[self._index_column_name].values))
        # 初始化基础数据
        for index_value in all_index_values:
            for key in self._compare_types:
                result = result.append({
                    self._index_column_name: index_value,
                    self._target_compare_type_column_name: key,
                    self._target_added_column_name: "",
                    self._target_reduced_column_name: "",
                }, ignore_index=True)

        return result

    def _calculate_diff_according_to_type(
            self,
            result: pd.DataFrame,
            contains_data: bool,
            current_day_data: pd.DataFrame,
            compare_type: str,
            compare_data: pd.DataFrame,
    ):
        if not contains_data:
            return

        for row_i, row in result.iterrows():
            target_cmp_type = row[self._target_compare_type_column_name]
            if target_cmp_type != compare_type:
                continue
            index_value = row[self._index_column_name]
            current_day_selection = current_day_data.loc[current_day_data[self._index_column_name] == index_value]
            # 过滤非有效结算户
            current_day_selection = current_day_selection.loc[
                current_day_selection[self._is_valid_clearing_account_column_name] == 1]
            compare_data_selection = compare_data.loc[compare_data[self._index_column_name] == index_value]
            # 过滤非有效结算户
            compare_data_selection = compare_data_selection.loc[
                compare_data_selection[self._is_valid_clearing_account_column_name] == 1]
            # 当天的客户清单
            client_list_current = current_day_selection.to_dict(orient='list')[
                self._account_name_column_name]
            # 待比较的客户清单
            client_list_compare = compare_data_selection.to_dict(orient='list')[
                self._account_name_column_name]

            # 这里的结果是跟比较时期比增加的
            diff_current = set(client_list_current).difference(client_list_compare)
            if len(diff_current) > 0:
                result.at[row_i, self._target_added_column_name] = ", \n".join(diff_current)
            # 这里的结果是跟比较时期比减少的
            diff_compare = set(client_list_compare).difference(client_list_current)
            if len(diff_compare) > 0:
                result.at[row_i, self._target_reduced_column_name] = ", \n".join(diff_compare)

    def _after_calculated_difference(self, result):
        # 没有的数据填充"-"
        result.fillna("", inplace=True)
        # 处理比较类型的排序
        result[self._target_compare_type_column_name] = pd.Categorical(
            result[self._target_compare_type_column_name],
            self._compare_type_order.keys()
        )
        result.set_index([self._index_column_name], inplace=True)
        return result

    def _deal_with_current_data(
            self, *,
            result: pd.DataFrame,
            current_day_data: pd.DataFrame,
    ):
        pass
