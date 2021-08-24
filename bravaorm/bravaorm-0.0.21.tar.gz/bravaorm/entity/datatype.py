# -*- coding: utf-8 -*-

import decimal
import datetime

class ValidateValue:

    def __init__(self, context=None, keyname=None, pk=False, auto_increment=False, fk=False, not_null=False, required=False, max=None, name=None, type=None, format=None, precision=None, scale=None, key=None, reference=None, table=None, intermediate=None, rel_key=None, ref_key=None):
        self.pk = pk
        self.fk = fk
        self.required = required
        self.max = max
        self.name = name
        if name:
            self.type = getattr(__import__(f'model.{name.lower()}', fromlist=[name]), name)
        else:
            self.type = None
        self.auto_increment = auto_increment
        self.not_null = not_null
        self.precision = precision
        self.scale = scale
        self.format = format
        self.key = key
        self.reference = reference
        self.table = table
        self.intermediate = intermediate
        self.rel_key = rel_key
        self.ref_key = ref_key
        self.context = context
        self.keyname = keyname
        self._value = None if not self.__class__ or not 'List' in self.__class__.__name__ else ListType(self.type, context, keyname)

    def __call__(self, **kw):
        return self.type(**kw)

    def __reset__(self):    
        self._value = None if not self.__class__ or not 'List' in self.__class__.__name__ else ListType(self.type, self.context, self.keyname)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class String(ValidateValue):

    def __init__(self, **attrs):
        super().__init__(**attrs)

    def __setattr__(self, attr, data, check=True):
        if check and attr == "value" and data is not None:
            if not isinstance(data, str):
                raise Exception("requires string")
            if self.max and len(data) > self.max:
                raise Exception(f"Value too large. The default limit is {self.max}")
        super().__setattr__(attr, data)


class Int(ValidateValue):

    def __init__(self, **attrs):
        super().__init__(**attrs)

    def __setattr__(self, attr, data, check=True):
        if check and attr == "value" and data is not None:
            if self.max and len(str(data)) > self.max:
                raise Exception(f"Value too large. The default limit is {self.max}")
            if not isinstance(data, int):
                try:
                    data = int(data)
                except ValueError as e:
                    raise Exception("requires int")
        super().__setattr__(attr, data)


class DateTime(ValidateValue):

    def __init__(self, **attrs):
        super().__init__(**attrs)

    def __setattr__(self, attr, data, check=True):
        if check and attr == "value" and data is not None:
            if not isinstance(data, datetime.datetime):
                try:
                    data = datetime.datetime.strptime(data, self.format)
                except ValueError as e:
                    if "unconverted data remain" not in str(e):
                        raise Exception("is not datetime or string is not correct format")
                    pass
        super().__setattr__(attr, data)


class Decimal(ValidateValue):

    def __init__(self, **attrs):
        super().__init__(**attrs)

    def __setattr__(self, attr, data, check=True):
        if check and attr == "value" and data is not None:
            if not isinstance(data, Decimal):
                try:
                    data = decimal.Decimal(str(round(float(data), self.scale)))
                except ValueError as e:
                    raise Exception("requires Decimal")
        super().__setattr__(attr, data)


class Float(ValidateValue):

    def __init__(self, **attrs):
        super().__init__(**attrs)

    def __setattr__(self, attr, data, check=True):
        if check and attr == "value" and data is not None:
            if not isinstance(data, float):
                try:
                    data = round(float(data), self.scale)
                except ValueError as e:
                    raise Exception("requires Float")
        super().__setattr__(attr, data)


class Boolean(ValidateValue):

    def __init__(self, **attrs):
        super().__init__(**attrs)

    def __setattr__(self, attr, data, check=True):
        if check and attr == "value" and data is not None:
            if not isinstance(data, bool):
                try:
                    data = bool(data)
                except ValueError as e:
                    raise Exception("requires Boolean")
        super().__setattr__(attr, data)


class Dict(ValidateValue):

    def __init__(self, **attrs):
        super().__init__(**attrs)

    def __setattr__(self, attr, data, check=True):
        if check and attr == "value" and data is not None:
            if not isinstance(data, dict):
                raise Exception("requires Dict")
        super().__setattr__(attr, data)


class Obj(ValidateValue):

    def __init__(self, **attrs):
        super().__init__(**attrs)

    def __setattr__(self, attr, data, check=True):
        if check and attr == "value" and data is not None:
            if data.__class__.__name__ != self.type.__name__:
                raise Exception(f"requires {self.type.__name__} object")
        super().__setattr__(attr, data)


class ObjList(ValidateValue):

    def __init__(self, **attrs):
        super().__init__(**attrs)

    def __setattr__(self, attr, data, check=True):
        if check and attr == "value" and data is not None:
            self.value.add(data)
        super().__setattr__(attr, data)


class ObjListOfMany(ValidateValue):

    def __init__(self, **attrs):
        super().__init__(**attrs)

    def __setattr__(self, attr, data, check=True):
        if check and attr == "value" and data is not None:
            self.value.add(data)
        super().__setattr__(attr, data)

class ListType(list):

    def __init__(self, type, _context=None, key=None):
        self._type = type
        self._context = _context
        self._key = key
        super(ListType, self).__init__()

    def append(self, item):
        try:

            if not isinstance(item, set) and not isinstance(item, map) and not isinstance(item, list) and item.__class__.__name__ != self._type.__name__:
                raise Exception(f'Item type not is {self._type.__name__}')

            if self._context and not self._key in self._context.__metadata__['relasionships']:
                self._context.__metadata__['relasionships'][self._key] = []

            if isinstance(item, list):
                super(ListType, self).extend(item)
                if (self._context):
                    self._context.__metadata__['relasionships'][self._key].extend(self.toJSON())
            elif isinstance(item, set) or isinstance(item, map):
                super(ListType, self).extend(list(item))
                if (self._context):
                    self._context.__metadata__['relasionships'][self._key].extend(self.toJSON())
            else:
                super(ListType, self).append(item)
                if (self._context):
                    self._context.__metadata__['relasionships'][self._key].append(item.toJSON())

        except Exception as e:
            raise e
        return self

    def add(self, item):
        self.append(item)
        return self

    def toJSON(self):
        try:
            return [item.toJSON() if hasattr(item, "toJSON") else item for item in self]
        except Exception as e:
            raise e
