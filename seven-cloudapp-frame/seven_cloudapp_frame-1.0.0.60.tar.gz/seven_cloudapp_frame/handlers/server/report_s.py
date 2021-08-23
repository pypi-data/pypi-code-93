# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-11-16 13:44:20
@LastEditTime: 2021-08-16 09:07:46
@LastEditors: HuangJianYi
:description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.stat_base_model import *


class StatReportListHandler(TaoBaseHandler):
    """
    :description: 报表数据列表(表格)
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 报表数据列表(表格)
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param start_date：开始时间
        :param end_date：结束时间
        :return list
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")

        stat_base_model = StatBaseModel(context=self)
        return self.response_json_success(stat_base_model.get_stat_report_list(act_id, module_id, start_date, end_date))

class TrendReportListHandler(TaoBaseHandler):
    """
    :description: 报表数据列表(趋势图)
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 报表数据列表(趋势图)
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param start_date：开始时间
        :param end_date：结束时间
        :return list
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")

        stat_base_model = StatBaseModel(context=self)
        return self.response_json_success(stat_base_model.get_trend_report_list(act_id, module_id, start_date, end_date))