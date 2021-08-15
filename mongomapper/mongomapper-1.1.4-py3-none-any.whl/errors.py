from typing import Optional
from .base import BaseSchema

class DocumentNotFoundError(Exception):
  model:  BaseSchema
  filter: dict

  def __init__(self, model: BaseSchema, filter: Optional[dict] = {}):
    super().__init__(model, filter)

    self.model  = model
    self.filter = filter