from ._base_definition import BaseDefinition
from refinitiv.dataplatform.content.esg.data_type import DataType


class Definition(BaseDefinition):
    def __init__(self, universe, start=None, end=None, closure=None):
        super().__init__(universe=universe, start=start, end=end, closure=closure)
        self._data_type = DataType.StandardScores
