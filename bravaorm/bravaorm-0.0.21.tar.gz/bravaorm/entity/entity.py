# -*- coding: utf-8 -*-

from bravaorm.entity.datatype import *

__methods__ = ['toJSON', 'load', 'add']

class Entity():

    def __init__(self, aliases=None, context=None, **kw):
        self.__metadata__['data'] = {}
        self.__metadata__['aliases'] = {}
        self.__metadata__['relasionships'] = {}
        self.__context__ = context
        self.load(**kw)
        if aliases:
            for c, k in aliases:
                if not k in self.__metadata__['aliases']:
                    self.__metadata__['aliases'][k] = kw[k]

    def load(self, **kw):
        if len(kw) > 0:
            for k in self.__dict__:
                if not k.startswith("__"):
                    if k in kw:
                        if self[k].__class__.__name__.startswith("Obj"):
                            self.add(k, kw[k])
                        else:
                            self[k].value = kw[k]
                            self.__metadata__['data'][k] = self[k].value
                    elif self[k].__class__.__name__.startswith("Obj"):
                        group_data = {key.replace(f"{k}.",''):value for key, value in kw.items() if key.startswith(f"{k}.")}
                        if len(group_data) > 0:
                            self.add(k, group_data)


    def add(self, key=None, data=None):
        if key and data and (isinstance(data, dict) or isinstance(data, list)):
            if "List" in self[key].__class__.__name__:
                if not key in self.__metadata__['relasionships']:
                    self.__metadata__['relasionships'][key]=[]
                self.__metadata__['relasionships'][key].extend(data if isinstance(data, list) else [data])
                self[key].value.extend([self[key].type(context={'entity':self ,'key':key}, **item) for item in data if any(item.values())] if isinstance(data, list) else [self[key].type(context={'entity':self ,'key':key}, **data)] if any(data.values()) else [])
            else:
                data = data[0] if isinstance(data, list) else data
                if any(data.values()):
                    self.__metadata__['relasionships'][key] = data
                    self[key].value = self[key].type(context={'entity':self ,'key':key} , **data)
        else:
            raise Exception("entity.add requires key and dict of object data")

    def __getitem__(self, field):
        return super().__getattribute__(field) if hasattr(self, field) else self.__metadata__['aliases'][field]

    def __getattribute__(self, field):
        if field.startswith("__") or field in __methods__:
            return super().__getattribute__(field)
        else:
            return super().__getattribute__(field).value

    def __setattr__(self, item, value):
        try:
            if not item.startswith("__") and not "entity.datatype" in str(value.__class__):
                if self[item]:
                    if hasattr(value, '__context__') and not value.__context__:
                        value.__context__ = self
                    self[item].value = value
                    self.__metadata__['data'][item] = self[item].value.toJSON() if hasattr(self[item].value, 'toJSON') else self[item].value
                    if self.__context__:
                        _context = self.__context__['entity']
                        _context_key = self.__context__['key']
                        if isinstance(_context[_context_key].value, list):
                            index = _context[_context_key].value.index(self)
                            _context.__metadata__['relasionships'][_context_key][index] = self.__metadata__['data']
                        else:
                            _context.__metadata__['relasionships'][_context_key] = self.__metadata__['data']
                else:
                    super().__setattr__(item, value)
            else:
                super().__setattr__(item, value)
        except Exception as e:
            raise Exception(f'{item} {e}')

    def toJSON(self):
        try:
            return {**self.__metadata__['data'], **self.__metadata__['relasionships'], **self.__metadata__['aliases']}
        except Exception as e:
            raise e
