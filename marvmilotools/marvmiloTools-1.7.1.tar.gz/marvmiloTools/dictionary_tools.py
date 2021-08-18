import json
import copy
 
class DictObject():
    def __init__(self, instance):
        if not isinstance(instance, dict):
            raise TypeError("No dictionary")
        else:
            self.__current__ = 0
            for key in instance:
                if isinstance(instance[key], dict):
                    self.__dict__[key] = DictObject(instance[key])
                else:
                    self.__dict__[key] = toObj(instance[key])
    
    def __str__(self):
        return str(self.toDict())
    __repr__ = __str__
    def __iter__(self):
        return self
    def __next__(self):
        try:
            val = [key for key in list(self.__dict__.keys()) if not key == "__current__"][self.__current__]
            self.__current__ += 1
            return val
        except IndexError:
            raise StopIteration
    def __len__(self):
        return(len(self.__dict__)-1)
    def __getitem__(self, item):
        return self.__dict__[item]
    def __setitem__(self, item, value):
        self.__dict__[item] = value
    def __delitem__(self, item):
        del self.__dict__[item]
    
    def get(self, item):
        return self.__dict__[item]
    def keys(self):
        return {k:v for k,v in self.__dict__.items() if not k == "__current__"}.keys()
    def values(self):
        return {k:v for k,v in self.__dict__.items() if not k == "__current__"}.values()
    def items(self):
        return {k:v for k,v in self.__dict__.items() if not k == "__current__"}.items()
    def update(self, dictionary):
        self.__dict__.update(dictionary)
    def pop(self, item):
        self.__dict__.pop(item)
    def popitem(self):
        self.__dict__.popitem()
    def clear(self):
        self.__dict__.clear()
    def copy(self):
        return copy.copy(self)
 
    #pretty print Dict
    def pretty(self):
        return json.dumps(self.toDict(), indent=4)
    
    #convert back to dict
    def toDict(self):
        return toDict(self)
 
#convert dictionary to object
def toObj(instance):    
    if isinstance(instance, dict):
        return DictObject(instance)
    
    elif isinstance(instance, str):
        return instance
    
    else: 
        try:
            for i, item in enumerate(instance):
                if isinstance(item, dict):
                    instance[i] = DictObject(item)
                else:
                    instance[i] = toObj(item)
            return instance
        except TypeError:
            return instance
 
#convert back to dictionary
def toDict(obj):
    if isinstance(obj, DictObject):
        return {k:toDict(v) for k,v in obj.items() if not k == "__current__"}
    elif isinstance(obj, list):
        return [toDict(v) for v in obj]
    else:
        return obj