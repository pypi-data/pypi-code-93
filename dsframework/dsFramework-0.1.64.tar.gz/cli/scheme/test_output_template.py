import json
from typing import List, Optional

from pydantic import validator, Extra
from pydantic.main import BaseModel

class TestOutputRow(BaseModel):
    data: str
    id: int
    raw_id: Optional[int] = -1

class TestOutputResponse(BaseModel):
    truth_id: int
    truth_dataset_id: int
    model_type_id: int
    raw_id: int = -1
    pred: str
    target: str
    text: str = ''

    @validator('pred')
    def pred_must_be_valid_json(cls, v):
        try:
            json.loads(v)
        except:
            raise ValueError('pred must be a valid json string')
        return v

    @validator('target')
    def target_must_be_valid_json(cls, v):
        try:
            json.loads(v)
        except:
            raise ValueError('target must be a valid json string')
        return v

    class Config:
        extra = Extra.allow
