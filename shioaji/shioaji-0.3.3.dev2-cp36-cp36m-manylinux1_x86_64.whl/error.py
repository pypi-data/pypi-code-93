class BaseError(Exception):
    def __init__(self, code, message):
        formated_mes = "{} : {}".format(code, message)
        super().__init__(formated_mes)
        self.code = code
        self.message = message


class TokenError(BaseError):
    """Raise when token error."""


class SystemMaintenance(BaseError):
    """Raise when system maintenance an error."""
