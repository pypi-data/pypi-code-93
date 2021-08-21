import math
from dataclasses import dataclass, field, is_dataclass, asdict
from common.logging_config import logger
from django.core.exceptions import FieldError
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from rest_framework.exceptions import ValidationError

SUCCESS = "success"
FAILURE = "failure"

# # 请求成功，但条件筛选结果集为空
# EMPTY_RESOURCE = 20004

# 请求错误码（主要是参数校验）
REQUEST_ERROR_CODE = 400

# 未授权
UNAUTHORIZED = 401

#
FORBID_CODE = 403

# 服务器内部错误
SERVER_ERROR_CODE = 500

# 上层服务错误
UPSTREAM_SERVER_ERROR_CODE = 502

# 请求上层服务超时
UPSTREAM_SERVER_WAIT_TIMEOUT_CODE = 504

ERROR_CODE_TUPLE = (
    REQUEST_ERROR_CODE,
    FORBID_CODE,
    SERVER_ERROR_CODE,
    UPSTREAM_SERVER_ERROR_CODE,
    UPSTREAM_SERVER_WAIT_TIMEOUT_CODE,
)
results_version: str = ""


def init_version(version: str):
    global results_version
    results_version = version


@dataclass
class Results:
    status: str = FAILURE
    code: int = REQUEST_ERROR_CODE
    version: str = results_version
    describe: str = ""
    data_length: int = 0
    data: dict = field(default_factory=dict)

    def __setattr__(self, key, value):
        super(Results, self).__setattr__(key, value)
        if key == "code":
            if value not in ERROR_CODE_TUPLE:
                super(Results, self).__setattr__("status", SUCCESS)
            else:
                super(Results, self).__setattr__("status", FAILURE)
        if key == "data":
            if (isinstance(value, dict) or isinstance(value, list)) and self.data_length == 0:
                super(Results, self).__setattr__("data_length", len(value))
        if not self.version:
            super(Results, self).__setattr__("version", results_version)


@dataclass
class PageTypeResults:
    result: list = field(default_factory=list)
    total_page: int = 0
    total: int = 0
    page: int = 0
    size: int = 0
    group: list = field(default_factory=list)

    def __setattr__(self, key, value):
        if key != "result" and key != "group":
            value = int(value)
        super(PageTypeResults, self).__setattr__(key, value)
        if all([self.total, self.page, self.size]) and self.total_page == 0:
            super(PageTypeResults, self).__setattr__("total_page", math.ceil(self.total / self.size))


class RESTResponse(JsonResponse):
    def __init__(self, data, encoder=DjangoJSONEncoder, safe=True, json_dumps_params=None, **kwargs):
        if not json_dumps_params:
            json_dumps_params = {"ensure_ascii": False}
        if isinstance(data, Results):
            super(RESTResponse, self).__init__(
                asdict(data),
                status=data.code,
                encoder=encoder,
                safe=safe,
                json_dumps_params=json_dumps_params,
                **kwargs,
            )
        elif is_dataclass(data):

            super(RESTResponse, self).__init__(
                asdict(data), encoder=encoder, safe=safe, json_dumps_params=json_dumps_params, **kwargs
            )
        else:
            super(RESTResponse, self).__init__(
                data, encoder=encoder, safe=safe, json_dumps_params=json_dumps_params, **kwargs
            )


def get_error_status_code(error, results: Results = None):
    """
    根据错误类型，获取状态码和信息
    :param error:
    :return:
    """
    logger.exception(error)
    if isinstance(error, ValidationError):
        status_code = REQUEST_ERROR_CODE
    elif isinstance(error, ValueError):
        status_code = REQUEST_ERROR_CODE
    elif isinstance(error, FieldError):
        status_code = REQUEST_ERROR_CODE
    else:
        status_code = SERVER_ERROR_CODE
    describe = str(error)
    if isinstance(results, Results):
        results.code = status_code
        results.describe = describe
    return status_code, describe
