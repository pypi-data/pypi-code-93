from typing import Callable, List, Mapping, Optional

from pydantic import BaseModel

from igenius_adapters_sdk.entities import query
from igenius_adapters_sdk.tools import utils

QueryResult = List[Mapping]


class ChassisConfig(BaseModel):
    bin_interpolation: Optional[bool] = True
    alias_shortening: Optional[bool] = True


class Chassis(BaseModel):
    query: query.Query
    engine: Callable
    config: Optional[ChassisConfig] = ChassisConfig()

    def do_interpolation(self, result: QueryResult) -> QueryResult:
        try:
            if self.query.bin_interpolation:
                result = utils.bin_interpolation(self.query, result)
        except AttributeError:
            pass
        return result

    def do_alias_restore(self, result: QueryResult) -> QueryResult:
        return utils.restore_original_aliases(self.query, result)

    def do_run(self, result: QueryResult) -> QueryResult:
        if self.config.bin_interpolation:
            result = self.do_interpolation(result)
        if self.config.alias_shortening:
            result = self.do_alias_restore(result)
        return result

    def query_pre_processing(self):
        if self.config.alias_shortening:
            self.query = utils.apply_alias_shortening(self.query)

    async def async_run(self) -> QueryResult:
        self.query_pre_processing()
        result = await self.engine(self.query)
        return self.do_run(result)

    def run(self) -> QueryResult:
        self.query_pre_processing()
        result = self.engine(self.query)
        return self.do_run(result)
