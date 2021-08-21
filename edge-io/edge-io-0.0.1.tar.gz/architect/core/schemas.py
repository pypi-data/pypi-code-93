from typing import Optional, Callable

import dacite

from pydantic.dataclasses import dataclass


class BaseDataClass:

    @classmethod
    def from_dict(cls, data):
        return dacite.from_dict(data_class=cls, data=data)


@dataclass
class BaseComponent(BaseDataClass):
    pass
