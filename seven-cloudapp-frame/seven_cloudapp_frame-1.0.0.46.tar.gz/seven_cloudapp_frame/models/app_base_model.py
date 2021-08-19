# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-28 09:54:51
@LastEditTime: 2021-08-13 16:04:43
@LastEditors: HuangJianYi
@Description: 
"""
from decimal import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.models.db_models.app.app_info_model import *
from seven_cloudapp_frame.models.db_models.base.base_info_model import *
from seven_cloudapp_frame.models.db_models.friend.friend_link_model import *
from seven_cloudapp_frame.models.db_models.product.product_price_model import *
from seven_cloudapp_frame.models.db_models.tao.tao_login_log_model import *
from seven_cloudapp_frame.models.db_models.version.version_info_model import *


class AppBaseModel():
    """
    :description: 应用信息基类
    """
    def __init__(self, context):
        self.context = context

    def get_app_id(self,store_name):
        """
        :description: 获取应用标识
        :param store_name:店铺名称
        :return app_id
        :last_editors: HuangJianYi
        """
        app_id = ""
        app_info_dict = AppInfoModel(context=self.context).get_cache_dict("store_name=%s", field="app_id", params=[store_name])
        if app_info_dict:
            app_id = app_info_dict["app_id"]
        return app_id

    def get_app_info_dict(self,app_id,is_cache=True):
        """
        :description: 获取应用信息
        :param app_id: 应用标识
        :param is_cache: 是否缓存
        :return: 返回应用信息
        :last_editors: HuangJianYi
        """
        app_info_model = AppInfoModel(context=self.context)
        if is_cache:
            dependency_key = f"app_info:appid_{app_id}"
            return app_info_model.get_cache_dict(dependency_key=dependency_key,where="app_id=%s", params=[app_id])
        else:
            return app_info_model.get_dict(where="app_id=%s", params=[app_id])

    def get_app_expire(self,app_id):
        """
        :description: 获取小程序是否过期未续费
        :param app_id: 应用标识
        :return 1过期0未过期
        :last_editors: HuangJianYi
        """
        now_date = SevenHelper.get_now_datetime()
        invoke_result_data = InvokeResultData()
        app_info_dict = self.get_app_info_dict(app_id)
        if not app_info_dict:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "小程序不存在"
            return invoke_result_data
        result = {}
        if app_info_dict["expiration_date"] == "1900-01-01 00:00:00":
            result["is_expire"] = 0
        elif TimeHelper.format_time_to_datetime(now_date) > TimeHelper.format_time_to_datetime(app_info_dict["expiration_date"]):
            result["is_expire"] = 1
        else:
            result["is_expire"] = 0
        invoke_result_data.data = result
        return invoke_result_data

    def get_base_info_result(self,user_nick,menu_list=[],use_point_list=[]):
        """
        :description: 获取基础信息
        :param user_nick: 用户昵称
        :param menu_list: 左侧菜单列表
        :param use_point_list: 顶部使用指引
        :return
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        base_info_dict = BaseInfoModel(context=self.context).get_dict()
        if not base_info_dict:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "基础信息不存在"
            return invoke_result_data

        # 左上角信息
        info = {}
        info["company"] = "天志互联"
        info["miniappName"] = base_info_dict["product_name"]
        info["logo"] = base_info_dict["product_icon"]

        # 左边菜单
        if len(menu_list) == 0:
            menu_list = []
            menu = {}
            menu["name"] = "创建活动"
            menu["key"] = "create_action"
            menu_list.append(menu)
            menu = {}
            menu["name"] = "活动管理"
            menu["key"] = "act_manage"
            menu_list.append(menu)
            menu = {}
            menu["name"] = "装修教程"
            menu["key"] = "decoration_poster"
            menu_list.append(menu)
            menu = {}
            menu["name"] = "版本更新"
            menu["key"] = "update_ver"
            menu_list.append(menu)

        # 左边底部菜单
        bottom_button_list = []
        bottom_button = {}
        bottom_button["title"] = "发票管理"
        bottom_button["handling_event"] = "popup"
        bottom_button["event_name"] = "billManage"
        bottom_button_list.append(bottom_button)
        bottom_button = {}
        bottom_button["title"] = "配置教程"
        bottom_button["handling_event"] = "popup"
        bottom_button["event_name"] = "use_teaching"
        bottom_button_list.append(bottom_button)
        bottom_button = {}
        bottom_button["title"] = "联系旺旺"
        bottom_button["handling_event"] = "outtarget"
        bottom_button["event_name"] = "http://amos.alicdn.com/getcid.aw?v=2&uid=%E5%A4%A9%E5%BF%97%E4%BA%92%E8%81%94&site=cntaobao&s=1&groupid=0&charset=utf-8"
        bottom_button_list.append(bottom_button)
        bottom_button = {}
        bottom_button["title"] = "号码绑定"
        bottom_button["handling_event"] = "popup"
        bottom_button["event_name"] = "bind_phone"
        bottom_button_list.append(bottom_button)

        # 顶部使用指引
        if len(use_point_list) == 0:
            use_point_list = []
            use_point = {}
            use_point["index"] = "1"
            use_point["title"] = "创建活动并配置完成"
            use_point_list.append(use_point)
            use_point = {}
            use_point["index"] = "2"
            use_point["title"] = "将淘宝小程序装修至店铺"
            use_point_list.append(use_point)
            use_point = {}
            use_point["index"] = "3"
            use_point["title"] = "正式运营淘宝小程序"
            use_point_list.append(use_point)

        data = {}
        data["info"] = info
        data["menu"] = menu_list
        data["bottom_button"] = bottom_button_list
        data["use_point"] = use_point_list

        friend_link_model = FriendLinkModel(context=self.context)
        product_price_model = ProductPriceModel(context=self.context)
        friend_link_list = friend_link_model.get_cache_list(where="is_release=1")
        product_price = product_price_model.get_cache_entity(where="%s>=begin_time and %s<=end_time and is_release=1",order_by="create_time desc",params=[SevenHelper.get_now_datetime()])
        # 把string转成数组对象
        base_info_dict["update_function"] = SevenHelper.json_loads(base_info_dict["update_function"]) if base_info_dict["update_function"] else []
        base_info_dict["decoration_poster_list"] = SevenHelper.json_loads(base_info_dict["decoration_poster_json"]) if base_info_dict["decoration_poster_json"] else []
        base_info_dict["menu_config_list"] = SevenHelper.json_loads(base_info_dict["menu_config_json"]) if base_info_dict["menu_config_json"] else []
        base_info_dict["friend_link_list"] = friend_link_list if len(friend_link_list)>0 else []
        base_info_dict["product_price_list"] = SevenHelper.json_loads(product_price.content) if product_price else []

        #中台指定账号升级
        version_info = VersionInfoModel(context=self.context).get_entity(where="type_id=1",order_by="id desc")
        if version_info:
            if version_info.update_scope == 2 and version_info.white_lists:
                white_lists = list(set(str(version_info.white_lists).split(',')))
                if user_nick in white_lists:
                    base_info_dict.client_ver = version_info.version_number
        #配置文件指定账号升级
        if user_nick:
            if user_nick == config.get_value("test_user_nick"):
                base_info_dict.client_ver = config.get_value("test_client_ver")
        data["base_info"] = base_info_dict
        invoke_result_data.data =data
        return invoke_result_data
   
    def get_app_info_result(self,user_nick,open_id,access_token):
        """
        :description: 获取小程序信息
        :param user_nick:用户昵称
        :param open_id:open_id
        :param access_token:access_token
        :return app_info
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        store_user_nick = user_nick.split(':')[0]
        if not store_user_nick:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起，请先授权登录"
            return invoke_result_data
        if not open_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起，请先授权登录"
            return invoke_result_data
            
        app_info_model = AppInfoModel(context=self.context)
        app_info = app_info_model.get_entity("store_user_nick=%s", params=store_user_nick)
        top_base_model = TopBaseModel(context=self.context)
        invoke_result_data = top_base_model.get_dead_date(store_user_nick,access_token)
        if invoke_result_data.success == False:
            return invoke_result_data
        dead_date = invoke_result_data.data
        now_timestamp = TimeHelper.datetime_to_timestamp(datetime.datetime.strptime(TimeHelper.get_now_format_time('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S'))
        login_log = TaoLoginLogModel(context=self.context).get_entity("open_id=%s", order_by="id desc", params=open_id)
        if app_info:
            app_info.access_token = access_token
            if dead_date != "expire":
                app_info.expiration_date = dead_date
            app_info_model.update_entity(app_info,"expiration_date")

            app_info.user_nick = user_nick
            app_info.dead_date = dead_date
            if app_info.dead_date != "expire":
                dead_date_timestamp = TimeHelper.datetime_to_timestamp(datetime.datetime.strptime(app_info.dead_date, '%Y-%m-%d %H:%M:%S'))
                app_info.surplus_day = int(int(abs(dead_date_timestamp - now_timestamp)) / 24 / 3600)
            app_info.last_login_date = login_log.modify_date if login_log else ""
            invoke_result_data.data = app_info
            return invoke_result_data
        else:
            app_info = AppInfo()
            app_info.access_token = access_token
            base_info = BaseInfoModel(context=self.context).get_dict()
            
            app_info.template_ver = base_info["client_ver"]
            app_info.user_nick = user_nick
            app_info.dead_date = dead_date
            if app_info.dead_date != "expire":
                dead_date_timestamp = TimeHelper.datetime_to_timestamp(datetime.datetime.strptime(app_info.dead_date, '%Y-%m-%d %H:%M:%S'))
                app_info.surplus_day = int(int(abs(dead_date_timestamp - now_timestamp)) / 24 / 3600)
            app_info.last_login_date = login_log.create_date if login_log else ""
            invoke_result_data.data = app_info
            return invoke_result_data
            