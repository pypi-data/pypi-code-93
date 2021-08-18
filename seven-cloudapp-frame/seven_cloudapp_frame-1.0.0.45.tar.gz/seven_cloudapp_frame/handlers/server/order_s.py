# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-09 14:11:52
@LastEditTime: 2021-08-18 20:20:42
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.enum import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.order_base_model import *
from seven_cloudapp_frame.models.seven_model import PageInfo


class PayOrderListHandler(TaoBaseHandler):
    """
    :description: 用户购买订单列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户购买订单列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param user_open_id：open_id
        :param nick_name：用户昵称
        :param pay_date_start：订单支付时间开始
        :param pay_date_end：订单支付时间结束
        :param page_size：页大小
        :param page_index：页索引
        :return:
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        tb_user_id = self.get_param("tb_user_id")
        user_open_id = self.get_param("user_open_id")
        nick_name = self.get_param("nick_name")
        pay_date_start = self.get_param("pay_date_start")
        pay_date_end = self.get_param("pay_date_end")
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        order_base_model = OrderBaseModel(context=self)
        return self.response_json_success(order_base_model.get_tao_pay_order_list(app_id, act_id, tb_user_id, user_open_id, nick_name, pay_date_start, pay_date_end, page_size, page_index))


class PrizeOrderListHandler(TaoBaseHandler):
    """
    :description: 用户奖品订单列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户奖品订单列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param order_no：订单号
        :param nick_name：用户昵称
        :param real_name：用户名字
        :param telephone：联系电话
        :param adress：收货地址
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
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        tb_user_id = self.get_param("tb_user_id")
        user_open_id = self.get_param("user_open_id")
        nick_name = self.get_param("nick_name")
        order_no = self.get_param("order_no")
        real_name = self.get_param("real_name")
        telephone = self.get_param("telephone")
        adress = self.get_param("adress")
        real_name = self.get_param("real_name")
        order_status = self.get_param("order_status")
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")
        order_by = self.get_param("order_by","id desc")
        is_search_roster = self.get_param("is_search_roster", False)
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        order_base_model = OrderBaseModel(context=self)
        return self.response_json_success(order_base_model.get_prize_order_list(app_id, act_id, tb_user_id, user_open_id, nick_name, order_no, real_name, telephone, adress, order_status, create_date_start, create_date_end, page_size, page_index, order_by, is_search_roster=is_search_roster, is_cache=False))


class UpdatePrizeOrderSellerRemarkHandler(TaoBaseHandler):
    """
    :description: 更新奖品订单卖家备注
    """
    @filter_check_params("prize_order_id")
    def post_async(self):
        """
        :description: 更新奖品订单卖家备注
        :param app_id：应用标识
        :param prize_order_id：奖品订单标识
        :param remarks：卖家备注
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        prize_order_id = int(self.get_param("prize_order_id", 0))
        seller_remark = self.get_param("seller_remark")
        order_base_model = OrderBaseModel(context=self)
        invoke_result_data = order_base_model.update_prize_order_seller_remark(app_id, prize_order_id, seller_remark)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        self.response_json_success()


class UpdatePrizeOrderStatusHandler(TaoBaseHandler):
    """
    :description: 更新用户奖品订单状态
    """
    @filter_check_params("prize_order_id,order_status")
    def post_async(self):
        """
        :description: 更新用户奖品订单状态
        :param app_id：应用标识
        :param prize_order_id：奖品订单标识
        :param order_status：订单状态
        :param express_company：快递公司
        :param express_no：快递单号
        :return: 实体模型InvokeResultData
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        prize_order_id = int(self.get_param("prize_order_id", 0))
        order_status = int(self.get_param("order_status", 0))
        express_company = self.get_param("express_company")
        express_no = self.get_param("express_no")

        order_base_model = OrderBaseModel(context=self)
        invoke_result_data = order_base_model.update_prize_order_status(app_id, prize_order_id, order_status, express_company, express_no)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        self.response_json_success()


class ImportPrizeOrderHandler(TaoBaseHandler):
    """
    :description: 导入奖品订单进行发货
    """
    @filter_check_params("content,act_id")
    def post_async(self):
        """
        :description: 
        :param app_id：应用标识
        :param content：base64加密后的excel内容
        :param act_id：活动标识
        :param ref_head_name：关联表头名称，可不传
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        content = self.get_param("content")
        ref_head_name = self.get_param("ref_head_name", "小程序订单号")

        order_base_model = OrderBaseModel(context=self)
        invoke_result_data = order_base_model.import_prize_order(app_id, act_id, content, ref_head_name)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        self.response_json_success()
