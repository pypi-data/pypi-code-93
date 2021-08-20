from enum import Enum, unique

__all__ = ["AssetClass", "ASSET_CLASS_VALUES"]


@unique
class AssetClass(Enum):
    COMMODITIES = "Commodities"
    EQUITY_OR_INDEX_OPTIONS = "EquityOrIndexOptions"
    BOND_AND_STIR_FUTURES_AND_OPTIONS = "BondAndSTIRFuturesAndOptions"
    WARRANTS = "Warrants"
    EQUITIES = "Equities"
    INDICES = "Indices"
    EQUITY_INDEX_FUTURES = "EquityIndexFutures"
    FUNDS = "Funds"
    CERTIFICATES = "Certificates"
    BONDS = "Bonds"
    RESERVE_CONVERTIBLE = "ReverseConvertible"
    MINI_FUTURE = "MiniFuture"
    FX_AND_MONEY = "FXAndMoney"

    @staticmethod
    def convert_to_str(some):
        result = None
        if isinstance(some, str):
            result = AssetClass.normalize(some)
        elif isinstance(some, AssetClass):
            result = some.value
        if result:
            return result
        else:
            raise AttributeError(f"Asset class value must be in {ASSET_CLASS_VALUES}")

    @staticmethod
    def normalize(some):
        some_lower = some.lower()
        symbol_type = _ASSET_CLASS_LOWER.get(some_lower)
        result = ""
        if symbol_type:
            result = symbol_type.value
        return result


ASSET_CLASS_VALUES = tuple(t.value for t in AssetClass)
_ASSET_CLASS_LOWER = {
    name.lower(): item for name, item in AssetClass.__members__.items()
}
