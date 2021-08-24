
"""
Financefeast Client Library exceptions
"""

class NotAuthorised(Exception):
    """
    Raises an Not Authorised exception for a 403 HTTP response from the API
    """


class RateLimitExceeded(Exception):
    """
    Rate Limit exceeded
    """
    super(Exception)

class MissingClientId(Exception):
    """
    Missing client_id
    """
    def __init__(self, message):
        self.message = message

class MissingClientSecret(Exception):
    """
    Missing client_secret
    """
    def __init__(self, message):
        self.message = message

class MissingTicker(Exception):
    """
    Ticker not passed to method
    """
    pass
