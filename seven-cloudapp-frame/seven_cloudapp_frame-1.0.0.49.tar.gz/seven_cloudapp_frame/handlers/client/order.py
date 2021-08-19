# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-09 15:00:05
@LastEditTime: 2021-08-19 10:49:54
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.order_base_model import *
from seven_cloudapp_frame.models.stat_base_model import *


class SyncPayOrderHandler(TaoBaseHandler):
    """
    :description: 同步淘宝支付订单给用户加资产
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 同步淘宝支付订单给用户加资产
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        is_log = self.get_param("is_log",False)
        order_base_model = OrderBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = order_base_model.sync_tao_pay_order(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, invoke_result_data.data["asset_type"], invoke_result_data.data["goods_id"], invoke_result_data.data["sku_id"], invoke_result_data.data["ascription_type"], app_key, app_secret, is_log, invoke_result_data.data["check_user_nick"], invoke_result_data.data["continue_request_expire"], invoke_result_data.data["asset_sub_table"])
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(app_id, act_id, module_id, user_id, open_id, invoke_result_data)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)

    def business_process_executing(self, app_id, act_id, user_id, module_id, login_token):
        """
        :description: 执行前事件
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param login_token:访问令牌
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = {"asset_type": 3, "goods_id": "", "sku_id": "", "ascription_type": 1, "check_user_nick": True, "continue_request_expire": 5, "asset_sub_table": None}
        return invoke_result_data

    def business_process_executed(self, app_id, act_id, module_id, user_id, open_id, invoke_result_data):
        """
        :description: 执行后事件
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param open_id:open_id
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        if invoke_result_data.success == True:
            stat_base_model = StatBaseModel(context=self)
            key_list_dict = {}
            key_list_dict["PayUserCount"] = 1
            key_list_dict["PayCount"] = invoke_result_data["pay_num"]
            key_list_dict["PayMoneyCount"] = invoke_result_data["pay_price"]
            stat_base_model.add_stat_list(app_id, act_id, module_id, user_id, open_id, key_list_dict)
        return invoke_result_data


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
        return self.response_json_success(order_base_model.get_prize_order_list(app_id, act_id, tb_user_id, user_open_id, "", "", "", "", "", order_status, create_date_start, create_date_end, page_size, page_index, order_by, is_search_roster=is_search_roster, is_cache=True))


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