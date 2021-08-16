from functools import wraps
from rest_framework.exceptions import ParseError, UnsupportedMediaType, MethodNotAllowed, NotAcceptable
from rest_framework.serializers import ValidationError

from ..exceptions import apis as apiexp


def serializer_validation(func):
    @wraps(func)
    def inner(self, request, *args, **kwargs):
        try:
            return func(self, request, *args, **kwargs)
        except ParseError as e:
            raise apiexp.ParseErrorExp(e.default_detail)
        except ValidationError as e:
            raise apiexp.ValidationErrorExp(e.detail)
        except UnsupportedMediaType as e:
            raise apiexp.UnsupportedMediaExp(e.default_detail)
        except MethodNotAllowed as e:
            raise apiexp.MethodNotAllowedExp(e.default_detail)
        except NotAcceptable as e:
            raise apiexp.NotAcceptableExp(e.default_detail)
    return inner
