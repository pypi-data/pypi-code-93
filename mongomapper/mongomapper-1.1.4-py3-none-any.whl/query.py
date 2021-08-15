from typing import Optional
from .errors import DocumentNotFoundError

class Query:
  model:      ...
  filter:     dict
  projection: dict
  
  def __init__(self, model, filter: Optional[dict] = {}, projection: Optional[dict] = {}):
    self.model      = model
    self.filter     = filter
    self.projection = projection
  
  def where(self, **filter):
    self.filter = self.filter | filter
    return self
  
  def delete(self):
    return self.model.collection.delete_many(self.filter)
  
  def delete_one(self):
    return self.model.collection.delete_one(self.filter)
  
  def find(self, limit: int = 0, skip: int = 0):
    docs = self.model.collection.find(self.filter, self.projection or None, skip, limit)
    return [self.model(**doc) for doc in docs]
  
  def find_one(self):
    doc = self.model.collection.find_one(self.filter, self.projection or None)

    if doc is None:
      raise DocumentNotFoundError(model=self.model, filter=self.filter)

    return self.model(**doc)

# DEPRECATED aliases
Query.get = Query.find
Query.get_one = Query.find_one