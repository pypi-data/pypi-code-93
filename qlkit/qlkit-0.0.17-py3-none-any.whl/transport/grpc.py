#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
import json
import grpc
import typing as t
from google.protobuf.text_format import MessageToString
from google.protobuf.message import Message

from .. import log
from ..error import Error, new_error, code_pb2
from ..cmd import app_local

"""
python gRPC server example:
https://github.com/avinassh/grpc-errors/blob/HEAD/python
"""


def strip_protobuf_message(message: Message) -> str:
    """将protobuf数据字符串格式化，输出为一行的text内容"""
    if isinstance(message, Message):
        return MessageToString(message, as_one_line=True)
    else:
        return str(message)


class Status(grpc.Status):
    def __init__(self, code: grpc.StatusCode, details: str, trailing_metadata):
        self.code = code
        self.details = details
        self.trailing_metadata = trailing_metadata


def error_to_grpc_status(err: Error) -> grpc.Status:
    grpc_status_code = getattr(grpc.StatusCode, code_pb2.Code.Name(err.code))
    grpc_details = json.dumps({
        "message": err.message,
        "localized_message": err.localized_message
    })
    metadata = [(k, v) for k, v in err.metadata.items()]
    grpc_trailing_metadata = metadata + [("reason", str(err.reason))]
    return Status(grpc_status_code, grpc_details, tuple(grpc_trailing_metadata))


def grpc_exception_to_error(exception: grpc.RpcError) -> Error:
    """
    grpc.RpcError actually are grpc._channel._InactiveRpcError
    https://grpc.github.io/grpc/python/grpc.html#client-side-context
    :param exception:
    :return:
    """
    error_code = exception.code().value[0]
    try:
        details = json.loads(exception.details())
    except json.decoder.JSONDecodeError:
        # in gRPC raw exception, details are utf-8 string.
        error_message = exception.details()
        error_localized_message = ""
    else:
        error_message = details.get("message", "")
        error_localized_message = details.get("localized_message", "")

    trailing_metadata = exception.trailing_metadata()
    error_metadata = {}
    error_reason = 0
    for i in trailing_metadata:
        if i.key == "reason":
            error_reason = int(i.value)
        else:
            error_metadata[i.key] = i.value

    if error_code in (code_pb2.INTERNAL, code_pb2.UNKNOWN):
        # get gRPC debug information
        error_metadata["debug_error_string"] = exception.debug_error_string()

    return new_error(
        error_code, error_reason, error_message,
        error_localized_message, error_metadata
    )


def grpc_execute(service_func):
    """
    接受grpc的请求，转换为Service的输入参数。调用Service的方法，捕获异常，处理Service错误
    转化为grpc的错误信息。返回grpc的response。
    """
    logger = log._get_root_logger()
    transport_context = {}
    logger = log.ApplicationContextAdapter(logger, transport_context)

    @functools.wraps(service_func)
    def wrapper_execute_service(self, request, context):
        # get grpc context add to application threadLocal
        metadata = {k: v for k, v in context.invocation_metadata()}
        app_local.set_grpc_metadata(metadata)

        class_name = self.__class__.__name__
        func_name = service_func.__name__
        caller = "%s.%s" % (class_name, func_name)
        transport_context.update({
            "caller": caller,
            "request": strip_protobuf_message(request),
            "context": context.trailing_metadata()
        })
        try:
            # execute Service method
            response, err = service_func(self, request, context)
        except Exception as e:
            # generate error object
            exception_name = e.__class__.__name__
            err_msg = "Execute %s got %s: %s" % \
                      (caller, exception_name, e)
            err = new_error(code_pb2.UNKNOWN, 0, err_msg)
            transport_context["code"] = err.code
            logger.exception(err_msg)
            err = new_error(code_pb2.INTERNAL, 0, err_msg)
            context.abort_with_status(error_to_grpc_status(err))
        else:
            if err:
                # Service method return error
                logger.debug("[error]:%s" % strip_protobuf_message(err.inner.error))
                context.abort_with_status(error_to_grpc_status(err))
            # check Service method return type
            if response is None:
                err_msg = f"Execute {caller} should return Response, but got None."
                err = new_error(code_pb2.INTERNAL, 0, err_msg)
                logger.critical(err_msg)
                context.abort_with_status(error_to_grpc_status(err))

            # return Service method response(grpc response)
            # add biz id into metadata
            metadata = []
            if app_local.biz_id:
                metadata.append(("biz_id", app_local.biz_id))
            if metadata:
                context.set_trailing_metadata(tuple(metadata))
            transport_context["code"] = code_pb2.OK
            logger.debug("return: %s" % strip_protobuf_message(response))

            return response

    return wrapper_execute_service


