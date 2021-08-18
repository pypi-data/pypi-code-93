from json import JSONDecodeError

import requests

from assembly_payments.exceptions import PyAssemblyPaymentsNotImplementedException, PyAssemblyPaymentsBadRequest, \
    PyAssemblyPaymentsUnprocessableEntity, PyAssemblyPaymentsForbidden, PyAssemblyPaymentsNotFound, \
    PyAssemblyPaymentsConflict


class BaseService:
    GET = 'get'
    POST = 'post'
    PATCH = 'patch'
    DELETE = 'delete'

    def __init__(self, get_auth=None, base_url=None, auth_url=None, beta_url=None, logging=False):
        self.get_auth = get_auth
        self.endpoint = None
        self.base_url = base_url
        self.auth_url = auth_url
        self.beta_url = beta_url
        self.logging = logging

    def _execute(self, method, endpoint, data=None, headers=None, url=None):
        if headers is None:
            headers = dict(
                Authorization=f"Bearer {self.get_auth()}"
            )

        if url is None:
            url = self.base_url

        response = getattr(requests, method)(f"{url}{endpoint}", json=data, headers=headers)

        if self.logging:
            print(method.upper(), endpoint, response.status_code, response.text)

        self._handle_exceptions(response)
        if response.content:
            return response.json()
        return

    def _handle_exceptions(self, response):
        exc_classes = {
            400: PyAssemblyPaymentsBadRequest,
            403: PyAssemblyPaymentsForbidden,
            404: PyAssemblyPaymentsNotFound,
            409: PyAssemblyPaymentsConflict,
            422: PyAssemblyPaymentsUnprocessableEntity,
        }

        exc_class = exc_classes.get(response.status_code)
        if exc_class:
            try:
                data = response.json()
            except JSONDecodeError:
                data = response.text
            raise exc_class(data)

    def list(self, *args, **kwargs):
        raise PyAssemblyPaymentsNotImplementedException(f"{self.__class__} does not implement list. Please raise an issue or PR if you'd like it implemented.")

    def get(self, *args, **kwargs):
        raise PyAssemblyPaymentsNotImplementedException(f"{self.__class__} does not implement get. Please raise an issue or PR if you'd like it implemented.")

    def create(self, **kwargs):
        raise PyAssemblyPaymentsNotImplementedException(f"{self.__class__} does not implement create. Please raise an issue or PR if you'd like it implemented.")

    def update(self, **kwargs):
        raise PyAssemblyPaymentsNotImplementedException(f"{self.__class__} does not implement update. Please raise an issue or PR if you'd like it implemented.")

    def delete(self, *args, **kwargs):
        raise PyAssemblyPaymentsNotImplementedException(f"{self.__class__} does not implement delete. Please raise an issue or PR if you'd like it implemented.")
