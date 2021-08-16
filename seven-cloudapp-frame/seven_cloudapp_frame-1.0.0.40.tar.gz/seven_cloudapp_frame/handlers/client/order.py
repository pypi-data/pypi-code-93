# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-09 15:00:05
@LastEditTime: 2021-08-09 18:15:47
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.order_base_model import *


class PrizeOrderListHandler(TaoBaseHandler):
    """
    :description: 用户奖品订单列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户奖品订单列表
        :param act_id：活动标识
        :param order_no：订单号
        :param tb_user_id：用户标识
        :param user_open_id：open_id
        :param order_status：订单状态（-1未付款-2付款中0未发货1已发货2不予发货3已退款4交易成功）
        :param create_date_start：订单创建时间开始
        :param create_date_end：订单创建时间结束
        :param page_size：页大小
        :param page_index：页索引
        :param order_by：排序
        :param is_search_roster：是否查询订单关联中奖记录
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        tb_user_id = self.get_param("tb_user_id")
        user_open_id = self.get_param("user_open_id")
        order_status = self.get_param("order_status")
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")
        order_by = self.get_param("order_by","id desc")
        is_search_roster = self.get_param("is_search_roster", False)
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        order_base_model = OrderBaseModel(context=self)
        return self.reponse_json_success(order_base_model.get_prize_order_list(app_id, act_id, tb_user_id, user_open_id, "", "", "", "", "", order_status, create_date_start, create_date_end, page_size, page_index, order_by, is_search_roster=is_search_roster, is_cache=True))

class SelectPrizeOrderHandler(TaoBaseHandler):
    """
    :description: 中奖记录下单
    """
    @filter_check_params("act_id,tb_user_id,login_token,real_name,telephone")
    def get_async(self):
        """
        :param act_id：活动标识
        :param tb_user_id：用户标识
        :param login_token:用户访问令牌
        :param prize_ids:用户奖品id串，逗号分隔（为空则将所有未下单的奖品进行下单）
        :param real_name:用户名
        :param telephone:电话
        :param province:省
        :param city:市
        :param county:区县
        :param street:街道
        :param address:地址
        :return
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        tb_user_id = self.get_param("tb_user_id")
        login_token = self.get_param("login_token")
        prize_ids = self.get_param("prize_ids")
        real_name = self.get_param("real_name")
        telephone = self.get_param("telephone")
        province = self.get_param("province")
        city = self.get_param("city")
        county = self.get_param("county")
        street = self.get_param("street")
        address = self.get_param("address")
        order_base_model = OrderBaseModel(context=self)
        invoke_result_data = order_base_model.select_prize_order(app_id, act_id, tb_user_id, login_token, prize_ids, real_name, telephone, province, city, county, street,address)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        else:
            return self.response_json_success()