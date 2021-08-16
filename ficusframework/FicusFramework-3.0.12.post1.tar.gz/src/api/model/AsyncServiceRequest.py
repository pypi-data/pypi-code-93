from enum import Enum


class SendType(Enum):
    NEED_ASYNC_SEND = 'NEED_ASYNC_SEND'  # 需要发送异步任务给执行器
    NEED_SYNC_SEND = 'NEED_SYNC_SEND'  # 需要发送同步任务给执行器
    NOT_NEED_SEND = 'NOT_NEED_SEND'  # 不需要发送任务给执行器


class AcceptType(Enum):
    APPLICATION_JSON = 'APPLICATION_JSON'
    TEXT_PLAIN = 'TEXT_PLAIN'


class AsyncServiceRequest:
    """
    异步的请求
    """

    def __init__(self, url: str, method: str = 'POST', header: dict = None, body=None,
                 send_type: SendType = SendType.NEED_ASYNC_SEND, accept_type: AcceptType = AcceptType.APPLICATION_JSON):
        """

        :param url: 请求的URL地址
        :param method:  请求方法
        :param header:  消息头
        :param body:    消息体
        :param send_type:   默认为需要发送异步任务给执行器
        :param accept_type:  接收回调的类型
        """
        self.url = url
        self.method = method
        self.header = header
        self.body = body
        self.send_type = send_type
        self.accept_type = accept_type
