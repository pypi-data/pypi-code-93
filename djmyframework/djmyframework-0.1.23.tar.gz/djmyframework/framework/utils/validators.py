#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:xzr 
@file: validators.py 
@time: 2019/02/19
@contact: xzregg@gmail.com
"""
import re


def isString(x):
    """是否字符"""
    return type(x) is bytes


def isGteZero(x):
    """是否数字"""
    rule = '^\d+$'
    return re.match(rule, str(x))


def isNumber(x):
    rule = '[+-]?\d+$'
    return re.match(rule, str(x))


# 判断是否为浮点数 1.324
def isFloat(x):
    return type(x) is float


# 判断是否为字典 {'a1':'1','a2':'2'}
def isDict(x):
    return type(x) is dict


def isMobilePhone(x):
    """是否电话号码"""
    try:
        x = str(x)
        phoneprefix = int(x[:3])
        in_phoneprefix = 130 <= phoneprefix <= 199
        if len(x) == 11 and x.isdigit() and in_phoneprefix:
            return True
        else:
            return False
    except:
        return False


def isArray(x):
    """是否数组"""
    return type(x) is list


def isEmpty(x):
    """是否为空(含None)"""
    if type(x) is type(None):
        return True
    if isNumber(x):
        return False
    return len(x) == 0


#
def isDate(x):
    """判断是否为日期格式,并且是否符合日历规则 2010-01-31"""
    x = str(x)
    if len(x) == 10:
        rule = '(([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8]))))|((([0-9]{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))-02-29)$/'
        match = re.match(rule, x)
        if match:
            return True
        return False
    return False


def isEmail(x):
    """判断是否为邮件地址"""
    x = str(x)
    rule = '[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$'
    match = re.match(rule, x)

    if match:
        return True
    return False


def isChineseCharString(x):
    """判断是否为中文字符串"""
    x = str(x)
    for v in x:
        if (v >= "\\u4e00" and v <= "\\u9fa5") or (v >= '\\u0041' and v <= '\\u005a') or (
                v >= '\\u0061' and v <= '\\u007a'):
            continue
        else:
            return False
    return True


def isLegalAccounts(x):
    """判断帐号是否合法 允许3-18字节，允许字母数字点减号下划线"""
    x = str(x)
    rule = '[a-zA-Z0-9_.-]{3,18}$'
    match = re.match(rule, x)

    if match:
        return True
    return False


def isLegalPasswords(x):
    """不含空格，6-16个字符， 不含中文"""
    x = str(x)
    if len(x) < 6 or len(x) > 16:
        return False

    for v in x:
        if v.strip() in ['', '.', '-', '_']:
            return False
        else:
            continue
    return True

    return True


def isIpAddr(x):
    """匹配IP地址"""
    x = str(x)
    # rule = '\d+\.\d+\.\d+\.\d+'
    rule = '((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)'
    match = re.match(rule, x)

    if match:
        return True
    return False


def isIdentityIdcard(idcard):
    """Validate id card is valid."""
    IDCARD_REGEX = '[1-9][0-9]{14}([0-9]{2}[0-9X])?'
    if isinstance(idcard, int):
        idcard = str(idcard)

    if not re.match(IDCARD_REGEX, idcard):
        return False

    factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]

    items = [int(item) for item in idcard[:-1]]

    copulas = sum([a * b for a, b in zip(factors, items)])

    ckcodes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

    return ckcodes[copulas % 11].upper() == idcard[-1].upper()
