"""Module containing datasets' custom errors."""


__all__ = [
    # Class exports
    'InvalidTimeframeError',
    'OHLCVError',
    'OHLCVFetchError',
    'OHLCVReindexError',
    'UnknownExchangeError',
    'UnknownSymbolError',
    'UnknownTimeframeUnitError',
]


class UnknownExchangeError(ValueError):
    """This error is raised when we don't recognize a given exchange name."""


class UnknownSymbolError(ValueError):
    """This error is raised when we don't recognize a given symbol."""


class UnknownTimeframeUnitError(ValueError):
    """This error is raised when the input timeframe unit is unknown."""


class InvalidTimeframeError(ValueError):
    """This error is raised when the input timeframe is invalid.

    This error is also raised if the `Timeframe` class can't
    automagically extrapolate the values from the input."""


class OHLCVError(Exception):
    """This error is raised for any OHLCV-related functionalities."""


class OHLCVFetchError(OHLCVError):
    """This error is raised when we failed to fetch OHLCV from DB."""


class OHLCVReindexError(OHLCVError):
    """This error is raised when we don't recognize a given exchange name."""
