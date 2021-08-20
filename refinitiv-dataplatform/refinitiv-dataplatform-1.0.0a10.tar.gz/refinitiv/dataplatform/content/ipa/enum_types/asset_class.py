# coding: utf8
# contract_gen 2020-06-15 10:07:47.550306

__all__ = ["AssetClass"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class AssetClass(Enum):
    FUTURES = "Futures"
    SWAP = "Swap"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(AssetClass, _MAIN_CONSTITUENT_ASSET_CLASS_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _MAIN_CONSTITUENT_ASSET_CLASS_VALUES_IN_LOWER_BY_MAIN_CONSTITUENT_ASSET_CLASS,
            some,
        )


_MAIN_CONSTITUENT_ASSET_CLASS_VALUES = tuple(t.value for t in AssetClass)
_MAIN_CONSTITUENT_ASSET_CLASS_VALUES_IN_LOWER_BY_MAIN_CONSTITUENT_ASSET_CLASS = {
    name.lower(): item for name, item in AssetClass.__members__.items()
}
