# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-03 09:24:50
@LastEditTime: 2021-08-19 16:03:12
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.db_models.prize.prize_roster_model import *


class SubmitSkuHandler(TaoBaseHandler):
    """
    :description: 中奖记录选择SKU提交
    """
    @filter_check_params("user_prize_id,sku_id")
    def get_async(self):
        """
        :description: 提交SKU
        :param user_prize_id：用户中奖信息标识
        :param sku_name：sku属性名称
        :param sku_id：sku_id
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        user_prize_id = int(self.get_param("user_prize_id"))
        sku_name = self.get_param("sku_name")
        sku_id = self.get_param("sku_id")


        prize_roster_model = PrizeRosterModel(context=self)
        prize_roster = prize_roster_model.get_cache_entity_by_id(user_prize_id)
        if not prize_roster or prize_roster.open_id != open_id or prize_roster.app_id != app_id:
            return self.response_json_error("no_user_prize", "对不起，找不到该奖品")
        if prize_roster.is_sku > 0:
            prize_roster.sku_id = sku_id
            prize_roster.sku_name = sku_name
            goods_code_list = self.json_loads(prize_roster.goods_code_list)
            goods_codes = [i for i in goods_code_list if str(i["sku_id"]) == sku_id]
            if goods_codes and len(goods_codes)>0 and ("goods_code" in goods_codes[0].keys()):
                prize_roster.goods_code = goods_codes[0]["goods_code"]
        prize_roster_model.update_entity(prize_roster, "sku_id,sku_name,goods_code")

        return self.response_json_success()


class SkuInfoHandler(TaoBaseHandler):
    """
    :description: 获取SKU信息
    """
    @filter_check_params("num_iid")
    def get_async(self):
        """
        :description: 获取SKU信息
        :param num_iid：num_iid
        :return
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        num_iid = self.get_param("num_iid")
        is_log = bool(self.get_param("is_log",False))

        top_base_model = TopBaseModel(context=self)
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error", "小程序不存在")
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.get_goods_list_by_goodsids(num_iid, app_info_dict["access_token"], app_key, app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if "items_seller_list_get_response" in invoke_result_data.data.keys():
            if "items" in invoke_result_data.data["items_seller_list_get_response"].keys():
                return self.response_json_success(invoke_result_data.data["items_seller_list_get_response"])
        else:
            act_prize = ActPrizeModel(context=self).get_dict("goods_id=%s and sku_json<>'' and is_sku=1 ", params=[num_iid])
            if not act_prize:
                return self.response_json_error("error", "对不起，找不到该商品的sku")
            sku_detail = self.json_loads(act_prize['sku_json'])
            return self.response_json_success(sku_detail["items_seller_list_get_response"])


class GoodsListHandler(TaoBaseHandler):
    """
    :description: 获取商品列表
    """
    def get_async(self):
        """
        :description: 获取商品列表
        :param page_index：页索引
        :param page_size：页大小
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        page_index = int(self.get_param("page_index", 0))
        page_size = self.get_param("page_size", 10)
        is_log = bool(self.get_param("is_log",False))

        top_base_model = TopBaseModel(context=self)
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error", "小程序不存在")
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.get_goods_list(page_index, page_size, "", "", "", app_info_dict["access_token"], app_key, app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)
