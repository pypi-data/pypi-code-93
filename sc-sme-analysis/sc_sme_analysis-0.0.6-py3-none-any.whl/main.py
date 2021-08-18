# The MIT License (MIT)
#
# Copyright (c) 2021 Scott Lau
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import os

from sc_utilities import log_init

log_init()

import pandas as pd

from .utils import ConfigUtils
from sc_analyzer_base import BranchUtils, ManifestUtils
from .summary import *
from .analyzer import *


class Runner:

    def __init__(self):
        ConfigUtils.clear()
        self._config = ConfigUtils.get_config()
        # 生成的目标Excel文件存放路径
        self._target_directory = self._config.get("sme.target_directory")
        # 目标文件名称
        self._target_filename = self._config.get("sme.target_filename")
        # 生成的Excel中按客户经理汇总的Sheet的名称
        self._target_manager_summary_sheet_name = self._config.get("sme.target_manager_summary_sheet_name")
        # 生成的Excel中按客户经理汇总的Sheet的名称
        self._target_branch_summary_sheet_name = self._config.get("sme.target_branch_summary_sheet_name")

    def _load_branch_stuff(self):
        try:
            BranchUtils.set_config(self._config)
            # 加载机构名称对应表
            BranchUtils.load_branch_name_mapping()
            # 加载公共户关键字列表
            BranchUtils.load_common_account_keyword_list()
            # 加载业绩归属机构配置
            BranchUtils.load_sales_performance_attribution_mapping()
            # 加载所有发生业务的机构清单
            BranchUtils.load_all_business_branch_list()
            return 0
        except Exception as error:
            logging.getLogger(__name__).error("加载机构名称对应表失败：{}".format(error))
            return 1

    def _load_manifest_stuff(self):
        try:
            ManifestUtils.set_config(self._config)
            # 加载花名册
            ManifestUtils.load_manifest()
            # 加载离职人员调整表
            ManifestUtils.load_leave_employee_mapping()
            # 加载（非息）离职人员归属机构表
            ManifestUtils.load_non_interest_leave_employee_branch_mapping()
            return 0
        except Exception as error:
            logging.getLogger(__name__).error("加载花名册相关信息失败：{}".format(error))
            return 1

    def run(self):
        logging.getLogger(__name__).info("开始进行中小企业部考核数据分析...")

        # 加载机构相关配置
        result = self._load_branch_stuff()
        if result != 0:
            return result

        # 加载花名册相关配置
        result = self._load_manifest_stuff()
        if result != 0:
            return result

        target_filename_full_path = os.path.join(self._target_directory, self._target_filename)
        logging.getLogger(__name__).info("输出文件：{} ".format(target_filename_full_path))
        with pd.ExcelWriter(target_filename_full_path) as excel_writer:
            # 分析客户经理汇总
            manager_summary_analyzer_list, manager_summary_result, target_column_list = \
                self._manager_summary_analysis(excel_writer)
            # 分析机构汇总
            branch_summary_analyzer_list = self._branch_summary_analysis(
                excel_writer,
                manager_summary_result,
                target_column_list
            )
            # 输出原Excel数据
            self._write_original_excel_data(branch_summary_analyzer_list, manager_summary_analyzer_list)
        logging.getLogger(__name__).info("结束中小企业部考核数据分析...")
        return 0

    def _manager_summary_analysis(self, excel_writer):
        manager_summary_analyzer_list = [
            # 有效授信户
            ValidCreditAccountAnalyzer(config=self._config, excel_writer=excel_writer),
            # 普惠贷款余额
            InclusiveFinanceBalanceAnalyzer(config=self._config, excel_writer=excel_writer),
            # 有效结算户
            ValidClearingAccountAnalyzer(config=self._config, excel_writer=excel_writer),
        ]
        # 按客户经理汇总结果
        manifest_data = ManifestUtils.get_manifest_df().copy()
        manager_summary_result = pd.DataFrame()
        previous_data = pd.DataFrame()
        # 输出列清单列表
        target_column_list = list()
        logging.getLogger(__name__).info("按客户经理分析...")
        for analyzer in manager_summary_analyzer_list:
            try:
                manager_summary_result = analyzer.analysis(
                    manifest_data=manifest_data,
                    previous_data=previous_data,
                )
                previous_data = manager_summary_result
                target_column_list.extend(analyzer.get_target_columns())
            except Exception as e:
                logging.getLogger(__name__).exception("分析 {} 时出错".format(analyzer.get_business_type()), exc_info=e)
        # 客户经理汇总分析，待上述分析完成后，这里做一个总计分析
        analyzer = ManagerSummaryAnalyzer(
            config=self._config,
            excel_writer=excel_writer,
            target_column_list=target_column_list,
        )
        try:
            manager_summary_result = analyzer.analysis(
                manifest_data=manifest_data,
                previous_data=previous_data,
            )
        except Exception as e:
            logging.getLogger(__name__).exception("分析 {} 时出错".format(analyzer.get_business_type()), exc_info=e)
        if not manager_summary_result.empty:
            # # 没有业绩的显示0
            # manager_summary_result.fillna(0, inplace=True)
            manager_summary_result.to_excel(excel_writer=excel_writer, index=False,
                                            sheet_name=self._target_manager_summary_sheet_name)
        return manager_summary_analyzer_list, manager_summary_result, target_column_list

    def _branch_summary_analysis(self, excel_writer, manager_summary_result, target_column_list):
        branch_summary_analyzer_list = [
            # 机构汇总
            BranchSummaryAnalyzer(
                config=self._config,
                manager_summary=manager_summary_result,
                target_column_list=target_column_list,
                excel_writer=excel_writer,
            ),
        ]
        # 唯一的机构清单
        branch_summary_result = pd.DataFrame(
            data=set(BranchUtils.get_branch_name_mapping().values()),
            columns=[ManifestUtils.get_branch_column_name()],
            dtype=str
        )
        logging.getLogger(__name__).info("按机构汇总分析...")
        # 按机构汇总结果
        for analyzer in branch_summary_analyzer_list:
            try:
                branch_summary_result = analyzer.analysis(
                    manifest_data=manager_summary_result,
                    previous_data=pd.DataFrame(),
                )
            except Exception as e:
                logging.getLogger(__name__).exception("分析 {} 时出错".format(analyzer.get_business_type()), exc_info=e)
        if not branch_summary_result.empty:
            # 没有业绩的显示0
            branch_summary_result.fillna(0, inplace=True)
            # # 添加机构合计行
            # branch_summary_result.set_index(ManifestUtils.get_branch_column_name(), inplace=True)
            # branch_summary_result.loc["合计"] = branch_summary_result.apply(lambda x: x.sum())
            # branch_summary_result.reset_index(inplace=True)
            # 输出到Excel
            branch_summary_result.to_excel(excel_writer=excel_writer, index=False,
                                           sheet_name=self._target_branch_summary_sheet_name)
        return branch_summary_analyzer_list

    def _write_original_excel_data(self, branch_summary_analyzer_list, manager_summary_analyzer_list):
        logging.getLogger(__name__).info("输出源数据到Excel...")
        # 输出源数据到Excel
        for analyzer in manager_summary_analyzer_list + branch_summary_analyzer_list:
            try:
                analyzer.write_origin_data()
            except Exception as e:
                logging.getLogger(__name__).exception("输出 {} 源数据到Excel时出错".format(analyzer.get_business_type()),
                                                      exc_info=e)


def main():
    try:
        state = Runner().run()
    except Exception as e:
        logging.getLogger(__name__).exception('An error occurred.', exc_info=e)
        return 1
    else:
        return state


if __name__ == '__main__':
    main()
