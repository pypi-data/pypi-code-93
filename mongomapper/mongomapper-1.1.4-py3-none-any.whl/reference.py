from bson.objectid import ObjectId
from typing import Type
from .base import BaseSchema

def Reference(type):
  class _Reference(ObjectId):
    __schema__: Type[BaseSchema] = type

    @property
    def document(self):
      return self.__schema__.get(self)

    def __repr__(self):
      return f'Reference<{self.__schema__.__name__}>("{self}")'

    @classmethod
    def __get_validators__(cls):
      yield cls.validate
    
    @classmethod
    def validate(cls, v):
      if isinstance(v, BaseSchema):
        v = v._id
      
      return cls(v)
  
  return _Reference