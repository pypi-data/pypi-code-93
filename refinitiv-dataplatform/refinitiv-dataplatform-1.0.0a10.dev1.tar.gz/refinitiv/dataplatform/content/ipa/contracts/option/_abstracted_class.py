# coding: utf-8

import abc
import enum
from refinitiv.dataplatform.content.ipa.instrument._definition import ObjectDefinition


class BarrierDefinition(ObjectDefinition, abc.ABC):
    def __init__(self):
        super().__init__()


class BinaryDefinition(ObjectDefinition, abc.ABC):
    def __init__(self):
        super().__init__()


class FixingInfo(ObjectDefinition, abc.ABC):
    def __init__(self):
        super().__init__()


class BinaryType(enum.Enum):
    pass
