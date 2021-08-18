
class TelegraphException(Exception):
    pass


class TokenRequired(TelegraphException):
    pass


class UnavailableTag(TelegraphException):
    pass


class NotAllowedTag(TelegraphException):
    pass


class InvalidHTML(TelegraphException):
    pass