# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-02 13:37:05
@LastEditTime: 2021-08-19 16:03:25
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.ip_base_model import *
from seven_cloudapp_frame.handlers.frame_base import *


class IpInfoListHandler(TaoBaseHandler):
    """
    :description: 获取ip列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取ip列表
        :param act_id：活动标识
        :param page_index：页索引
        :param page_size：页大小
        :return: list
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        self.response_json_success(IpBaseModel(context=self).get_ip_info_list(app_id, act_id, page_size, page_index))
