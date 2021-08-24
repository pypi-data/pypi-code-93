ERRNO_OK = 0
ERRNO_500 = 500
ERRNO_404 = 404
ERRMSG_OK = "ok"

ERRNO_INVALID_PARAM = 801

ERRNO_LOGIN_SUCCESS = 0
ERRNO_LOGIN_FAILED = 800
ERRNO_TOKEN_ERROR = 401

ERRNO_USER_NOT_EXIST = 470
ERRNO_USER_EXIST = 471

ERRMSG_USER_NOT_EXIST = "用户不存在"
ERRMSG_USER_EXIST = "用户存在"
ERRMSG_PASSWORD_WRONG = "密码错误，请重新输入"
ERRMSG_LOGIN_SUCCESS = "登录成功！"
ERRMSG_TOKEN_ERROR = "Token已过期！"


def result_ok(data=None):
    res = {
        "errno": ERRNO_OK,
        "errmsg": ERRMSG_OK,
    }
    if data is not None:
        res["data"] = data
    return res


def result_err(msg,errno = ERRNO_INVALID_PARAM):
    return {
        "errno": errno,
        "errmsg": msg,
    }


def result_custom_ok(data, **kwargs):
    kwargs["errno"] = ERRNO_OK
    kwargs["errmsg"] = ERRMSG_OK
    kwargs["data"] = data
    return kwargs
