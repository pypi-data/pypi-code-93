# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-17 11:19:05
@LastEditTime: 2021-08-23 09:31:50
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.task_base_model import *


class TaskInfoListHandler(TaoBaseHandler):
    """
    :description: 获取任务列表
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 获取任务列表
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param tb_user_id：用户标识
        :param task_types:任务类型 多个逗号,分隔
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        task_types = self.get_param("task_types")
        is_log = self.get_param("is_log",False)
        task_base_model = TaskBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, task_types)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        task_list = task_base_model.get_client_task_list(app_id, act_id, module_id, user_id, task_types, app_key, app_secret, is_log)
        return self.response_json_success(self.business_process_executed(task_list))

    def business_process_executing(self, app_id, act_id, user_id, module_id, task_types):
        """
        :description: 执行前事件
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param task_types:任务类型 多个逗号,分隔
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        return invoke_result_data

    def business_process_executed(self, task_list):
        """
        :description: 执行后事件
        :param task_list:任务列表
        :return:
        :last_editors: HuangJianYi
        """
        return task_list


class ReceiveRewardHandler(TaoBaseHandler):
    """
    :description: 处理领取任务奖励
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理领取任务奖励
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :param task_id:任务标识
        :param task_sub_type:子任务类型
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        task_id = int(self.get_param("task_id"),0)
        task_sub_type = self.get_param("task_sub_type")
        task_base_model = TaskBaseModel(context=self)
        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token, task_id,task_sub_type)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = task_base_model.process_receive_reward(app_id, act_id, module_id, user_id, login_token, task_id, task_sub_type, self.__class__.__name__, self.request_code)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)

    def business_process_executing(self, app_id, act_id, user_id, module_id, login_token, task_id, task_sub_type):
        """
        :description: 执行前事件
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param login_token:访问令牌
        :param task_id:任务标识
        :param task_sub_type:子任务类型
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        return invoke_result_data

    def business_process_executed(self, invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class FreeGiftHandler(TaoBaseHandler):
    """
    :description: 处理掌柜有礼、新人有礼、免费领取等相似任务
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理掌柜有礼、新人有礼、免费领取等相似任务
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = task_base_model.process_free_gift(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, invoke_result_data.data["check_new_user"], invoke_result_data.data["check_user_nick"], invoke_result_data.data["continue_request_expire"], invoke_result_data.data["task_sub_table"], invoke_result_data.data["asset_sub_table"])
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)

    def business_process_executing(self,app_id, act_id, user_id, module_id, login_token):
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
        invoke_result_data.data = {"check_new_user":True,"check_user_nick":True,"continue_request_expire":5,"task_sub_table":None,"asset_sub_table":None}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class OneSignHandler(TaoBaseHandler):
    """
    :description: 处理单次签到任务
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理单次签到任务
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = task_base_model.process_one_sign(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, invoke_result_data.data["check_new_user"], invoke_result_data.data["check_user_nick"], invoke_result_data.data["continue_request_expire"], invoke_result_data.data["task_sub_table"], invoke_result_data.data["asset_sub_table"])
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data)
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
        invoke_result_data.data = {"check_new_user": True, "check_user_nick": True, "continue_request_expire": 5, "task_sub_table": None, "asset_sub_table": None}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class WeeklySignHandler(TaoBaseHandler):
    """
    :description: 处理每周签到任务
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理每周签到任务
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = task_base_model.process_weekly_sign(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, invoke_result_data.data["check_new_user"], invoke_result_data.data["check_user_nick"], invoke_result_data.data["continue_request_expire"], invoke_result_data.data["task_sub_table"], invoke_result_data.data["asset_sub_table"])
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data)
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
        invoke_result_data.data = {"check_new_user": False, "check_user_nick": True, "continue_request_expire": 5, "task_sub_table": None, "asset_sub_table": None}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class InviteNewUserHandler(TaoBaseHandler):
    """
    :description: 处理邀请新用户任务
    """
    @filter_check_params("act_id,tb_user_id,invite_user_id,login_token")
    def get_async(self):
        """
        :description: 处理邀请新用户任务
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param invite_user_id:邀请用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        invite_user_id = int(self.get_param("invite_user_id", 0))
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = task_base_model.process_invite_new_user(app_id, act_id, module_id, user_id, login_token, invite_user_id, self.__class__.__name__, invoke_result_data.data["check_user_nick"], invoke_result_data.data["continue_request_expire"], invoke_result_data.data["task_sub_table"], invoke_result_data.data["invite_sub_table"])
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data)
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
        invoke_result_data.data = {"check_user_nick": True, "continue_request_expire": 5, "task_sub_table": None, "invite_sub_table": None}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class InviteJoinMemberHandler(TaoBaseHandler):
    """
    :description: 处理邀请加入会员任务
    """
    @filter_check_params("act_id,tb_user_id,invite_user_id,login_token")
    def get_async(self):
        """
        :description: 处理邀请加入会员任务
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param invite_user_id:邀请用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        invite_user_id = int(self.get_param("invite_user_id", 0))
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = task_base_model.process_invite_join_member(app_id, act_id, module_id, user_id, login_token, invite_user_id, self.__class__.__name__, self.request_code, invoke_result_data.data["check_new_user"], invoke_result_data.data["check_user_nick"], invoke_result_data.data["continue_request_expire"], invoke_result_data.data["task_sub_table"], invoke_result_data.data["invite_sub_table"])
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data)
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
        invoke_result_data.data = {"check_new_user": True, "check_user_nick": True, "continue_request_expire": 5, "task_sub_table": None, "invite_sub_table": None}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class ShareReportHandler(TaoBaseHandler):
    """
    :description: 处理分享上报
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理分享上报
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = task_base_model.process_share_report(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, invoke_result_data.data["check_user_nick"], invoke_result_data.data["continue_request_expire"])
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data)
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
        invoke_result_data.data = {"check_user_nick": True, "continue_request_expire": 5}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class CollectGoodsHandler(TaoBaseHandler):
    """
    :description: 处理收藏商品任务
    """
    @filter_check_params("act_id,tb_user_id,login_token,goods_id")
    def get_async(self):
        """
        :description: 处理收藏商品任务
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param goods_id:商品ID
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        goods_id = self.get_param("goods_id")
        login_token = self.get_param("login_token")
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = task_base_model.process_collect_goods(app_id, act_id, module_id, user_id, login_token, goods_id, self.__class__.__name__, invoke_result_data.data["check_user_nick"], invoke_result_data.data["continue_request_expire"], invoke_result_data.data["task_sub_table"], invoke_result_data.data["collect_sub_table"])
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data)
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
        invoke_result_data.data = {"check_user_nick": True, "continue_request_expire": 5,"task_sub_table":None, "collect_sub_table":None}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class BrowseGoodsHandler(TaoBaseHandler):
    """
    :description: 处理浏览商品任务
    """
    @filter_check_params("act_id,tb_user_id,login_token,goods_id")
    def get_async(self):
        """
        :description: 处理浏览商品任务
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param goods_id:商品ID
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        goods_id = self.get_param("goods_id")
        login_token = self.get_param("login_token")
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = task_base_model.process_browse_goods(app_id, act_id, module_id, user_id, login_token, goods_id, self.__class__.__name__, invoke_result_data.data["check_user_nick"], invoke_result_data.data["continue_request_expire"], invoke_result_data.data["task_sub_table"], invoke_result_data.data["browse_sub_table"])
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data)
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
        invoke_result_data.data = {"check_user_nick": True, "continue_request_expire": 5, "task_sub_table": None, "browse_sub_table": None}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class FavorStoreHandler(TaoBaseHandler):
    """
    :description: 处理关注店铺
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理关注店铺
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = task_base_model.process_favor_store(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, invoke_result_data.data["check_user_nick"], invoke_result_data.data["continue_request_expire"], invoke_result_data.data["asset_sub_table"])
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data)
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
        invoke_result_data.data = {"check_user_nick": True, "continue_request_expire": 5, "asset_sub_table": None}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class JoinMemberHandler(TaoBaseHandler):
    """
    :description: 处理加入店铺会员
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理加入店铺会员
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = task_base_model.process_join_member(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, invoke_result_data.data["check_user_nick"], invoke_result_data.data["continue_request_expire"], invoke_result_data.data["asset_sub_table"])
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data)
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
        invoke_result_data.data = {"check_user_nick": True, "continue_request_expire": 5, "asset_sub_table": None}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data
