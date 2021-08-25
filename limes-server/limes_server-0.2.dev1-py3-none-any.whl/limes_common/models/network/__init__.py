from __future__ import annotations
import inspect
from json.decoder import JSONDecodeError

from typing import Callable, TypeVar, Union, Any
from requests import Response as py_Response
import json

from limes_common.models.basic import AbbreviatedEnum, AdvancedEnum


T = TypeVar('T')
U = TypeVar('U')
Primitive = Union[str, int, float, bool, list['Primitive'], dict[str, 'Primitive']]

def _tryParse(constr: Callable[[T], U], data: dict[str, T], key: str, default: U) -> U:
    val = data.get(key)
    if val:
        return constr(val)
    else:
        return default

class PublicModel:
    def __init__(self, res: py_Response) -> None:
        self.Code = res.status_code
        self.data: dict = json.loads(res.text) if self.Code==200 else {}

class SerializableTypes:
    # all need to be strict uppercase for Parse to work
    STR = str, ''
    INT = int, 0
    BOOL = bool, False
    FLOAT = float, 0.0

    __typesMap = {}

    @classmethod
    def _members(cls) -> list[dict[str, Callable[[str], Any]]]:
        def makeSafeConstr(fn, default: T) -> Callable[[str], T]:
            def safeConstr(x: str) -> T:
                try:
                    return fn(x)
                except ValueError:
                    return default
            return safeConstr

        def get(c: type):
            allMap = SerializableTypes.__typesMap
            m = allMap.get(c, None)
            if m == None:
                d = {}
                for constr, default in [i[1] for i in filter(lambda i: i[0].isupper(), c.__dict__.items())]:
                    d[str(type(default))] = makeSafeConstr(constr, default)
                allMap[c] = d
                m = d
            return m
        all = []
        for c in inspect.getmro(cls):
            all.append(get(c))
            if c == SerializableTypes: break
        return all

    @classmethod
    def ConstrFromStr(cls, string: str) -> Callable | None:
        for d in cls._members():
            if string in d:
                return d[string]
        return None

    @classmethod
    def ConstrFromType(cls, obj) -> Callable | None:
        string = type(obj)
        return cls.ConstrFromStr(string)


class Model:
    __TYPE = 'L_type'
    __VALUE = 'L_value'

    # INHERITING CLASSES MUST SET DEFAULTS TO ALL CONSTRUCTOR PARAMATERS
    def __init__(self) -> None:
        self._jsonLoadSuccess = False
        self._parsed = False
        self._responseCode = 0
        self._raw = ''

    @classmethod
    def _load(cls, v, typesDict: type[SerializableTypes]):
        if not isinstance(v, dict):
            return None
        TYPE = Model.__TYPE
        VALUE = Model.__VALUE
        if TYPE not in v or VALUE not in v:
            return v

        t = v[TYPE]
        val = v[VALUE]
        loaded = None
        if t == str(list):
            loaded = []
            for i in val:
                loaded.append(cls._load(i, typesDict))
        elif t == str(dict):
            loaded = {}
            for k, innerv in val.items():
                loaded[k] = cls._load(innerv, typesDict)
        else:
            constr = typesDict.ConstrFromStr(t)
            if constr is None: return None
            if constr.__code__.co_argcount == 2:
                loaded = constr(val, typesDict)
            else:
                loaded = constr(val)
        return loaded


    # todo merge with Parse
    @classmethod
    def Load(cls, serialized: bytes | str | dict, typesDict: type[SerializableTypes]=SerializableTypes):
        return cls.Parse(serialized, typesDict)

    @classmethod
    def Parse(cls, serialized: bytes | str | dict | py_Response, typesDict: type[SerializableTypes]=SerializableTypes):
        try:
            model = cls()
        except TypeError:
            raise TypeError('%s inheriting <Model> must have no requred paramaters in constructor' % str(cls))
        try:
            if isinstance(serialized, dict):
                d = serialized
            else:
                if isinstance(serialized, py_Response):
                    model._responseCode = serialized.status_code
                    model._raw = serialized.text
                    serialized = serialized.text
                d = json.loads(serialized)
                model._jsonLoadSuccess = True
        except JSONDecodeError:
            return model

        # found = False
        for k, v in d.items():
            if k.startswith('_'): continue
            model.__setattr__(k, cls._load(v, typesDict))
            # found = True
        # model._parsed = found
        return model

    def _toDict(self, v):
        TYPE = Model.__TYPE
        VALUE = Model.__VALUE
        d = {}
        d[TYPE] = str(type(v))
        if isinstance(v, Model):
            d[VALUE] = v.ToDict()
        elif isinstance(v, list):
            l = []
            for i in v:
                l.append(self._toDict(i))
            d[VALUE] = l
        elif isinstance(v, dict):
            inner = {}
            for k, v in v.items():
                inner[k] = self._toDict(v)
            d[VALUE] = inner
        else:
            d[VALUE] = v
        return d

    def ToDict(self) -> dict:
        d = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'): continue
            d[k] = self._toDict(v)
        return d

class ErrorModel(Model):
    def __init__(self, code: int=0, message: str='') -> None:
        super().__init__()
        self.ErrorCode = code
        self.Message = message