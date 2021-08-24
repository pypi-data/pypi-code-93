"""
exception.py 异常处理
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/25/21 5:17 PM
"""


class Error(Exception):
    """
    错误处理
    """


class AclError(Error):
    """
    权限错误处理
    """
