class CredentialShieldException(RuntimeError):
    pass


class InvalidTokenFormatException(CredentialShieldException):
    pass


class InvalidApplicationIdException(CredentialShieldException):
    pass


class InvalidTokenSourceException(CredentialShieldException):
    pass


class InvalidAccessTokenException(CredentialShieldException):
    pass


class ExpiredTokenException(CredentialShieldException):
    pass


class ScopeNotAllowedException(CredentialShieldException):
    pass
