import json
from typing import List, Optional
from pydantic import validator
from pydantic.main import BaseModel

class TestInputRow(BaseModel):
    data: str
    id: int
    raw_id: Optional[int] = -1

    @validator('data')
    def data_must_be_valid_json(cls, v):
        try:
            json.loads(v)
        except:
            raise ValueError('data must be a valid json string')
        return v

class TestInputRequest(BaseModel):
    truth_dataset_id: int = -1
    model_type_id: int = -1
    rows: List[TestInputRow]
