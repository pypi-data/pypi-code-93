from __future__ import absolute_import
from __future__ import unicode_literals

class LaiyeException(Exception):
    def __init__(self, msg = "error", code="128"):
        self.msg = msg
        self.code = code

class SSHAuthFailed(Exception):
    def __init__(self, *args, **kwargs):
        self.msg = "ssh账号密码错误"

class SSHConnectFailed(Exception):
    def __init__(self, *args, **kwargs):
        self.msg = "ssh连接失败"

class SSHPortFailed(Exception):
    def __init__(self, *args, **kwargs):
        self.msg = "ssh端口错误"

class SSHAuthInfoMissed(Exception):
    def __init__(self, *args, **kwargs):
        self.msg = "未找到ssh密码或密钥"

class SSHPortOrIpIllegal(Exception):
    def __init__(self, *args, **kwargs):
        self.msg = "IP地址或端口号不合法"

class UtilsError(LaiyeException):
    pass

class ModelError(LaiyeException):
    pass

class HandlerError(LaiyeException):
    pass

class Forbidden(LaiyeException):
    pass