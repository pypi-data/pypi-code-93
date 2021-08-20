# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-09 14:11:52
@LastEditTime: 2021-08-19 15:55:16
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.enum import *
from seven_cloudapp_frame.libs.customize.oss2_helper import *
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
        :param address：收货地址
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
        address = self.get_param("address")
        real_name = self.get_param("real_name")
        order_status = int(self.get_param("order_status", -1))
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")
        order_by = self.get_param("order_by","create_date desc")
        is_search_roster = self.get_param("is_search_roster", False)
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        order_base_model = OrderBaseModel(context=self)
        return self.response_json_success(order_base_model.get_prize_order_list(app_id, act_id, tb_user_id, user_open_id, nick_name, order_no, real_name, telephone, address, order_status, create_date_start, create_date_end, page_size, page_index, order_by, is_search_roster=is_search_roster, is_cache=False))


class PrizeRosterListHandler(TaoBaseHandler):
    """
    :description: 用户中奖记录列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户中奖记录列表
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param user_id：用户标识
        :param open_id：open_id
        :param user_nick：用户昵称
        :param order_no：订单号
        :param goods_type：物品类型（1虚拟2实物）
        :param prize_type：奖品类型(1现货2优惠券3红包4参与奖5预售)
        :param logistics_status：物流状态（0未发货1已发货2不予发货）
        :param prize_status：奖品状态（0未下单（未领取）1已下单（已领取）2已回购10已隐藏（删除）11无需发货）
        :param pay_status：支付状态(0未支付1已支付2已退款3处理中)
        :param page_size：页大小
        :param page_index：页索引
        :param create_date_start：开始时间
        :param create_date_end：结束时间
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 500))
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))
        order_no = self.get_param("order_no")
        user_id = int(self.get_param("tb_user_id", 0))
        user_nick = self.get_param("nick_name")
        user_open_id = self.get_param("user_open_id")
        is_order = self.get_param("is_order")
        goods_type = int(self.get_param("goods_type", -1))
        prize_type = int(self.get_param("prize_type", -1))
        logistics_status = int(self.get_param("logistics_status", -1))
        prize_status = int(self.get_param("prize_status", -1))
        pay_status = int(self.get_param("pay_status", -1))
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")
        if is_order:
            prize_status = 1
        order_base_model = OrderBaseModel(context=self)
        return self.response_json_success(order_base_model.get_prize_roster_list(app_id, act_id, module_id, user_id, user_open_id, user_nick, order_no, goods_type, prize_type, logistics_status, prize_status, pay_status, page_size, page_index, create_date_start, create_date_end))


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


class PrizeOrderExportHandler(TaoBaseHandler):
    """
    :description: 导出奖品订单列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 导出奖品订单列表
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param order_no：订单号
        :param order_status：订单状态
        :param nick_name：用户昵称
        :return str
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
        address = self.get_param("address")
        real_name = self.get_param("real_name")
        order_status = int(self.get_param("order_status", -1))
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")
        order_by = self.get_param("order_by", "create_date desc")
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        order_base_model = OrderBaseModel(context=self)
        prize_order_list_dict = order_base_model.get_prize_order_list(app_id, act_id, tb_user_id, user_open_id, nick_name, order_no, real_name, telephone, address, order_status, create_date_start, create_date_end, page_size, page_index, order_by, is_search_roster=True, is_cache=False).data
        result_data = self.business_process_executed(prize_order_list_dict)
        resource_path = OSS2Helper.export_excel(result_data)
        return self.response_json_success(resource_path)

    def business_process_executed(self, prize_order_list_dict):
        """
        :description: 执行后事件
        :param prize_order_list_dict:订单列表
        :return:
        :last_editors: HuangJianYi
        """
        result_data = []
        if len(prize_order_list_dict) > 0:
            frame_base_model = FrameBaseModel(context=self)
            for prize_order_dict in prize_order_list_dict:
                for prize_roster_dict in prize_order_dict["roster_list"]:
                    data_row = {}
                    data_row["小程序订单号"] = prize_order_dict["order_no"]
                    data_row["淘宝子订单号"] = prize_roster_dict["sub_pay_order_no"]
                    data_row["淘宝名"] = prize_order_dict["user_nick"]
                    data_row["模块名称"] = prize_roster_dict["module_name"]
                    data_row["奖品名称"] = prize_roster_dict["prize_name"]
                    data_row["商家编码"] = prize_roster_dict["goods_code"]
                    data_row["姓名"] = prize_order_dict["real_name"]
                    data_row["手机号"] = prize_order_dict["telephone"]
                    data_row["省份"] = prize_order_dict["province"]
                    data_row["城市"] = prize_order_dict["city"]
                    data_row["区县"] = prize_order_dict["county"]
                    data_row["街道"] = prize_order_dict["street"]
                    data_row["收货地址"] = prize_order_dict["address"]
                    data_row["物流单号"] = prize_order_dict["express_no"]
                    data_row["物流公司"] = prize_order_dict["express_company"]
                    if str(prize_order_dict["deliver_date"]) == "1900-01-01 00:00:00":
                        data_row["发货时间"] = ""
                    else:
                        data_row["发货时间"] = str(prize_order_dict["deliver_date"])
                    data_row["订单状态"] = frame_base_model.get_order_status_name(prize_order_dict["order_status"])
                    data_row["奖品价值"] = str(prize_roster_dict["prize_price"])
                    data_row["奖品规格"] = prize_roster_dict["sku_name"]
                    data_row["备注"] = prize_order_dict["seller_remark"]
                    result_data.append(data_row)
        return result_data


