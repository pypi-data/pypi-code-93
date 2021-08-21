# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-19 09:23:14
@LastEditTime: 2021-08-19 16:12:52
@LastEditors: HuangJianYi
@Description: 
"""
import requests
from Crypto.Cipher import AES
import base64
import xmltodict
from xml.etree import ElementTree
import xml.etree.ElementTree as ET
from urllib.parse import quote
import hashlib
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_framework.base_model import *


class WeChatHelper:
    """
    :description: 微信帮助类
    """
    logger_error = Logger.get_logger_by_name("log_error")

    @classmethod
    def code2_session(self, code, grant_type="authorization_code"):
        """
        :description:临时登录凭证校验
        :param code：登录票据
        :param grant_type：授权方式
        :return: 返回字典包含字段 session_key,openid
        :last_editors: HuangJianYi
        """
        redis_key = "wechat_code:" + str(code)
        redis_init = SevenHelper.redis_init()
        code2_session_dict = redis_init.get(redis_key)
        if code2_session_dict:
            code2_session_dict = SevenHelper.json_loads(code2_session_dict)
            return code2_session_dict
        app_id = config.get_value("app_id")
        app_secret = config.get_value("app_secret")
        param = {
            'js_code': code,  # 用户点击按钮跳转到微信授权页, 微信处理完后重定向到redirect_uri, 并给我们加上code=xxx的参数, 这个code就是我们需要的
            'appid': app_id,
            'secret': app_secret,
            'grant_type': grant_type,
        }

        # 通过code获取access_token
        requset_url = 'https://api.weixin.qq.com/sns/jscode2session'
        resp = None
        try:
            resp = requests.get(requset_url, params=param)
            res_result = SevenHelper.json_loads(resp.text)
            open_id = res_result['openid']
            session_key = res_result['session_key']
            redis_init.set(redis_key, SevenHelper.json_dumps(res_result), ex=60 * 60)
            redis_init.set(f"wechat_sessionkey:{open_id}", session_key, ex=60 * 60)
            return res_result
        except Exception as ex:
            self.logger_error.error("【微信code2_session】" + str(ex) + ":" + str(resp.text))
            return None

    @classmethod
    def decrypt_data_by_code(self, open_id, code, encrypted_Data, iv):
        """
        :description:解析加密数据，客户端判断是否登录状态，如果登录只传open_id不传code，如果是登录过期,要传code重新获取session_key
        :param open_id：open_id
        :param code：登录票据
        :param encrypted_Data：加密数据,微信返回加密参数
        :param iv：微信返回参数
        :return: 解密后的数据，用户信息或者手机号信息
        :last_editors: HuangJianYi
        """
        data = None
        if code:
            code2_session_dict = self.code2_session(code)
            if code2_session_dict:
                open_id = code2_session_dict["openid"]
        try:
            session_key = SevenHelper.redis_init().get(f"wechat_sessionkey:{open_id}")
            app_id = config.get_value("app_id")
            wx_data_crypt = WeChatDataCrypt(app_id, session_key)
            data = wx_data_crypt.decrypt(encrypted_Data, iv)  #data中是解密的信息
        except Exception as ex:
            self.logger_error.error("【微信decrypt_data_by_code】" + str(ex))
        return data

    @classmethod
    def decrypt_data(self, app_id, session_key, encrypted_Data, iv):
        """
        :description:解析加密数据
        :param app_id: 微信小程序标识
        :param session_key: session_key调用登录接口获得
        :param encrypted_Data：加密数据,微信返回加密参数
        :param iv：微信返回参数
        :return: 解密后的数据，用户信息或者手机号信息
        :last_editors: HuangJianYi
        """
        data = {}
        try:
            wx_data_crypt = WeChatDataCrypt(app_id, session_key)
            data = wx_data_crypt.decrypt(encrypted_Data, iv)  #data中是解密的信息
        except Exception as ex:
            self.logger_error.error("【微信decrypt_data】" + str(ex))
        return data

    @classmethod
    def array_to_xml(self, array):
        """array转xml"""
        xml = ["<xml>"]
        for k, v in array.items():
            if v.isdigit():
                xml.append("<{0}>{1}</{0}>".format(k, v))
            else:
                xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
        xml.append("</xml>")
        return "".join(xml)

    @classmethod
    def xml_to_array(self, xml):
        """将xml转为array"""
        array_data = {}
        root = ElementTree.fromstring(xml)
        for child in root:
            value = child.text
            array_data[child.tag] = value
        return array_data

class WeChatDataCrypt:
    """
    :description: 微信数据解密帮助类
    """
    def __init__(self, app_id, session_key):
        self.app_id = app_id
        self.session_key = session_key

    def decrypt(self, encryptedData, iv):
        # base64 decode
        session_key = base64.b64decode(self.session_key)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)
        decrypted = {}
        cipher = AES.new(session_key, AES.MODE_CBC, iv)
        result_data = str(self._unpad(cipher.decrypt(encryptedData)), "utf-8")
        if result_data:
            decrypted = json.loads(result_data)
        if decrypted:
            if decrypted['watermark']['appid'] != self.app_id:
                raise Exception('Invalid Buffer')
        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]

class WeChatPayRequest(object):
    """
    :description: 微信支付请求类
    :description: 配置文件内容 "wechat_pay": {"api_key": "","mch_id": ""}
    """
    """配置账号信息"""
    # =======【基本信息设置】=====================================
    # 微信公众号身份的唯一标识。审核通过后，在微信发送的邮件中查看
    app_id = ""
    # 受理商ID，身份标识
    mch_id = ""
    # API密钥，需要在商户后台设置
    api_key = ""

    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self):
        pay_config = config.get_value("wechat_pay")
        self.app_id = config.get_value("app_id")
        self.api_key = pay_config['api_key']
        self.mch_id = pay_config['mch_id']

    def get_prepay_id(self, unifiedorder_url, params):
        """
        :description: 获取预支付单号prepay_id
        :param unifiedorder_url：微信下单地址
        :param params：请求参数字典
        :return: 
        :last_editors: HuangJianYi
        """
        redis_key = "wechat_prepay_id:" + str(params['out_trade_no'])
        redis_init = SevenHelper.redis_init()
        prepay_id = redis_init.get(redis_key)
        xml = self._get_req_xml(params)
        respone = requests.post(unifiedorder_url, xml, headers={'Content-Type': 'application/xml'})
        msg = respone.text.encode('ISO-8859-1').decode('utf-8')
        xmlresp = xmltodict.parse(msg)
        if xmlresp['xml']['return_code'] == 'SUCCESS':
            if xmlresp['xml']['result_code'] == 'SUCCESS':
                prepay_id = str(xmlresp['xml']['prepay_id'])
                redis_init.set(redis_key, prepay_id, ex=3600 * 1)
                return prepay_id
            else:
                self.logger_error.error("【{params['out_trade_no']},微信统一下单获取prepay_id】" + xmlresp['xml']['err_code_des'])
                return WeixinError(xmlresp['xml']['err_code_des'])
        else:
            self.logger_error.error("【{params['out_trade_no']},微信统一下单获取prepay_id】" + xmlresp['xml']['return_msg'])
            return WeixinError(xmlresp['xml']['return_msg'])

    def create_order(self, out_trade_no, body, total_fee, spbill_create_ip, notify_url, open_id="", time_expire="", trade_type="JSAPI"):
        """
        :description: 创建微信预订单
        :param out_trade_no：商户订单号(支付单号)
        :param body：订单描述
        :param total_fee：支付金额
        :param spbill_create_ip：客户端IP
        :param notify_url：微信支付结果异步通知地址
        :param open_id：微信open_id
        :param time_expire：交易结束时间
        :param trade_type：交易类型trade_type为JSAPI时，openid为必填参数！此参数为微信用户在商户对应appid下的唯一标识, 统一支付接口中，缺少必填参数openid！
        :return: 
        :last_editors: HuangJianYi
        """
        spbill_create_ip = spbill_create_ip if SevenHelper.is_ip(spbill_create_ip) == True else "127.0.0.1"

        params = {
            'appid': self.app_id,  # appid
            'mch_id': self.mch_id,  # 商户号
            'nonce_str': self._get_nonceStr(),
            'body': body,
            'out_trade_no': str(out_trade_no),
            'total_fee': str(int(decimal.Decimal(str(total_fee)) * 100)),
            'spbill_create_ip': spbill_create_ip,
            'trade_type': trade_type,
            'notify_url': notify_url
        }
        if trade_type == "JSAPI":
            if open_id == "":
                return WeixinError("缺少必填参数open_id")
            else:
                params['openid'] = open_id
        if time_expire != "":
            params['time_expire'] = str(time_expire)

        # 开发者调用支付统一下单API生成预交易单
        unifiedorder_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        prepay_id = self.get_prepay_id(unifiedorder_url, params)
        if type(prepay_id) == WeixinError:
            return prepay_id

        params['prepay_id'] = prepay_id
        params['package'] = f"prepay_id={prepay_id}"
        params['timestamp'] = str(int(time.time()))
        sign_again_params = {'appId': params['appid'], 'nonceStr': params['nonce_str'], 'package': params['package'], 'signType': 'MD5', 'timeStamp': params['timestamp']}
        return self._get_sign(sign_again_params)  # 返回给app

    def query_order(self, out_trade_no="", transaction_id=""):
        """
        :description: 查询订单
        :param transaction_id：微信订单号
        :param out_trade_no：商户订单号(支付单号)
        :return: 
        :last_editors: HuangJianYi
        """
        if transaction_id == "" and out_trade_no == "":
            return WeixinError("缺少必填参数transaction_id或out_trade_no")
        xmlresp = {}
        xml = ""
        try:
            params = {
                'appid': self.app_id,  # appid
                'mch_id': self.mch_id,  # 商户号
                'nonce_str': self._get_nonceStr(),
            }
            if transaction_id != "":
                params['transaction_id'] = str(transaction_id)  # 微信交易单号
            if out_trade_no != "":
                params['out_trade_no'] = str(out_trade_no)  # 支付单号

            xml = self._get_req_xml(params)
            queryorder_url = 'https://api.mch.weixin.qq.com/pay/orderquery'  # 微信请求url
            respone = requests.post(queryorder_url, xml, headers={'Content-Type': 'application/xml'})
            msg = respone.text.encode('ISO-8859-1').decode('utf-8')
            xmlresp = xmltodict.parse(msg)
        except Exception as ex:
            self.logger_error.error("【微信查询订单】" + str(ex) + ":" + str(xml))
            return WeixinError("微信查询订单出现异常")
        return xmlresp

    def close_order(self, out_trade_no=""):
        """
        :description: 关闭订单
        :param out_trade_no：商户订单号(支付单号)
        :return: 
        :last_editors: HuangJianYi
        """
        if out_trade_no == "":
            return WeixinError("缺少必填参数out_trade_no")
        xmlresp = {}
        try:
            params = {
                'appid': self.app_id,  # appid
                'mch_id': self.mch_id,  # 商户号
                'nonce_str': self._get_nonceStr(),
                'out_trade_no': str(out_trade_no)  # 支付单号
            }
            xml = self._get_req_xml(params)
            queryorder_url = 'https://api.mch.weixin.qq.com/pay/closeorder'  # 微信请求url
            respone = requests.post(queryorder_url, xml, headers={'Content-Type': 'application/xml'})
            msg = respone.text.encode('ISO-8859-1').decode('utf-8')
            xmlresp = xmltodict.parse(msg)
        except Exception as ex:
            self.logger_error.error("【微信关闭订单】" + str(ex))
            return WeixinError("微信关闭订单出现异常")
        return xmlresp

    def get_pay_status(self, out_trade_no, transaction_id=""):
        """
        :description: 查询订单状态
        :param transaction_id：微信订单号
        :return: 
        :last_editors: HuangJianYi
        """
        xmlresp = self.query_order(out_trade_no, transaction_id)
        if type(xmlresp) == WeixinError:
            return ""
        else:
            if xmlresp['xml']['return_code'] == 'SUCCESS':
                if xmlresp['xml']['result_code'] == 'SUCCESS':
                    return str(xmlresp['xml']['trade_state'] if xmlresp['xml'].__contains__("trade_state") else "")  # SUCCESS--支付成功REFUND--转入退款NOTPAY--未支付CLOSED--已关闭REVOKED--已撤销(刷卡支付)USERPAYING--用户支付中PAYERROR--支付失败(其他原因，如银行返回失败)ACCEPT--已接收，等待扣款
                else:
                    return ""
            else:
                return ""

    def _get_nonceStr(self, length=32):
        """生成随机字符串"""
        import random
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        strs = []
        for x in range(length):
            strs.append(chars[random.randrange(0, len(chars))])
        return "".join(strs)

    def _key_value_url(self, value, urlencode):
        """
        将键值对转为 key1=value1&key2=value2
        对参数按照key=value的格式，并按照参数名ASCII字典序排序
        """
        slist = sorted(value)
        buff = []
        for k in slist:
            v = quote(value[k]) if urlencode else value[k]
            buff.append("{0}={1}".format(k, v))

        return "&".join(buff)

    def _get_sign(self, params):
        """
        生成sign
        拼接API密钥
        """
        stringA = self._key_value_url(params, False)
        stringSignTemp = stringA + '&key=' + self.api_key  # APIKEY, API密钥，需要在商户后台设置
        sign = (hashlib.md5(stringSignTemp.encode("utf-8")).hexdigest()).upper()
        params['sign'] = sign
        return params

    def _get_req_xml(self, params):
        """
        拼接XML
        """
        params = self._get_sign(params)
        xml = "<xml>"
        for k, v in params.items():
            # v = v.encode('utf8')
            # k = k.encode('utf8')
            xml += '<' + k + '>' + v + '</' + k + '>'
        xml += "</xml>"
        return xml.encode("utf-8")

class WeChatPayReponse(object):
    """
    :description: 微信支付响应类
    """

    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self, reponse_xml):
        pay_config = config.get_value("wechat_pay")
        self.data = WeChatHelper.xml_to_array(reponse_xml)  # 接收到的数据，类型为关联数组
        self.api_key = pay_config['api_key']

    def _format_bizquery_paramap(self, paraMap, urlencode):
        """格式化参数，签名过程需要使用"""
        slist = sorted(paraMap)
        buff = []
        for k in slist:
            v = quote(paraMap[k]) if urlencode else paraMap[k]
            buff.append("{0}={1}".format(k, v))

        return "&".join(buff)

    def _get_sign(self, obj):
        """生成签名"""
        # 签名步骤一：按字典序排序参数,format_bizquery_paramap已做
        String = self._format_bizquery_paramap(obj, False)
        # 签名步骤二：在string后加入KEY
        String = "{0}&key={1}".format(String, self.api_key)
        # 签名步骤三：MD5加密
        # String = hashlib.md5(String).hexdigest()
        String = hashlib.md5(String.encode("utf-8")).hexdigest()
        # 签名步骤四：所有字符转为大写
        result_ = String.upper()
        return result_

    def check_sign(self):
        """校验签名"""
        tmpData = dict(self.data)  # make a copy to save sign
        del tmpData['sign']
        sign = self._get_sign(tmpData)  # 本地签名
        if self.data['sign'] == sign:
            return True
        return False

    def get_data(self):
        """获取微信的通知的数据"""
        return self.data

    def get_return_data(self, msg, ok=True):
        """返回xml格式数据"""
        code = "SUCCESS" if ok else "FAIL"
        return WeChatHelper.array_to_xml(dict(return_code=code, return_msg=msg))

class WeChatRefundReponse(object):
    """
    :description: 微信退款响应类
    """

    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self, reponse_xml):
        pay_config = config.get_value("wechat_pay")
        self.data = xmltodict.parse(reponse_xml)  # 接收到的数据
        self.api_key = pay_config['api_key']

    def get_data(self):
        """获取微信的通知的数据"""
        return self.data

    def decode_req_info(self, req_info):
        """解密退款通知加密参数req_info"""
        detail_info = CryptoHelper.aes_decrypt(req_info, CryptoHelper.md5_encrypt(self.api_key))
        dict_req_info = xmltodict.parse(detail_info)
        return dict_req_info

    def get_return_data(self, msg, ok=True):
        code = "SUCCESS" if ok else "FAIL"
        return WeChatHelper.array_to_xml(dict(return_code=code, return_msg=msg))

class WeixinError(Exception):
    def __init__(self, msg):
        super(WeixinError, self).__init__(msg)