# -*- coding: utf-8 -*-

# 描述符基类,用于类型检查


class Typed(object):

    def __init__(self, name, expected_type):
        self.name = name
        self.expected_type = expected_type

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError("Expected " + str(self.expected_type))
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        del instance.__dict__[self.name]

# 类装饰器，使用Typed类


def typeassert(**kwargs):
    def decorate(cls):
        for name, expected_type in kwargs.items():
            # 将名字name和期望类型创建一个Typed实例
            iTyped = Typed(name, expected_type)
            # 将名字name和iType，设置到cls中，作为对应cls.__dict__中的key，value
            setattr(cls, name, iTyped)
        return cls
    return decorate


class JSONObject:
    def __init__(self, d):
        self.__dict__ = d
        