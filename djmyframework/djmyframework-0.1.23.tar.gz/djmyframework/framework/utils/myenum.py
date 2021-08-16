# -*- coding: utf-8 -*-
# @Time    : 2019-10-18 09:50
# @Author  : xzr
# @File    : enum
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 自定枚举类


from collections import OrderedDict
from copy import copy
from functools import lru_cache


class EnumElement(object):
    def __init__(self, value, name=None, other=None):
        self.value = value
        self.name = name
        self.other = other


class EnumT(object):
    """
    枚举 增加 name 属性显示
    """

    def __new__(cls, value, name='', other_attr=None):
        value_type = type(value)
        # assert isinstance(key, (str, int)), '%s not int or str' % key_type
        enum_ele_type = type(
                'EnumElement',
                (value_type, EnumElement),
                {}
        )
        obj = enum_ele_type(value)
        obj.value = value
        if name:
            obj.name = name
        if other_attr:
            obj.other = other_attr
        return obj

    def __repr__(self):
        return 'Enum(%s,%s)' % (self, self.name)


class EnumMeta(type):

    def __new__(metacls, cls_name, bases, classdict):

        enum_class = super().__new__(metacls, cls_name, bases, classdict)
        cls_attrs = enum_class.__dict__
        enum_class._member_map_ = copy(enum_class._member_map_)

        for parent in bases:
            parent_member_map_ = getattr(parent, '_member_map_', None)
            if parent_member_map_ is not None:
                enum_class._member_map_.update(parent_member_map_)

        for k in cls_attrs.keys():
            if k and k[0] != '_':
                if isinstance(cls_attrs[k], (tuple, list)):
                    setattr(enum_class, k, EnumT(*cls_attrs[k]))
                    enum_class._member_map_[cls_attrs[k]] = cls_attrs[k]

        return enum_class

    def __str__(cls):
        return '%s (%s)' % (cls.__name__, ','.join('%s:%s' % (k, v.name) for k, v in cls))

    def __iter__(cls):
        for k, v in cls._member_map_.items():
            yield k, v


class Enum(metaclass=EnumMeta):
    """

    usage:
        >>> class Color(Enum):
        ...     RED = (1, u'红')
        ...     ORANGE = (2, u'橙')
        ...     BULE = (3, u'蓝')
        ...
        >>>
        >>> class Rainbow(Color):
        ...     YELLOW = (4, u'黄')
        ...     GREEN = (5, u'绿')
        ...
        >>> Color
        OrderedDict([(1, Enum(1, '红')), (2, Enum(2, '橙')), (3, Enum(3, '蓝'))])
        >>> Color.RED, Color.RED.name
        (Enum(1, '红'), '红')
        >>> Color(1), Color(1) == Color.RED
        (Enum(1, '红'), True)
        >>> Color.member_list()
        ((1, Enum(1, '红')), (2, Enum(2, '橙')), (3, Enum(3, '蓝')))
        >>> Rainbow(2), Rainbow(2) == 2, Rainbow(2).name
        (Enum(2, '橙'), True, '橙')
        >>> Rainbow.member_list()
        ((1, Enum(1, '红')), (2, Enum(2, '橙')), (3, Enum(3, '蓝')), (4, Enum(4, '黄')), (5, Enum(5, '绿')))

    """

    _member_map_ = OrderedDict()

    def __new__(cls, key):
        return cls._member_map_.get(key, None)

    @classmethod
    @lru_cache()
    def member_list(cls):
        return tuple((k, v.name) for k, v in cls)


if __name__ == '__main__':
    def _(s):
        return s



    class EqualOperator(Enum):
        Equal = 'exact', _('等于')
        NotEqual = 'not_exact', _('等于')


    class NullOperator(Enum):
        NotNull = 'not_null', _('有值')
        IsNull = 'is_null', _('没值')


    class InOperator(Enum):
        In = 'in', _('多选')
        NotIn = 'not_in', _('反选')


    class CharOperator(EqualOperator, NullOperator, InOperator):
        Contain = EnumElement('contains', _('包含'))
        NotContain = 'not_contains', _('不包含')
        IsEmpty = 'is_empty', _('为空')
        NotEmpty = 'not_empty', _('不为空')
        Rlike = 'rlike', _('正则匹配	匹配判断')
        NotRlike = 'not_rlike', _('正则不匹配 匹配判断')




    print(CharOperator.member_list())



    class Color(Enum):
        RED = 1, _('红'), {"asd": 3}
        ORANGE = (2, u'橙')
        BULE = (3, u'蓝')


    class Rainbow(Color):
        YELLOW = (4, u'黄')
        GREEN = (5, u'绿')


    class PAGE(Enum):
        BLACK = (4, u'黑')
        WHITE = (6, u'白')


    class AD_STATUS(Enum):
        CAMPAIGN_STATUS_ENABLE = (1, u'启用')
        CAMPAIGN_STATUS_DISABLE = (2, u'暂停')


    print(type(AD_STATUS), type(AD_STATUS.CAMPAIGN_STATUS_DISABLE))

    for k, v in AD_STATUS:
        print(type(k), type(k.name))
    print(AD_STATUS, list(AD_STATUS))
    print(AD_STATUS.member_list())
    assert AD_STATUS.CAMPAIGN_STATUS_ENABLE == 1
    assert AD_STATUS.CAMPAIGN_STATUS_ENABLE == AD_STATUS(1)
    #
    # print(AD_STATUS, type(AD_STATUS), type(AD_STATUS.CAMPAIGN_STATUS_ENABLE), AD_STATUS.CAMPAIGN_STATUS_ENABLE,
    #       AD_STATUS.CAMPAIGN_STATUS_ENABLE.name, AD_STATUS(23) == AD_STATUS.CAMPAIGN_STATUS_ENABLE)
    # print(Color)
    # import json
    # print(json.dumps(Color.member_list()))
    # print(Color.RED, Color.RED.name)
    # print(Color.RED == 1)
    # print(Color(1), Color(1) == Color.RED)
    # print(Rainbow)
    # print(Rainbow(2), Rainbow(2) == 2, Rainbow(2).name)
    #
    # print(Rainbow.member_list())
    # print(PAGE)
    # print(dir(Color))
    # print(Color.__dict__)
    # print(Rainbow.member_list())
    # print(Rainbow.RED.other)
