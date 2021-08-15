from pydantic import BaseModel
import json


class Base(BaseModel):
    @classmethod
    def load(cls, data):
        if type(data) is dict:
            return cls(**data)
        loaded = json.loads(data.decode())
        return cls(**loaded)

    def dump(self):
        return self.json().encode()
