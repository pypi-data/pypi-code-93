from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.sysutil.policy import is_port, is_ip_or_fqdn, is_password
from laipvt.helper.exception import LaiyeException

def check_value(fn):
    def wrapper(self, *args, **kwargs):
        res = True
        if "port" in args[0] or "ocr_" in args[0]:
            if not is_port(args[1]): raise LaiyeException("参数{}的类型不正确, 端口范围: 0-65535".format(args[0]))
        elif "ip" in args[0]:
            if len(args[1]) == 0:
                res = True
            else:
                if isinstance(args[1], list):
                    for ip in args[1]:
                        if not is_ip_or_fqdn(ip): raise LaiyeException("参数{}的类型不正确, 非法的ip地址".format(args[0]))
                else:
                    if not is_ip_or_fqdn(args[1]): raise LaiyeException("参数{}的类型不正确, 非法的ip地址".format(args[0]))
        elif "passwo" in args[0]:
            if not is_password(args[1]): raise LaiyeException("参数{}的类型不正确, 密码复杂度不匹配，要求长度大于8位，并且至少包含一个数字，小写字母，大写字母".format(args[0]))
        if res:
            fn(self, *args, **kwargs)
        else:
            raise LaiyeException("参数{}的类型不正确".format(args[0]))
    return wrapper