class GrpcResponse(object):
    """
    为了方便 grpc 客户端处理逻辑而设计
    用例：
    response = client.GetUser(request)
    if response.is_success():       # 一定要先检查是否成功，失败的请求不会有protobuf对象
        # response.User 是 protobuf 定义的对象，response 会自动识别到 grpc 传输的 protobuf 对象名并且注入。
        return User(user_id=response.User.user_id, name=response.User.name)
    else:
        # request get error
        if response.error.is_not_found():
            pass
        elif response.error.is_invalid_argument():
            pass
        else:
            pass

    关于 response 的 protobuf 对象和 error 对象：
    protobuf 对象会被自动注入到 response 中，属性名与 protobuf 对象名一致。
    user.proto
    message User {
        int32 user_id
        string name
    }
    可通过response.User.user_id response.User.name访问 User 对象。

    error：
        如果 grpc 的通信返回了错误，则会自动将错误实例化到 response.error 中。
    """

    def __init__(self, grpc_context: grpc.RpcContext, protobuf=None):
        self._protobuf = protobuf
        self._grpc_context = grpc_context
        self._inject_protobuf()
        self.error = self._init_error()
        self._metadata = self._init_metadata()

    def _inject_protobuf(self):
        """
        将 grpc 传输的 protobuf对象注入到 response 中
        """
        if self._protobuf:
            setattr(self, self._protobuf.DESCRIPTOR.name, self._protobuf)

    def _init_error(self):
        if not self.is_success():
            # if context code != 0, than return error
            return grpc_exception_to_error(self._grpc_context)
        else:
            return None

    def is_success(self):
        code = self._grpc_context.code().value[0]
        return code == code_pb2.OK

    def get_metadata(self):
        """get error metadata or context metadata"""
        return self._metadata.copy()

    def _init_metadata(self):
        metadata = {}
        if self.is_success():
            trailing_metadata = self._grpc_context.trailing_metadata()
            for i in trailing_metadata:
                metadata[i.key] = i.value
        else:
            # get gRPC debug information
            metadata["debug_error_string"] = self._grpc_context.debug_error_string()
        return metadata


class Client(object):
    """
    Grpc 客户端
    行为：
        自动处理异常，返回 GrpcResponse 对象
    """
    def __init__(self, stub_method):
        self.stub_method = stub_method

    def _add_biz_into_metadata(self, metadata: t.Optional[dict]):
        if app_local.biz_id:
            if metadata:
                metadata["biz_id"] = app_local.biz_id
            else:
                metadata = {"biz_id": app_local.biz_id}
        return metadata

    def call(self, request, metadata: dict = None, timeout=None,
             wait_for_ready=None, compression=None) -> GrpcResponse:
        if metadata:
        # add biz id to metadata
            metadata = self._add_biz_into_metadata(metadata)
            for k, v in metadata.items():
                assert isinstance(k, (str, bytes)), "Metadata key must be str or bytes"
                assert isinstance(v, (str, bytes)), "Metadata value must be str or bytes"
            grpc_metadata = tuple(metadata.items())
        else:
            grpc_metadata = None

        try:
            response, context = self.stub_method.with_call(
                request, timeout, grpc_metadata,
                wait_for_ready=wait_for_ready, compression=compression
            )
        except grpc.RpcError as grpc_client_context:
            return GrpcResponse(grpc_client_context)
        else:
            return GrpcResponse(context, response)


class GrpcClient(object):
    """
    1. normal grpc client, error handing
    2. circuitbreaker
    3. custom metadata
    stub = some_pb_gprc.XX_Stub(channel)
    with GrpcClient(stub) as client:
        response = client.Grpc_Method(request)
        # handle response
    """

    class Object(object):
        def __init__(self, stub):
            self.stub = stub

    def __init__(self, stub):
        self.inner = self.Object(stub)

    def __getattr__(self, item):
        if item == "stub":
            return self.inner.stub
        stub_method = getattr(self.inner.stub, item)
        return Client(stub_method).call

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
