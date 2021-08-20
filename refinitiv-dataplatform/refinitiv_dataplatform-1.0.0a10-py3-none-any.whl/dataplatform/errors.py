# coding: utf-8

__all__ = [
    "RDPError",
    "SessionError",
    "PlatformSessionError",
    "DesktopSessionError",
    "EndpointError",
    "StreamError",
    "StreamingError",
    "StreamConnectionError",
    "EnvError",
    "RequiredError",
    "StreamingPricesError",
    "ESGError",
    "NewsHeadlinesError",
    "BondPricingError",
    "FinancialContractsError",
]


class RDPError(Exception):
    """Base class for exceptions in this module.

    :param code:
    :param message: description
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return f"Error code {self.code} | {self.message}"


class SessionError(RDPError):
    pass


class StreamingError(RDPError):
    pass


class StreamConnectionError(RDPError):
    pass


class PlatformSessionError(SessionError):
    pass


class DesktopSessionError(SessionError):
    pass


class ESGError(RDPError):
    pass


class NewsHeadlinesError(RDPError):
    pass


class EndpointError(RDPError):
    pass


class StreamError(RDPError):
    pass


class StreamingPricesError(RDPError):
    pass


class EnvError(RDPError):
    pass


class BondPricingError(RDPError):
    pass


class FinancialContractsError(RDPError):
    pass


class RequiredError(RDPError):
    pass
