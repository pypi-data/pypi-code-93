import json
import sys

from openapi_client import ApiException as OpenAPIException
from savvihub.exceptions import SavviHubException


class APIException(SavviHubException):
    error_code = None
    fields = None

    def __init__(self, message, fields=None):
        if self.message is None:
            if message:
                self.message = message

            if fields:
                self.fields = fields
                self.message += ' ('
                for i, field in enumerate(fields):
                    if i > 0:
                        self.message += ', '
                    self.message += field['name']
                    if field['value']:
                        self.message += f': {field["value"]}'
                self.message += ')'

        super().__init__(self.message)

    def __eq__(self, other):
        return self.error_code == other.error_code


class DuplicateAPIException(APIException):
    error_code = 'Duplicate'


class InvalidParametersAPIException(APIException):
    error_code = 'InvalidParameters'


class InvalidTokenAPIException(APIException):
    error_code = 'InvalidToken'
    message = 'Token expired. You should run `savvihub login` first.'


class NotFoundAPIException(APIException):
    error_code = 'NotFound'


class UnexpectedProblemAPIException(APIException):
    error_code = 'UnexpectedProblem'


class NotADirectoryAPIException(APIException):
    error_code = 'NotADirectory'


class NoSuchFileOrDirectoryAPIException(APIException):
    error_code = 'NoSuchFileOrDirectory'


class K8SUnauthorizedAPIException(APIException):
    error_code = 'K8sUnauthorized'


class K8SPermissionDeniedAPIException(APIException):
    error_code = 'K8sPermissionDenied'


class K8STimeoutAPIException(APIException):
    error_code = 'K8sTimeout'


class ConnectionRefusedAPIException(APIException):
    error_code = 'ConnectionRefused'


class InvalidCACertAPIException(APIException):
    error_code = 'InvalidCACert'


class NetworkTimeoutAPIException(APIException):
    error_code = 'NetworkTimeout'


class InvalidCliVersionAPIException(APIException):
    error_code = 'InvalidCliVersion'
    message = 'CLI upgrade required. You should run `pip install --upgrade savvihub`.'


class GitHubNotAuthorizedAPIException(APIException):
    error_code = 'GitHubNotAuthorized'
    message = 'GitHub not connected. Visit https://savvihub.com/settings to connect.'


def inheritors(klass):
    subclasses = []
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.append(child)
                work.append(child)
    return subclasses


def convert_to_savvihub_exception(open_api_exception: OpenAPIException) -> APIException:
    try:
        json_resp = json.loads(open_api_exception.body)
        code = json_resp.get('code')
        message = json_resp.get('message')
        fields = json_resp.get('fields')

        for klass in inheritors(APIException):
            if klass.error_code == code:
                return klass(message, fields)

        return UnexpectedProblemAPIException(message, fields)

    except:
        return UnexpectedProblemAPIException(sys.exc_info()[0])
