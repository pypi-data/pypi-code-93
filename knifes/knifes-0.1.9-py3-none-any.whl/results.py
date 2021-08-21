from django.http import JsonResponse
from .jsons import ObjectEncoder


class ApiResult:
    code = 200
    succ = True
    msg = ''
    msg_detail = ''
    data = None

    @classmethod
    def fail(cls, msg, code=400, msg_detail=None):
        ret = ApiResult()
        ret.succ = False
        ret.code = code
        ret.msg = msg
        ret.msg_detail = msg_detail
        return ret

    @classmethod
    def succ(cls, data=None):
        ret = ApiResult()
        ret.code = 200
        ret.succ = True
        ret.data = data
        return ret

    @classmethod
    def succResponse(cls, data=None):
        return JsonResponse(cls.succ(data), encoder=ObjectEncoder, safe=False)

    @classmethod
    def failResponse(cls, msg, code=400, msg_detail=None):
        return JsonResponse(cls.fail(msg, code=code, msg_detail=msg_detail), encoder=ObjectEncoder, safe=False)

    @classmethod
    def tokenInvalid(cls, msg='请先登录'):
        return cls.failResponse(msg, code=300)

    @classmethod
    def missingParam(cls, msg='缺少参数'):
        return cls.failResponse(msg)
