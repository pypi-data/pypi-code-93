# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2021-08-03 10:11:39
@LastEditTime: 2021-08-16 09:05:30
@LastEditors: HuangJianYi
:description: 商品相关
"""
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.db_models.prize.prize_roster_model import *
from seven_cloudapp_frame.models.db_models.act.act_prize_model import *
from seven_cloudapp_frame.models.db_models.app.app_info_model import *


class GoodsListHandler(TaoBaseHandler):
    """
    :description: 商品列表（获取当前会话用户出售中的商品列表）
    """
    def get_async(self):
        """
        :description: 导入商品列表（获取当前会话用户出售中的商品列表）
        :param goods_name：商品名称
        :param order_tag：order_tag
        :param order_by：排序类型
        :param page_index：页索引
        :param page_size：页大小
        :return: 列表
        :last_editors: HuangJianYi
        """
        access_token = self.get_taobao_param().access_token
        goods_name = self.get_param("goods_name")
        order_tag = self.get_param("order_tag", "list_time")
        order_by = self.get_param("order_by", "desc")
        page_index = int(self.get_param("page_index", 0))
        page_size = self.get_param("page_size", 10)
        is_log = bool(self.get_param("is_log",False))

        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.get_goods_list(page_index, page_size, goods_name, order_tag, order_by, access_token, app_key, app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)

class GoodsListByGoodsIDHandler(TaoBaseHandler):
    """
    :description: 根据商品ID串获取商品列表
    """
    @filter_check_params("goods_ids")
    def get_async(self):
        """
        :description: 根据商品ID获取商品列表
        :param goods_ids：商品ID串，多个逗号,分隔
        :return: list
        :last_editors: HuangJianYi
        """
        access_token = self.get_taobao_param().access_token
        goods_ids = self.get_param("goods_ids")
        is_log = bool(self.get_param("is_log",False))

        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.get_goods_list_by_goodsids(goods_ids, access_token, app_key,app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)

class GoodsInfoHandler(TaoBaseHandler):
    """
    :description: 获取商品信息
    """
    @filter_check_params("goods_id")
    def get_async(self):
        """
        :description: 获取商品信息
        :param goods_id：商品ID
        :return: 商品信息
        :last_editors: HuangJianYi
        """
        access_token = self.get_taobao_param().access_token
        goods_id = self.get_param("goods_id")
        is_log = bool(self.get_param("is_log",False))

        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.get_goods_info(goods_id, access_token, app_key, app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)

class BenefitDetailHandler(TaoBaseHandler):
    """
    :description: 获取优惠券详情信息
    """
    def get_async(self):
        """
        :description: 获取优惠券详情信息
        :param right_ename:奖池ID
        :return: dict
        :last_editors: HuangJianYi
        """
        access_token = self.get_taobao_param().access_token
        right_ename = self.get_param("right_ename")
        is_log = bool(self.get_param("is_log",False))

        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.alibaba_benefit_query(right_ename, access_token,app_key, app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)
