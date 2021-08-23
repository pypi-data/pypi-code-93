from typing import NewType, Optional

from pydantic import BaseModel

LocaliseKey = NewType("LocaliseKey", str)


class I18n(BaseModel):
    name: LocaliseKey
    description: Optional[LocaliseKey]