class PrizeRosterExportHandler(TaoBaseHandler):
    """
    :description: 导出用户中奖记录列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 导出用户中奖记录列表
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param user_id：用户标识
        :param open_id：open_id
        :param user_nick：用户昵称
        :param order_no：订单号
        :param goods_type：物品类型（1虚拟2实物）
        :param prize_type：奖品类型(1现货2优惠券3红包4参与奖5预售)
        :param logistics_status：物流状态（0未发货1已发货2不予发货）
        :param prize_status：奖品状态（0未下单（未领取）1已下单（已领取）2已回购10已隐藏（删除）11无需发货）
        :param pay_status：支付状态(0未支付1已支付2已退款3处理中)
        :param page_size：页大小
        :param page_index：页索引
        :param create_date_start：开始时间
        :param create_date_end：结束时间
        :return 
        :last_editors: HuangJianYi
        """
        app_id =self.get_app_id()
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 500))
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))
        order_no = self.get_param("order_no")
        user_id = int(self.get_param("tb_user_id",0))
        user_nick = self.get_param("nick_name")
        user_open_id = self.get_param("user_open_id")
        is_order = self.get_param("is_order")
        goods_type = int(self.get_param("goods_type", -1))
        prize_type = int(self.get_param("prize_type", -1))
        logistics_status = int(self.get_param("logistics_status", -1))
        prize_status = int(self.get_param("prize_status", -1))
        pay_status = int(self.get_param("pay_status", -1))
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")
        if is_order:
            prize_status = 1
        order_base_model = OrderBaseModel(context=self)
        prize_roster_list_dict = order_base_model.get_prize_roster_list(app_id, act_id, module_id, user_id, user_open_id, user_nick, order_no, goods_type, prize_type, logistics_status, prize_status, pay_status, page_size, page_index, create_date_start, create_date_end).data
        result_data = self.business_process_executed(prize_roster_list_dict)
        resource_path = OSS2Helper.export_excel(result_data)
        return self.response_json_success(resource_path)

    def business_process_executed(self, prize_roster_list_dict):
        """
        :description: 执行后事件
        :param prize_roster_list_dict:中奖记录列表
        :return:
        :last_editors: HuangJianYi
        """
        result_data = []
        for prize_roster_dict in prize_roster_list_dict:
            data_row = {}
            data_row["行为编号"] = prize_roster_dict["id"]
            data_row["淘宝子订单号"] = prize_roster_dict["sub_pay_order_no"]
            data_row["淘宝名"] = prize_roster_dict["user_nick"]
            data_row["模块名称"] = prize_roster_dict["module_name"]
            data_row["奖品名称"] = prize_roster_dict["prize_name"]
            data_row["奖品价值"] = str(prize_roster_dict["prize_price"])
            data_row["奖品规格"] = prize_roster_dict["sku_name"]
            data_row["获得时间"] = prize_roster_dict["create_date"]
            if prize_roster_dict["order_no"] == "":
                data_row["状态"] = "未下单"
            else:
                data_row["状态"] = "已下单"
            result_data.append(data_row)
        return result_data