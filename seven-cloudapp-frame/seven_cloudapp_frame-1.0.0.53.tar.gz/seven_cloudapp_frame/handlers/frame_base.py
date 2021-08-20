# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-05-12 20:11:48
@LastEditTime: 2021-08-20 10:45:50
@LastEditors: HuangJianYi
:description: 
"""
import ast
import random
import decimal
from copy import deepcopy
from asq.initiators import query
from urllib.parse import parse_qs, urlparse

from seven_framework.redis import *
from seven_framework.web_tornado.base_handler.base_api_handler import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.models.user_base_model import *
from seven_cloudapp_frame.models.db_models.app.app_info_model import *
from seven_cloudapp_frame.models.db_models.middler.middler_product_model import *
from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.operation.operation_log_model import *


class FrameBaseHandler(BaseApiHandler):
    """
    :description: 公共handler基类
    """
    def options_async(self):
        self.response_json_success()

    def check_xsrf_cookie(self):
        return

    def json_dumps(self, rep_dic):
        """
        :description: 将字典转化为字符串
        :param rep_dic：字典对象
        :return: str
        :last_editors: HuangJianYi
        """
        return SevenHelper.json_dumps(rep_dic)

    def json_loads(self, rep_str):
        """
        :description: 将字符串转化为字典
        :param rep_str：str
        :return: dict
        :last_editors: HuangJianYi
        """
        return SevenHelper.json_loads(rep_str)

    def response_custom(self, rep_dic):
        """
        :description: 输出公共json模型
        :param rep_dic: 字典类型数据
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        reponse_result_encrypt = config.get_value("reponse_result_encrypt", False)
        if reponse_result_encrypt == True:
            self.http_reponse("0" + self.base64_encode(self.json_dumps(rep_dic)))
        else:
            self.http_reponse(self.json_dumps(rep_dic))

    def response_common(self, success=True, data=None, error_code="", error_message=""):
        """
        :description: 输出公共json模型
        :param success: 布尔值，表示本次调用是否成功
        :param data: 类型不限，调用成功（success为true）时，服务端返回的数据
        :param errorCode: 字符串，调用失败（success为false）时，服务端返回的错误码
        :param errorMessage: 字符串，调用失败（success为false）时，服务端返回的错误信息
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        if hasattr(data, '__dict__'):
            data = data.__dict__
        template_value = {}
        template_value['success'] = success
        template_value['data'] = data
        template_value['error_code'] = error_code
        template_value['error_message'] = error_message

        rep_dic = {}
        rep_dic['success'] = True
        rep_dic['data'] = template_value

        log_extra_dict = {}
        log_extra_dict["is_success"] = 1
        if success == False:
            log_extra_dict["is_success"] = 0

        response_encrypt = config.get_value("response_encrypt", False)
        if response_encrypt == True:
            self.http_reponse("0" + self.base64_encode(self.json_dumps(rep_dic)),log_extra_dict)
        else:
            self.http_reponse(self.json_dumps(rep_dic), log_extra_dict)

    def response_json_success(self, data=None):
        """
        :description: 通用成功返回json结构
        :param data: 返回结果对象，即为数组，字典
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        self.response_common(data=data)

    def response_json_error(self, error_code="", error_message="", data=None, log_type=0):
        """
        :description: 通用错误返回json结构
        :param errorCode: 字符串，调用失败（success为false）时，服务端返回的错误码
        :param errorMessage: 字符串，调用失败（success为false）时，服务端返回的错误信息
        :param data: 返回结果对象，即为数组，字典
        :param log_type: 日志记录类型（0-不记录，1-info，2-error）
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        if log_type == 1:
            self.logging_link_info(f"{error_code}\n{error_message}\n{data}\n{self.request}")
        elif log_type == 2:
            self.logging_link_error(f"{error_code}\n{error_message}\n{data}\n{self.request}")
        self.response_common(False, data, error_code, error_message)

    def response_json_error_params(self):
        """
        :description: 通用参数错误返回json结构
        :param desc: 返错误描述
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: ChenXiaolei
        """
        self.response_common(False, None, "params error", "参数错误")

    def return_dict_error(self, error_code="", error_message=""):
        """
        :description: 返回error信息字典模型
        :param errorCode: 字符串，服务端返回的错误码
        :param errorMessage: 字符串，服务端返回的错误信息
        :return: dict
        :last_editors: HuangJianYi
        """
        rep_dic = {}
        rep_dic['error_code'] = error_code
        rep_dic['error_message'] = error_message

        self.logging_link_error(f"{error_code}\n{error_message}\n{self.request}")

        return rep_dic

    def get_now_datetime(self):
        """
        :description: 获取当前时间
        :return: str
        :last_editors: HuangJianYi
        """
        return SevenHelper.get_now_datetime()

    def create_order_id(self,ran=5):
        """
        :description: 生成订单号
        :param ran：随机数位数，默认5位随机数（0-5）
        :return: 25位的订单号
        :last_editors: HuangJianYi
        """
        return SevenHelper.create_order_id(ran)

    def check_continue_request(self, handler_name, app_id, object_id, expire=500):
        """
        :description: 一个用户同一handler频繁请求校验
        :param handler_name: handler名称
        :param app_id: 应用标识
        :param object_id: object_id(user_id或open_id)
        :param expire: 间隔时间，单位毫秒
        :return:满足频繁请求条件直接输出拦截
        :last_editors: HuangJianYi
        """
        result = False, ""
        if object_id and handler_name and app_id:
            if SevenHelper.is_continue_request(f"continue_request:{handler_name}_{app_id}_{object_id}", expire) == True:
                result = True, f"操作太频繁,请{expire}毫秒后再试"
        return result

    def add_request_user(self, app_id, object_id):
        """
        :description: 每分钟流量UV计数,用于登录接口限制登录
        :param app_id: 应用标识
        :param object_id: 用户唯一标识
        :return:
        :last_editors: HuangJianYi
        """
        redis_init = SevenHelper.redis_init()
        cache_key = f"request_user_list:{app_id}_{str(SevenHelper.get_now_int(fmt='%Y%m%d%H%M'))}"
        redis_init.sadd(cache_key, object_id)
        redis_init.expire(cache_key, 3600)

    def check_request_user(self, app_id, current_limit_count, current_limit_minute=1):
        """
        :description: 每分钟流量UV校验
        :param app_id: 应用标识
        :param current_limit_count: 流量限制数
        :param current_limit_minute: 流量限制时间，默认1分钟
        :return: True代表满足限制条件进行拦截
        :last_editors: HuangJianYi
        """
        if current_limit_count == 0:
            return False
        redis_init = SevenHelper.redis_init()
        if current_limit_minute == 1:
            cache_key = f"request_user_list:{app_id}_{str(SevenHelper.get_now_int(fmt='%Y%m%d%H%M'))}"
        else:
            key_list = []
            for i in  current_limit_minute:
                now_minute_int = int((datetime.datetime.now() + datetime.timedelta(minutes=-i)).strftime('%Y%m%d%H%M'))
                key = f"request_user_list:{app_id}_{str(now_minute_int)}"
                key_list.append(key)
            cache_key = f"request_user_list:{app_id}"
            redis_init.sinterstore(cache_key, key_list)
            redis_init.expire(cache_key, 3600)

        if int(redis_init.scard(cache_key)) >= current_limit_count:
            return True
        else:
            return False

    def get_app_key_secret(self):
        """
        :description: 获取app_key和app_secret
        :param 
        :return app_key, app_secret
        :last_editors: HuangJianYi
        """
        request_app_key = int(self.get_param("app_key", 0))
        app_key = config.get_value("app_key")
        app_secret = config.get_value("app_secret")

        if request_app_key not in (0, app_key):
            cache_key = f"middler_product:requestappkey_{request_app_key}"
            redis_init = SevenHelper.redis_init()
            middler_product_dict = redis_init.get(cache_key)
            if not middler_product_dict:
                middler_product_dict = MiddlerProductModel(context=self).get_dict("app_key=%s", field="app_secret", params=request_app_key)
                if middler_product_dict:
                    redis_init.set(cache_key, SevenHelper.json_dumps(middler_product_dict), ex=config.get_value("cache_expire", 60 * 10))
            else:
                middler_product_dict = json.loads(middler_product_dict)
            if middler_product_dict:
                app_key = request_app_key
                app_secret = middler_product_dict["app_secret"]

        return app_key, app_secret


class TaoBaseHandler(FrameBaseHandler):

    """
    :description: 淘宝handler基类
    """
    def prepare(self):
        """
        :Description: 置于任何请求方法前被调用(请勿重写此函数,可重写prepare_ext)
        :last_editors: HuangJianYi
        """
        if self.__class__.__name__ == "IndexHandler":
            return

        dict_par = {}
        dict_par["open_id"] = self.get_taobao_param().open_id
        dict_par["nick_name"] = self.get_taobao_param().user_nick
        dict_par["app_id"] = self.get_param("app_id")
        if not dict_par["app_id"]:
            dict_par["app_id"] = self.get_taobao_param().source_app_id

        try:
            # 标记日志请求关联
            self._build_http_log(dict_par)

            if dict_par["app_id"] and dict_par["open_id"]:
                # 频繁请求校验
                is_continue_request, error_message = self.check_continue_request(self.__class__.__name__, dict_par["app_id"], dict_par["open_id"])
                if is_continue_request:
                    return self.response_json_error("error", error_message)

                #每分钟流量UV计数,用于登录接口限制登录
                self.add_request_user(str(dict_par["app_id"]), str(dict_par["open_id"]))

        except Exception as ex:
            self.logging_link_error("【淘宝handler基类】" + str(ex))

    def get_taobao_param(self):
        """
        :description: 获取淘宝上下文参数
        :return: TaoBaoParam
        :last_editors: HuangJianYi
        """
        app_key = self.get_param("app_key")
        user_nick = self.get_param("user_nick")
        open_id = self.get_param("open_id")
        env = self.get_param("env")
        mini_app_id = self.get_param("mini_app_id")
        access_token = self.get_param("access_token")
        sign = self.get_param("sign")
        mix_nick = self.get_param("mix_nick")
        tb_user_id = self.get_param("tb_user_id")
        main_user_id = self.get_param("main_user_id")
        source_app_id = self.get_param("source_app_id")
        request_id = self.get_param("request_id")

        #region 指定测试账号和小程序,用于在IDE上测试(前端通过source_app_id关联数据,后端通过user_nick关联数据)
        if source_app_id == config.get_value("client_template_id"):
            #前端（在IDE上返回前端模板id，在千牛上返回正确的id）
            source_app_id = config.get_value("test_source_app_id")
        if source_app_id == "":
            #后端（在IDE上返回空，在千牛上返回后端模板ids）
            source_app_id = config.get_value("test_source_app_id")
            user_nick = config.get_value("test_user_nick")
            open_id = config.get_value("test_open_id")
        #endregion

        info = TaoBaoParam()
        info.app_key = app_key
        info.user_nick = user_nick
        info.open_id = open_id
        info.env = env
        info.mini_app_id = mini_app_id
        info.access_token = access_token
        info.sign = sign
        info.mix_nick = mix_nick
        info.tb_user_id = tb_user_id
        info.main_user_id = main_user_id
        info.source_app_id = source_app_id
        info.request_id = request_id

        return info

    def get_app_id(self):
        """
        :description: 获取app_id(千牛端使用)
        :param self
        :return str
        :last_editors: HuangJianYi
        """
        app_id = self.get_param("app_id")
        if app_id == "":
            user_nick = self.get_taobao_param().user_nick
            if user_nick:
                store_user_nick = user_nick.split(':')[0]
                if store_user_nick:
                    app_info_dict = AppInfoModel(context=self).get_cache_dict(where="store_user_nick=%s", field="app_id", params=store_user_nick)
                    if app_info_dict:
                        app_id = app_info_dict["app_id"]
        return app_id

    def get_is_test(self):
        """
        :description: 判断是否本地测试
        :return: bool
        :last_editors: HuangJianYi
        """
        if self.get_taobao_param().env != "online":
            return True
        return False

    def get_online_url(self, act_id, app_id, module_id=0):
        """
        :description: 获取online_url
        :param act_id:活动标识
        :param app_id:应用标识
        :param module_id:模块标识
        :param page:跳转的首页地址pages/index/index
        :return str
        :last_editors: HuangJianYi
        """
        page_index = ""
        page = config.get_value("page_index")
        if page:
            page_index = "&page=" + CodingHelper.url_encode(page)
        query = CodingHelper.url_encode(f"actid={act_id}")
        if module_id > 0:
            query = CodingHelper.url_encode(f"actid={act_id}&module_id={module_id}")
        online_url = f"https://m.duanqu.com/?_ariver_appid={app_id}{page_index}&query={query}"
        return online_url

    def get_live_url(self, app_id):
        """
        :description: 获取live_url
        :param app_id:app_id
        :return str
        :last_editors: HuangJianYi
        """
        live_url = f"https://market.m.taobao.com/app/taefed/shopping-delivery-wapp/index.html#/putin?mainKey=form&appId={app_id}"
        return live_url

    def create_operation_log(self, operation_type=1, model_name="", handler_name="", old_detail=None, update_detail=None, operate_user_id="",operate_user_name=""):
        """
        :description: 创建操作日志
        :param operation_type：操作类型：1-add，2-update，3-delete
        :param model_name：模块或表名称
        :param handler_name：handler名称
        :param old_detail：当前信息
        :param update_detail：更新之后的信息
        :param operate_user_id：操作人标识
        :param operate_user_name：操作人名称
        :return: 
        :last_editors: HuangJianYi
        """
        operation_log = OperationLog()
        operation_log_model = OperationLogModel(context=self)

        operation_log.user_nick = self.get_taobao_param().user_nick
        operation_log.app_id = self.get_taobao_param().source_app_id
        operation_log.act_id = int(self.get_param("act_id", 0))
        operation_log.open_id = self.get_taobao_param().open_id
        operation_log.request_params = self.request_params
        operation_log.method = self.request.method
        operation_log.protocol = self.request.protocol
        operation_log.request_host = self.request.host
        operation_log.request_uri = self.request.uri
        operation_log.remote_ip = self.get_remote_ip()
        operation_log.create_date = TimeHelper.get_now_format_time()
        operation_log.operation_type = operation_type
        operation_log.model_name = model_name
        operation_log.handler_name = handler_name
        operation_log.detail = old_detail if old_detail else {}
        operation_log.update_detail = update_detail if update_detail else {}
        operation_log.operate_user_id = operate_user_id
        operation_log.operate_user_name = operate_user_name

        if isinstance(operation_log.request_params, dict):
            operation_log.request_params = self.json_dumps(operation_log.request_params)
        if isinstance(old_detail, dict):
            operation_log.detail = self.json_dumps(old_detail)
        if isinstance(update_detail, dict):
            operation_log.update_detail = self.json_dumps(update_detail)

        operation_log_model.add_entity(operation_log)

class WeChatBaseHandler(FrameBaseHandler):
    """
    :description: 微信handler基类
    """
    device_info_dict = {}  # 头部参数

    def prepare_ext(self):
        """
        :Description: 置于任何请求方法前被调用(请勿重写此函数,可重写prepare_ext)
        :last_editors: HuangJianYi
        """
        if self.__class__.__name__ == "IndexHandler":
            return

        try:
            # 将设备信息字符串转为字典类型
            clientheaderinfo_string = self.request.headers._dict.get("Clientheaderinfo")
            if clientheaderinfo_string:
                self.device_info_dict = self.get_device_info(clientheaderinfo_string)

            user_id = self.get_param("user_id")
            if user_id:
                # 频繁请求校验
                is_continue_request, error_message = self.check_continue_request(self.__class__.__name__, self.device_info_dict["pid"], user_id)
                if is_continue_request:
                    return self.response_json_error("error", error_message)

        except Exception as ex:
            self.logging_link_error("【微信handler基类】"+ str(ex))


    def get_device_info(self, device_str):
        """
        :description: 获取头部参数字典
        :param device_string:头部信息串
        :last_editors: HuangJianYi
        """
        device_info_dict = {}
        info_model = parse_qs(device_str)
        device_info_dict["pid"] = int(info_model["PID"][0])
        device_info_dict["union_id"] = "" if "UnionID" not in info_model.keys() else info_model["UnionID"][0]
        device_info_dict["height"] = 0 if "Height" not in info_model.keys() else int(info_model["Height"][0])
        device_info_dict["width"] = 0 if "Width" not in info_model.keys() else int(info_model["Width"][0])
        device_info_dict["version"] = "" if "Version" not in info_model.keys() else info_model["Version"][0]  # 客户端版本号
        device_info_dict["app_version"] = "" if "AppVersion" not in info_model.keys() else info_model["AppVersion"][0]  # 小程序版本号
        device_info_dict["net"] = "" if "Net" not in info_model.keys() else info_model["Net"][0]
        device_info_dict["model_p"] = "" if "Model" not in info_model.keys() else info_model["Model"][0]
        device_info_dict["lang"] = "" if "Lang" not in info_model.keys() else info_model["Lang"][0]
        device_info_dict["ver_no"] = "" if "VerNo" not in info_model.keys() else info_model["VerNo"][0]  #接口版本号
        device_info_dict["chid"] = 0 if "CHID" not in info_model.keys() else int(info_model["CHID"][0])
        device_info_dict["signature_stamp"] = 0 if "SignatureStamp" not in info_model.keys() else int(info_model["SignatureStamp"][0])
        device_info_dict["signature_md5"] = "" if "SignatureMD5" not in info_model.keys() else info_model["SignatureMD5"][0]
        return device_info_dict


def filter_check_head(is_check=True, no_check_params=None, sign_key=""):
    """
    :description: 头部过滤装饰器 仅限handler使用
    :param is_check: 是否开启校验
    :param no_check_params: 不加入参数校验的参数集合
    :param sign_key: 签名key
    :last_editors: HuangJianYi
    """
    def check_head(handler):
        def wrapper(self, **args):

            is_check_head = config.get_value("is_check_head", True)
            if is_check_head == False:
                is_check = False
            else:
                is_check = True
            if is_check == True:
                try:
                    if type(no_check_params) == str:
                        no_check_array = no_check_params.split(",")
                    elif type(no_check_params) == list:
                        no_check_array = no_check_params
                    else:
                        no_check_array = []
                    # 验证是否有设备信息
                    clientheaderinfo_string = self.request.headers._dict.get("Clientheaderinfo")
                    # clientheaderinfo_string = "CHID=1&Height=520&Lang=zh_CN&Model=iPhone%205&Net=unknown&PID=1&PixelRatio=2&SignatureStamp=1611321295380&Ver=1&Version=7.0.4&Width=320"
                    if clientheaderinfo_string:
                        # 将设备信息字符串转为字典类型
                        device_dict = self.get_device_info(clientheaderinfo_string)
                        # 验证签名超时 10分钟过期
                        now_time = TimeHelper.get_now_timestamp(True)
                        if now_time - device_dict["signature_stamp"] > int(1000 * 60 * 10):
                            return self.response_json_error("signature_stamp", "登录超时")
                        # 验证是否有头部信息签名
                        if not device_dict.__contains__("signature_md5"):
                            return self.response_json_error("signature_md5", "缺少参数signature_md5")
                        # 验证头部签名是否成功
                        client_head_dict = dict([(k, v[0]) for k, v in parse_qs(clientheaderinfo_string, True).items() if k != "SignatureMD5" and not k in no_check_array])
                        head_signature_md5 = self.get_signature_md5(client_head_dict, sign_key)
                        signature_md5 = device_dict["signature_md5"].lower()
                        if signature_md5 != head_signature_md5:
                            return self.response_json_error("signature_fail", "头部签名验证失败")
                    else:
                        return self.response_json_error("no_device_info", "没有提交设备信息")
                except Exception as ex:
                    self.logging_link_error("【头部校验异常】" + str(ex))
                    return self.response_json_error("error", "头部验证失败")

            return handler(self, **args)

        return wrapper

    return check_head