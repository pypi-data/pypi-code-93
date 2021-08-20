from enum import Enum, unique

__all__ = ["AssetState", "ASSET_STATE_VALUES"]


@unique
class AssetState(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

    @staticmethod
    def convert_to_str(some):
        result = None
        if isinstance(some, str):
            result = AssetState.normalize(some)
        elif isinstance(some, AssetState):
            result = some.value
        if result:
            return result
        else:
            raise AttributeError(f"Asset state value must be in {ASSET_STATE_VALUES}")

    @staticmethod
    def normalize(some):
        some_lower = some.lower()
        symbol_type = _ASSET_STATE_LOWER.get(some_lower)
        result = ""
        if symbol_type:
            result = symbol_type.value
        return result


ASSET_STATE_VALUES = tuple(t.value for t in AssetState)
_ASSET_STATE_LOWER = {
    name.lower(): item for name, item in AssetState.__members__.items()
}
