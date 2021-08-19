# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 18:31:06
@LastEditTime: 2021-08-19 19:18:55
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.user_base_model import *
from seven_cloudapp_frame.models.order_base_model import *
from seven_cloudapp_frame.models.stat_base_model import *
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.models.asset_base_model import *
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.db_models.tao.tao_coupon_model import *


class LoginHandler(TaoBaseHandler):
    """
    :description: 登录处理
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 登录处理
        :param act_id:活动标识
        :param avatar:头像
        :return:
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        user_nick = self.get_taobao_param().user_nick
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))
        avatar = self.get_param("avatar")

        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error","小程序不存在")

        if self.check_request_user(app_id, app_info_dict["current_limit_count"]):
            return self.response_json_error("current_limit", "登录失败")

        user_base_model = UserBaseModel(context=self)
        invoke_result_data = user_base_model.save_user_by_openid(app_id, act_id, open_id, user_nick, avatar)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)

        invoke_result_data = self.business_process_executed(invoke_result_data)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)

        user_info_dict = invoke_result_data.data
        stat_base_model = StatBaseModel(context=self)
        key_list_dict = {}
        key_list_dict["VisitCountEveryDay"] = 1
        key_list_dict["VisitManCountEveryDay"] = 1
        key_list_dict["VisitManCountEveryDayIncrease"] = 1
        stat_base_model.add_stat_list(app_id, act_id, module_id, user_info_dict["user_id"], open_id, key_list_dict)
        return self.response_json_success(invoke_result_data.data)

    def business_process_executed(self,invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class UpdateUserInfoHandler(TaoBaseHandler):
    """
    :description: 更新用户信息
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 更新用户信息
        :param act_id：活动标识
        :param tb_user_id：用户标识
        :param avatar：头像
        :param is_member_before：初始会员状态
        :param is_favor_before：初始关注状态
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        user_nick = self.get_taobao_param().user_nick
        act_id = int(self.get_param("act_id", 0))
        tb_user_id = int(self.get_param("tb_user_id", 0))
        avatar = self.get_param("avatar")
        is_member_before = int(self.get_param("is_member_before", -1))
        is_favor_before = int(self.get_param("is_favor_before", -1))

        invoke_result_data = InvokeResultData()
        user_base_model = UserBaseModel(context=self)
        invoke_result_data = user_base_model.update_user_info(app_id, act_id, tb_user_id, open_id, user_nick, avatar, is_member_before, is_favor_before)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        else:
            return self.response_json_success("更新成功")


class CheckIsMemberHandler(TaoBaseHandler):
    """
    :description: 校验是否是店铺会员
    """
    def get_async(self):
        """
        :description: 校验是否是店铺会员
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        is_log = self.get_param("is_log", False)
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error", "小程序不存在")
        access_token = app_info_dict["access_token"]
        if access_token == "":
            return self.response_json_error("error", "未授权请联系客服授权")
        top_base_model = TopBaseModel(context=self)
        app_key,app_secret = self.get_app_key_secret()
        return self.response_json_success(top_base_model.check_is_member(app_id, access_token, app_key, app_secret, is_log))


class ApplyBlackUnbindHandler(TaoBaseHandler):
    """
    :description: 提交黑名单解封申请
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 提交黑名单解封申请
        :param act_id:活动标识
        :param tb_user_id:用户标识
        :param reason:解封理由
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))
        tb_user_id = int(self.get_param("tb_user_id", 0))
        reason = self.get_param("reason", "误封号,申请解封")

        invoke_result_data = InvokeResultData()
        user_base_model = UserBaseModel(context=self)
        invoke_result_data = user_base_model.apply_black_unbind(app_id, act_id, tb_user_id, open_id, reason)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        else:
            return self.response_json_success()


