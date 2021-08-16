#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:xzr 
@file: sms.py
@time: 2019/02/19
@contact: xzregg@gmail.com
"""

import hashlib
import json
# ==========================================
import random
import re
import time
import traceback

import requests

from framework.route import Route
from framework.views import api_view, notauth, Response, RspError
from ..settings import SMS_CONFIG
from framework.utils import validators


# django 常用导入
# =========================================


def send_sms(mobile, text):
    '''https://www.qcloud.com/document/product/382/5976
    腾讯云短信发送
    '''

    sdkappid = SMS_CONFIG.AppKey
    AppKey = SMS_CONFIG.AppSecret

    t = int(time.time())
    rnd = random.randint(100000, 999999)

    url = 'https://yun.tim.qq.com/v5/tlssmssvr/sendsms?sdkappid=%s&random=%s' % (sdkappid, rnd)
    sig_str = "appkey=" + AppKey + "&random=" + str(rnd) + "&time=" + str(t) + "&mobile=" + str(mobile)
    sig_str = sig_str.encode('utf8')
    sig = hashlib.sha256(sig_str).hexdigest()

    post_data = {
            "tel"   : {
                    "nationcode": "86",
                    "mobile"    : mobile,
            },
            "sign"  : SMS_CONFIG.sms_free_sign_name,
            "tpl_id": int(SMS_CONFIG.sms_template_code),
            "params": [str(text)],
            "sig"   : sig,
            "time"  : t,
            "extend": "",
            "ext"   : "",
    }

    try:
        resp = requests.post(url, data=json.dumps(post_data))
        print(resp.text)
        r = json.loads(resp.text).get('result', 1) == 0
    except Exception as e:
        traceback.print_exc()
        r = False
    return r


class SMSValidateCodeError(RspError): pass


def check_sms_mobile_code(request, mobile, vcode):
    mobile_rule = '^\+?\d{6,}$'
    if mobile != '' and re.match(mobile_rule, mobile):
        mobile = mobile.replace('+86', '')

        if not validators.isMobilePhone(mobile):
            raise SMSValidateCodeError('手机号码格式错误!')

        sms_data = request.session
        now_t = int(time.time())
        st = int(sms_data.get('sms_st', '') or 0)
        print(now_t - st)
        if (now_t - st) > 600:
            raise SMSValidateCodeError('验证码已过期,请重新获取!')
        _vcode = sms_data.get('sms_vdcode', '')
        if not vcode.isdigit() or int(vcode) != (_vcode):
            raise SMSValidateCodeError('验证码错误!')
        if sms_data.get('sms_mobile') != mobile:
            raise SMSValidateCodeError('手机号码不符!')

    else:
        raise SMSValidateCodeError('手机号码格式有错！！')


@Route()
@notauth
@api_view('post')
def send_verification_code(request):
    mobile = request.REQUEST.get('phone', '') or request.REQUEST.get('mobile', '')
    msg = ''
    mobile = mobile.replace('+86', '')
    if not validators.isMobilePhone(mobile):
        raise SMSValidateCodeError('%s 手机号码格式错误' % mobile)

    now_t = int(time.time())

    if request.REQUEST.get('verify', '') != request.session.get('verify', ''):  # 验证码
        request.COOKIES.clear()
        raise SMSValidateCodeError('验证码错误 !')

    st = int(request.session.get('sms_st', '') or 0)

    if (now_t - st) < 59:
        raise SMSValidateCodeError('发送过密,请稍后再发')

    the_num = random.randint(10000, 99999)

    request.session['sms_mobile'] = mobile
    request.session['sms_vdcode'] = the_num
    request.session['sms_st'] = now_t

    _r = send_sms(mobile, the_num)
    del request.session['verify']
    if not _r:
        msg = '%s 当日发送次数过多' % mobile

    return Response(msg=msg)
