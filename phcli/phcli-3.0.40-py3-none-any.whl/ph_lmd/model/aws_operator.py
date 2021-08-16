# -*- coding: utf-8 -*-

from abc import abstractmethod


class AWSOperator(object):
    """
    封装 AWS 的常规操作和抽象方法
    """

    @abstractmethod
    def package(self, data):
        """
        对 lambda 的 layer 或者 code 打成 zip 包
        """
        pass

    @abstractmethod
    def create(self, data):
        """
        创建 lambda 的 layer 或者 code 或者 role
        """
        pass

    @abstractmethod
    def lists(self, data):
        """
        获取所有资源实例
        """
        pass

    @abstractmethod
    def get(self, data):
        """
        获取指定资源实例
        """
        pass

    @abstractmethod
    def update(self, data):
        """
        更新 lambda 的 layer 或者 code 或者 role
        """
        pass

    @abstractmethod
    def apply(self, data):
        """
        创建或更新 lambda 的 layer 或者 code 或者 role
        """
        pass

    @abstractmethod
    def stop(self, data):
        """
        使 lambda 或者 API Gateway 停止接受请求
        """
        pass

    @abstractmethod
    def start(self, data):
        """
        重新使 lambda 或者 API Gateway 接受请求
        """
        pass

    @abstractmethod
    def delete(self, data):
        """
        删除 lambda 的 layer, 或者 code, 或者 role, 或者 API Gateway
        """
        pass
