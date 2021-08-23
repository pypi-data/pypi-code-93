class CraftAiError(Exception):
    """Base class for exceptions in the craft ai client."""

    def __init__(self, message=None, metadata=None):
        self.message = message
        self.metadata = metadata
        super(CraftAiError, self).__init__(message, metadata)

    def __str__(self):
        return repr(self.message)


class CraftAiUnknownError(CraftAiError):
    """An unknown error occured in the craft ai client."""


class CraftAiNetworkError(CraftAiError):
    """A network error occured between the client and craft ai."""


class CraftAiCredentialsError(CraftAiError):
    """A credentials error occured."""


class CraftAiInternalError(CraftAiError):
    """An Internal Server Error (500) ocurred on craft ai's side."""


class CraftAiBadRequestError(CraftAiError):
    """An unvalid request was send to craft ai's API."""


class CraftAiNotFoundError(CraftAiError):
    """A Not Found Error (404) occured on craft ai's side."""


class CraftAiDecisionError(CraftAiError):
    """An error occured during the decision phase."""


class CraftAiNullDecisionError(CraftAiDecisionError):
    """An error occured during the decision phase."""


class CraftAiTimeError(CraftAiError):
    """An error occured during the creation of a craft_ai.Time instance."""


class CraftAiTokenError(CraftAiError):
    """An invalid token error occured."""


class CraftAiLongRequestTimeOutError(CraftAiError):
    """Request timed out because the computation is not finished, please try again."""
