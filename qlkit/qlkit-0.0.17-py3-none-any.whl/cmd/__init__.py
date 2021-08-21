#!/usr/bin/env python
# -*- coding:utf-8 -*-

from abc import ABC, abstractmethod
from threading import local


class AppThreadLocal(local):
    context = None
    biz_id = None

    def __init__(self, /, **kw):
        self.__dict__.update(kw)

    def set_grpc_metadata(self, metadata):
        """设置 grpc 的 metadata 数据"""
        if not self.context:
            self.context = metadata
        else:
            self.context.update(metadata)
        if "biz_id" in metadata:
            self.set_biz_id(metadata["biz_id"])

    def set_biz_id(self, biz_id: str):
        """设置业务 ID（关于 biz_id 可参看 transport.generate_biz_id）"""
        assert isinstance(biz_id, (str, bytes)), "biz_id must be str or bytes"
        self.biz_id = biz_id

    def __getitem__(self, k):
        return self.__dict__.__getitem__(k)

    def __iter__(self):
        return self.__dict__.__iter__()

    def items(self):
        return self.__dict__.items()

    def get(self, key):
        return self.__dict__.get(key)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()


# 全局使用的线程安全对象
app_local = AppThreadLocal()


class Server(ABC):
    """
    Server object
    定义了一个 Server 程序应该具有的基本行为。所有的 Server 都需要具备这些行为能力。
    gRPC Server、HTTP Server、Event Subscribe Server、Cronjob Server，都需要实现这个 Server。
    """

    @abstractmethod
    def start(self):
        """启动 Server，开始进程生命周期"""
        pass

    @abstractmethod
    def graceful_stop(self):
        """
        优雅退出
        步骤：
        1、停止接收新的输入
        2、等待所有任务执行完
        3、释放 server 进程持有的资源
        4、退出
        """
        pass

    @abstractmethod
    def run_forever(self):
        """
        以一个守护进程方式运行
        """
        pass

    @abstractmethod
    def handle_term_signal(self):
        """响应 TERM 系统信号，执行 graceful_stop"""
        pass