class GetCouponPrizeHandler(TaoBaseHandler):
    """
    :description: 领取淘宝优惠券
    """
    @filter_check_params("user_prize_id")
    def get_async(self):
        """
        :description: 领取淘宝优惠券（发奖接口）
        :param user_prize_id:用户奖品标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        user_prize_id = int(self.get_param("user_prize_id", 0))
        is_log = self.get_param("is_log", False)
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error", "小程序不存在")
        access_token = app_info_dict["access_token"]
        if access_token == "":
            return self.response_json_error("error", "未授权请联系客服授权")
        prize_roster_model = PrizeRosterModel(context=self)
        prize_roster_dict = prize_roster_model.get_cache_dict_by_id(user_prize_id)
        if not prize_roster_dict or prize_roster_dict['open_id'] != open_id:
            return self.response_json_error("error", "奖品不存在")
        tao_coupon_model = TaoCouponModel(context=self)
        tao_coupon_dict = tao_coupon_model.get_dict(where="prize_id=%s", params=[prize_roster_dict["prize_id"]])
        if not tao_coupon_dict or tao_coupon_dict['right_ename'] == "":
            return self.response_json_error("error", "奖品不是优惠券,无需领取")
        top_base_model = TopBaseModel(context=self)
        app_key,app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.alibaba_benefit_send(tao_coupon_dict['right_ename'], open_id, access_token, app_key, app_secret, is_log)
        if invoke_result_data.success == False:
            return self.response_json_error("error", "领取失败")
        resp = invoke_result_data.data
        if resp["alibaba_benefit_send_response"]:
            if resp["alibaba_benefit_send_response"]["result_success"] == True:
                prize_roster_model.update_table("prize_status=1", "id=%s", params=[user_prize_id])
                result = {}
                result["prize_name"] = resp["alibaba_benefit_send_response"]["prize_name"]
                return self.response_json_success(result)
            if resp["alibaba_benefit_send_response"]["result_code"] == "COUPON_INVALID_OR_DELETED":
                prize_roster_model.update_table("prize_status=10", "id=%s", params=[user_prize_id])
                return self.response_json_error("error", "领取失败：优惠券无效或已删除")
            if resp["alibaba_benefit_send_response"]["result_code"] == "APPLY_SINGLE_COUPON_COUNT_EXCEED_LIMIT":
                return self.response_json_error("error", "领取失败：优惠券超过限额")
            if resp["alibaba_benefit_send_response"]["result_code"] == "USER_PERMISSION_EXCEED_MAX_RIGHT_COUNT_IN_DAY":
                return self.response_json_error("error", "领取失败：同一张优惠券每天限领取一次")
            if resp["alibaba_benefit_send_response"]["result_code"] == "APPLY_ONE_SELLER_COUNT_EXCEED_LIMIT":
                return self.response_json_error("error", "领取失败：用户优惠券超出10张限制")
        else:
            result = resp["sub_msg"] if resp["sub_msg"] else ""
            if result == "" and resp["result_msg"]:
                result = resp["result_msg"]
            return self.response_json_error("error", f"领取失败:{result}")


class UserAssetListHandler(TaoBaseHandler):
    """
    :description: 获取用户资产列表
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 获取用户资产列表
        :param act_id：活动标识
        :param tb_user_id：用户标识
        :param asset_type：资产类型(1-次数2-积分3-价格档位)
        :return list
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))
        tb_user_id = int(self.get_param("tb_user_id", 0))
        asset_type = int(self.get_param("asset_type", 0))

        asset_base_model = AssetBaseModel(context=self)
        return self.response_json_success(asset_base_model.get_user_asset_list(app_id, act_id, tb_user_id, asset_type, open_id))


class AssetLogListHandler(TaoBaseHandler):
    """
    :description: 资产流水记录
    """
    @filter_check_params("act_id,tb_user_id,asset_type")
    def get_async(self):
        """
        :description: 资产流水记录
        :param act_id：活动标识
        :param tb_user_id：用户标识
        :param asset_type：资产类型(1-次数2-积分3-价格档位)
        :param asset_object_id：资产对象标识
        :param page_size：条数
        :param page_index：页数
        :return list
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))
        tb_user_id = int(self.get_param("tb_user_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        asset_type = int(self.get_param("asset_type", 0))
        asset_object_id = self.get_param("asset_object_id")

        asset_base_model = AssetBaseModel(context=self)
        return self.response_json_success(asset_base_model.get_asset_log_list(app_id, act_id, asset_type, page_size, page_index, tb_user_id, asset_object_id, "", "", "", open_id, 0, ""))


class PrizeRosterListHandler(TaoBaseHandler):
    """
    :description: 用户中奖记录列表
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 用户中奖记录列表
        :param act_id：活动标识
        :param user_id：用户标识
        :param order_no：订单号
        :param goods_type：物品类型（1虚拟2实物）
        :param prize_type：奖品类型(1现货2优惠券3红包4参与奖5预售)
        :param logistics_status：物流状态（0未发货1已发货2不予发货）
        :param prize_status：奖品状态（0未下单（未领取）1已下单（已领取）2已回购10已隐藏（删除）11无需发货）
        :param pay_status：支付状态(0未支付1已支付2已退款3处理中)
        :param page_size：页大小
        :param page_index：页索引
        :return PageInfo
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))
        tb_user_id = int(self.get_param("tb_user_id", 0))
        order_no = self.get_param("order_no")
        goods_type = int(self.get_param("goods_type",-1))
        prize_type = int(self.get_param("prize_type", -1))
        logistics_status = int(self.get_param("logistics_status", -1))
        prize_status = int(self.get_param("prize_status", -1))
        pay_status = int(self.get_param("pay_status", -1))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))

        order_base_model = OrderBaseModel(context=self)
        return self.response_json_success(order_base_model.get_prize_roster_list(app_id, act_id, tb_user_id, open_id, order_no, goods_type, prize_type, logistics_status, prize_status, pay_status, page_size, page_index))


class GetJoinMemberUrlHandler(TaoBaseHandler):
    """
    :description: 获取加入会员地址
    """
    def get_async(self):
        """
        :description: 获取加入会员地址
        :return
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        is_log = bool(self.get_param("is_log",False))
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error", "小程序不存在")
        app_key, app_secret = self.get_app_key_secret()
        user_base_model = UserBaseModel(context=self)
        invoke_result_data = self.response_json_success(user_base_model.get_join_member_url(app_info_dict["access_token"], app_key, app_secret, is_log=is_log))
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class HorseracelampListHandler(TaoBaseHandler):
    """
    :description: 获取跑马灯奖品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取跑马灯奖品列表
        :param act_id: 活动标识
        :param module_id: 活动模块标识
        :param page_size: 条数
        :return:
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", -1))
        page_size = int(self.get_param("page_size", 10))

        if not app_id or not act_id:
            return self.response_json_success({"data": []})
        user_base_model = UserBaseModel(context=self)
        return self.response_json_success(user_base_model.get_horseracelamp_list(act_id, module_id, page_size))