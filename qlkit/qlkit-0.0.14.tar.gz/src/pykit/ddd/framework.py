#!/usr/bin/env python
# -*- coding:utf-8 -*-
import inspect
from abc import ABC
import uuid
import json

# Application Layer


class ApplicationService(object):
    """
    def some_use_case(self, request) -> response, error:
        pass
    """
    pass


# Domain Layer


class DomainService(object):
    pass


class DomainSpecification(object):
    pass


class DomainStrategy(object):
    pass


class Factory(object):
    pass


class AggregateRoot(object):
    pass


class Entity(object):
    pass


class ValueObject(object):
    """
    值对象。具有不变性、相等性和可替换性。
    """
    
    def as_dict(self):
        return self.__dict__.copy()


class AbcRepository(ABC):
    """
    Domain 层的抽象Repository，只定义一个interface。
    """
    pass

# Remote Service call


class RemoteServiceInterface(ABC):
    """
    RemoteService是interface，定义远端服务中需要用到的API。需要在Infra实现。
    方法中的参数和返回值都需要是本服务中的领域模型（DomainObject）。
    示例：
    class UserServiceInterface(abc.ABC):

        @abc.abstractmethod
        def login(self, player: Player) -> Player:
            pass

    如上所定义的是一个远端服务UserService。其中的Player是当前服务的DomainObject。
    """
    pass


"""
RemoteServiceImpl、Adaptor、Translator都属于Infra层。因为这里涉及到了具体的技术层面
的细节，不是业务逻辑。而RemoteServiceInterface描述的是业务逻辑，应该放在Domain层。
"""


class Adaptor(object):
    """
    Adaptor 复制具体的远端调用的实现。如果是gRPC请求，Adaptor负责创建、管理网络连接，
    负责发送请求。
    同时，通过调用Translator，完成DataTransferObject和DomainObject的转换。
    """
    pass


class Translator(object):
    """
    Translator负责处理外部数据与内部领域模型的转换。DTO->DO DO->DTO
    """
    pass


class InspectInitMixin(object):
    """
    InspectInit 用于根据do __init__的签名参数名列表生成do属性
    eg: def __init__(self, a, b):
        self.a = a
        self.b = b
    """
    def inspect_init(self, init_args: dict) -> None:
        do_fields = set(inspect.signature(self.__init__).parameters.keys())
        for field in do_fields:
            setattr(self, field, init_args.get(field))


"""
一个远程服务调用的示例：
class AccountServiceInterface(abc.ABC):
    @abc.abstractmethod
    def get_level(self, uid: int) -> Level:
        pass
        
        
class LevelTranslator(object):
    @classmethod
    def construct_level(cls, uid, level_id) -> Level:
        return Level(uid, level_id)
        
        
class LevelAdaptor(object):
    def __init__(self):
        self.http_client = requests
        
    def get_level(self, uid) -> Level:
        response = self.http_client.get(url, data={"uid": uid})
        # should handle http request error
        return LevelTranslator.construct_level(response.json())
        
class AccountServiceImpl(AccountServiceInterface):
    def get_level(self, uid: int) -> Level:
        adaptor = LevelAdaptor()
        return adaptor.get_level()        
"""
