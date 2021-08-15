from pymongo import MongoClient
from bson.objectid import ObjectId
from pydantic import BaseModel, PrivateAttr

from .utils import classproperty
from .config import config

client = MongoClient(f'mongodb+srv://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}/{config.DB_NAME}?retryWrites=true&w=majority')
db = client.get_database(config.DB_NAME)

class BaseSchema(BaseModel):
  __collection_name__: str
  
  _id: ObjectId = PrivateAttr(default_factory=ObjectId)
  
  def __init__(self, **data):
    super().__init__(**data)
    
    if '_id' in data:
      self._id = data['_id']

  @property
  def data(self):
    return self.dict()
  
  def dict(self, *args, **kwargs):
    return {'_id': self._id} | super().dict(*args, **kwargs)
  
  def save(self):
    filter = {'_id': self._id}
    data = {'$set': self.dict()}
    self.collection.update_one(filter, data)
  
  def delete(self):
    filter = {'_id': self._id}
    self.collection.delete_one(filter)

  @classproperty
  def collection(cls):
    return db.get_collection(cls.__collection_name__)

  @classmethod
  def create(cls, **data):
    doc = cls(**data)
    cls.collection.insert_one(doc.data)
    return doc