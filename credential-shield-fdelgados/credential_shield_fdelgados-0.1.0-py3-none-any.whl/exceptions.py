class CredentialShieldException(RuntimeError):
    pass


class InvalidTokenFormatException(CredentialShieldException):
    def __init__(self) -> None:
        super().__init__('Token format is incorrect')


class InvalidApplicationIdException(CredentialShieldException):
    def __init__(self) -> None:
        super().__init__('Invalid application id')


class InvalidTokenSourceException(CredentialShieldException):
    def __init__(self) -> None:
        super().__init__('Token issuer is not trusted')


class InvalidAccessTokenException(CredentialShieldException):
    def __init__(self) -> None:
        super().__init__('Invalid access token')


class ExpiredTokenException(CredentialShieldException):
    def __init__(self) -> None:
        super().__init__('Token has expired')


class ScopeNotAllowedException(CredentialShieldException):
    def __init__(self) -> None:
        super().__init__('Token issuer is not trusted')
