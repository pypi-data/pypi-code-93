# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 17:00:55
@LastEditTime: 2021-08-19 17:36:03
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.models.db_models.course.course_info_model import *
from seven_cloudapp_frame.models.db_models.saas.saas_custom_model import *
from seven_cloudapp_frame.models.db_models.marketing.marketing_program_model import *
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


class LeftNavigationHandler(TaoBaseHandler):
    """
    :description: 左侧导航栏
    """
    def get_async(self):
        """
        :description: 左侧导航栏
        :return:
        :last_editors: HuangJianYi
        """
        app_base_model = AppBaseModel(context=self)
        invoke_result_data = app_base_model.get_left_navigation(self.get_taobao_param().user_nickm, self.get_taobao_param().access_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class RightExplainHandler(TaoBaseHandler):
    """
    :description: 右侧各种教程和说明导航
    """
    def get_async(self):
        """
        :description: 右侧各种教程和说明导航
        :params course_type_id:分类标识
        :return 
        :last_editors: HuangJianYi
        """
        course_type_id = self.get_param("course_type_id",0)
        course_info_model = CourseInfoModel(context=self)
        condition = "is_release=1"
        params = []
        if course_type_id > 0:
            condition += "course_type_id=%s"
            params.append(course_type_id)
        course_info_list = course_info_model.get_cache_list(condition, params=params)
        return self.response_json_success(course_info_list)


class FriendLinkListHandler(TaoBaseHandler):
    """
    :description: 获取友情链接列表
    """
    def get_async(self):
        """
        :description: 获取友情链接列表
        :param {*}
        :return list
        :last_editors: HuangJianYi
        """
        friend_link_model = FriendLinkModel(context=self.context)
        friend_link_list = friend_link_model.get_cache_list(where="is_release=1")
        return self.response_json_success(friend_link_list)


class SaasCustomHandler(TaoBaseHandler):
    """
    :description: saas定制化信息获取
    """
    def get_async(self):
        """
        :description: saas定制化信息获取
        :param {*}
        :return int
        :last_editors: HuangJianYi
        """
        user_nick = self.get_taobao_param().user_nick
        if not user_nick:
            return self.response_json_success(0)
        store_user_nick = user_nick.split(':')[0]
        if not store_user_nick:
            return self.response_json_success(0)
        cloud_app_id = 0
        saas_custom = SaasCustomModel(context=self).get_entity("store_user_nick=%s AND is_release=1", params=store_user_nick)
        if saas_custom:
            cloud_app_id = saas_custom.cloud_app_id

        return self.response_json_success(cloud_app_id)


class SendSmsHandler(TaoBaseHandler):
    """
    :description: 发送短信
    """
    def get_async(self):
        """
        :description: 发送短信
        :param thelephone：电话号码
        :return 
        :last_editors: HuangJingCan
        """
        open_id = self.get_taobao_param().open_id
        thelephone = self.get_param("thelephone")
        client = AcsClient('LTAI4FwMYR1FBBui21t7cyh7', 'zyTM5zpYcL8lMXwtDgVoCfHgndoSKi', 'cn-hangzhou')

        result_code = str(random.randint(100000, 999999))
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', "cn-hangzhou")
        request.add_query_param('PhoneNumbers', thelephone)
        request.add_query_param('SignName', "天志互联")
        request.add_query_param('TemplateCode', "SMS_193145309")
        request.add_query_param('TemplateParam', "{\"code\":" + result_code + "}")

        response = client.do_action(request)

        result = dict(json.loads(response))
        result["result_code"] = result_code
        #记录验证码
        self.redis_init().set("user_" + open_id + "_bind_phone_code", result_code, ex=300)

        return self.response_json_success()


class MarketingProgramListHandler(TaoBaseHandler):
    """
    :description: 获取营销方案列表获取营销方案列表
    """
    def get_async(self):
        """
        :description: 获取营销方案列表
        :return: 列表
        :last_editors: HuangJianYi
        """
        marketing_program_list = MarketingProgramModel(context=self).get_cache_dict_list()
        return self.response_json_success(marketing_program_list)