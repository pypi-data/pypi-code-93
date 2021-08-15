from bson.objectid import ObjectId
from bson.codec_options import TypeRegistry, CodecOptions

from .utils import classproperty

from .base import BaseSchema, db
from .reference import Reference
from .query import Query

from .encoders import DateEncoder

type_registry = TypeRegistry([DateEncoder()])

class Schema(BaseSchema):
  @classproperty
  def collection(cls):
    return db.get_collection(cls.__collection_name__, codec_options=CodecOptions(type_registry=type_registry))

  @property
  def reference(self):
    return Reference(self.__class__)(self._id)

  @classproperty
  def query(cls):
    return Query(model=cls)

  @classmethod
  def all(cls, **filter):
    return cls.query.where(**filter).find()

  @classmethod
  def get(cls, document_id, **filter):
    return cls.query.where(_id=ObjectId(document_id), **filter).find_one()

  class Config:
    json_encoders = {
      ObjectId: lambda oid: str(oid),
      Reference: lambda ref: str(ref)
    }

# DEPRECATED aliases
Schema.list = Schema.all