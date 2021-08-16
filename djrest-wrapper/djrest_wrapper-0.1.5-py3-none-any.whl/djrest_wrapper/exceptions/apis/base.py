from django.utils.translation import gettext_lazy as _
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.exceptions import _get_codes, _get_error_details, _get_full_details


class APIException(Exception):
    status_code = HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('A server error occurred.')
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        super().__init__()
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        self.detail = _get_error_details(detail, code)

    def __str__(self):
        return str(self.detail)

    def get_codes(self):
        return _get_codes(self.detail)

    def get_full_details(self):
        return _get_full_details(self.detail)


class BaseApiExp(APIException):
    err_code = 0
    default_code = ''
