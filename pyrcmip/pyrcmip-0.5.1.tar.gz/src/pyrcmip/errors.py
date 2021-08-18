"""
Custom errors defined within pyrcmip
"""


class ProtocolConsistencyError(ValueError):
    """
    Inconsistency between input data and the RCMIP protocol
    """


class NoDataForMetricError(ValueError):
    """
    No data available to calculate the given metric
    """
