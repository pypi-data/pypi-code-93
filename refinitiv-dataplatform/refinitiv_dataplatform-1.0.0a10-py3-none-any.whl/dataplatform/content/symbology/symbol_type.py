__all__ = ["SymbolTypes", "SYMBOL_TYPE_VALUES"]

from enum import Enum, unique


@unique
class SymbolTypes(Enum):
    RIC = "RIC"
    ISIN = "IssueISIN"
    CUSIP = "CUSIP"
    SEDOL = "SEDOL"
    Ticker = "TickerSymbol"
    OAPermID = "IssuerOAPermID"
    LipperID = "FundClassLipperID"

    @staticmethod
    def convert_to_str(some):
        result = None
        if isinstance(some, str):
            result = SymbolTypes.normalize(some)
        elif isinstance(some, SymbolTypes):
            result = some.value
        if result:
            return result
        else:
            raise AttributeError(f"Symbol type value must be in {SYMBOL_TYPE_VALUES}")

    @staticmethod
    def normalize(some):
        some_lower = some.lower()
        symbol_type = _SYMBOL_TYPE_VALUES_IN_LOWER_BY_SYMBOL_TYPE.get(some_lower)
        result = ""
        if symbol_type:
            result = symbol_type.value
        return result


SYMBOL_TYPE_VALUES = tuple(t.value for t in SymbolTypes)
_SYMBOL_TYPE_VALUES_IN_LOWER_BY_SYMBOL_TYPE = {
    name.lower(): item for name, item in SymbolTypes.__members__.items()
}
