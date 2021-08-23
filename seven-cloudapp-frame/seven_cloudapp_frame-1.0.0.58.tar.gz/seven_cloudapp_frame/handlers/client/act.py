# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-02 14:03:12
@LastEditTime: 2021-08-19 16:03:02
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.models.act_base_model import *
from seven_cloudapp_frame.models.prize_base_model import *


class ActInfoHandler(TaoBaseHandler):
    """
    :description: 获取活动信息
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取活动信息
        :param act_id：活动标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        app_base_model = AppBaseModel(context=self)
        act_base_model = ActBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error", "小程序不存在")
        act_info_dict = act_base_model.get_act_info_dict(act_id)
        if not act_info_dict:
            return self.response_json_error("error", "活动不存在")

        act_info_dict["seller_id"] = app_info_dict["seller_id"]
        act_info_dict["store_id"] = app_info_dict["store_id"]
        act_info_dict["store_name"] = app_info_dict["store_name"]
        act_info_dict["store_icon"] = app_info_dict["store_icon"]
        act_info_dict["app_icon"] = app_info_dict["app_icon"]
        return self.response_json_success(act_info_dict)


class ActPrizeListHandler(TaoBaseHandler):
    """
    :description: 活动奖品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 活动奖品列表
        :param act_id: 活动标识
        :param module_id: 活动模块标识
        :param prize_name: 奖品名称
        :param ascription_type: 奖品归属类型（0-活动奖品1-任务奖品）
        :param page_size: 条数
        :param page_index: 页数
        :return: PageInfo
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", -1))
        prize_name = self.get_param("prize_name")
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        if not app_id or not act_id:
            return self.response_json_success({"data": []})
        prize_base_model = PrizeBaseModel(context=self)
        page_list, total = prize_base_model.get_act_prize_list(app_id, act_id, module_id, prize_name, 0, 0, page_size, page_index)
        page_info = PageInfo(page_index, page_size, total, page_list)
        return self.response_json_success(page_info)



