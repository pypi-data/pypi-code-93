from pydantic import BaseModel, Field
from typing import List, Optional

from pyrasgo.schemas.column import Column
from pyrasgo.schemas.enums import ModelTypes
from pyrasgo.schemas.feature import Feature


class CollectionBase(BaseModel):
    id: int

class Collection(CollectionBase):
    name: Optional[str]
    authorId: Optional[int]
    dataTableName: Optional[str]
    type: Optional[ModelTypes] = None
    organizationId: Optional[int]
    dimensions: Optional[List[Column]]
    features: Optional[List[Feature]]
    description: Optional[str]
    isShared: Optional[bool]

class CollectionUpdate(BaseModel):
    id: int
    name: Optional[str]