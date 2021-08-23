"""CRUD operations
"""
from abc import ABC
from abc import abstractmethod


import json

from urllib import parse
from typing import Dict
from typing import Mapping
from typing import Optional

from .typing import JSON
from .typing import GitLabAPIReceivedError
from .endpoints import IEndpoint

# pylint: disable=too-few-public-methods
# pylint: disable=missing-docstring


class _URLAttributes(Dict):
    """URL Attributes set

    This class provides the ability to transform a dictioanry of attribute to a URL compatible string, via the str
    built-in function

    Examples:
          Encode strings, integers and float values
          >>> str(_URLAttributes({'a': 1, 'b':2.0, 'c': 'string'}))
          '?a=1?b=2.0?c=string'

          Encode string values with spaces
          >>> str(_URLAttributes({'a': 'string with spaces'}))
          '?a=string%20with%20spaces'

          Encode complex objects list strings and dictionaries (or anything with implementing __repr__)
          >>> str(_URLAttributes({'a': [1,2], 'c': {1:2}}))
          '?a=%5B1%2C%202%5D?c=%7B1%3A%202%7D'

          Empty attributes does not encode anything
          >>> str(_URLAttributes({}))
          ''
    """
    def __str__(self) -> str:
        """Represent attribute ditionary in URL attribute string form

        Each attribute value will be converted into a string, it is part of the caller responsibility to ensure that
        the str representation of such type is usable as part of URL attribute, when sent to the endpoint
        """
        retval = ''
        for key, value in self.items():
            # convert it to string. A complex type can be converted into string as well. It's API's dependant what
            # values are actually legal, so _URLAttributes responsibility is just to ensure it's encoded
            # Note: repr('foo') -> "'foo'", which is incorrect.
            if not isinstance(value, str):
                value = repr(value)
            quoted_value = parse.quote(value)
            retval += f"?{key}={quoted_value}"
        return retval


class IAPIUpdate(ABC):
    """Gitlab Update interface

    This interface is responsible to perform a read operation against the API endpoint, and update the status of the
    operation on the object.

    At the end of the update() call, it is guaranteed that the status attribute is updated with a the latest
    information obtain by the operation.

    The update opertation will be requested using the path attribute.

    The update call has the responsiblity to transform the attributes in the form of key=value from the API
    documentation, into whatever data is required to communicate with the endpoint.
    e.g. from a dictionary into a serialised JSON structure to be sent via POST.
    """
    @property
    @abstractmethod
    def status(self) -> Optional[JSON]:
        """In a read operation, written read() with the result of the transaction"""
        ...

    @abstractmethod
    def update(self, attributes: Optional[Dict]) -> JSON:
        ...


class IAPICreate(ABC):
    """Gitlab Create interface

    This interface is responsible to perform a read operation against the API endpoint, and update the status of the
    operation on the object.

    At the end of the create() call, it is guaranteed that the status attribute is updated with a the latest
    information obtain by the operation.

    The create opertation will be requested using the path attribute.

    The create call has the responsiblity to transform the attributes in the form of key=value from the API
    documentation, into whatever data is required to communicate with the endpoint.
    e.g. from a dictionary into a serialised JSON structure to be sent via POST.
    """
    @property
    @abstractmethod
    def status(self) -> Optional[JSON]:
        """In a read operation, written read() with the result of the transaction"""
        ...

    @abstractmethod
    def create(self, attributes: Optional[Dict]) -> JSON:
        ...


class IAPIRead(ABC):
    """Gitlab Read interface

    This interface is responsible to perform a read operation against the API endpoint, and update the status of the
    operation on the object.

    At the end of the read() call, it is guaranteed that the status attribute is updated with a the latest
    information obtain by the operation.

    The read opertation will be requested using the path attribute.
    If attributes is not empty, it will be used to format the url.

    The read call has the responsiblity to transform the attributes in the form of key=value from the API
    documentation, into whatever data is required to communicate with the endpoint.
    e.g. from a dictionary into URL parameter syntax to be used with HTTP GET
    """
    @property
    @abstractmethod
    def status(self) -> Optional[JSON]:
        """In a read operation, written read() with the result of the transaction"""
        ...

    @abstractmethod
    def read(self, attributes: Optional[Dict]) -> JSON:
        ...


class APIBase:
    # The only attribute that a implementation class must provide explicitely
    path: str
    status: Optional[JSON] = None

    def __init__(self, endpoint: IEndpoint) -> None:
        self._endpoint = endpoint


class APIRead(APIBase, IAPIRead):
    status: Optional[JSON]
    path: str

    def read(self, attributes: Optional[Dict] = None) -> JSON:
        if attributes is None:
            attributes = _URLAttributes()
        else:
            attributes = _URLAttributes(attributes)

        path = f"{self.path}{attributes}"
        self.status = self._endpoint.read(path)

        if isinstance(self.status, Mapping) and 'error' in self.status:
            raise GitLabAPIReceivedError(self.status['error'], self.status)

        return self.status


class APICreate(APIBase, IAPICreate):
    status: Optional[JSON]
    path: str

    def create(self, attributes: Optional[Dict] = None) -> JSON:
        if attributes is None:
            attributes = {}

        data = json.dumps(attributes)
        self.status = self._endpoint.create(self.path, data)

        return self.status


class APIUpdate(APIBase, IAPIUpdate):
    status: Optional[JSON]
    path: str

    def update(self, attributes: Optional[Dict] = None) -> JSON:
        if attributes is None:
            attributes = {}

        data = json.dumps(attributes)
        self.status = self._endpoint.update(self.path, data)

        return self.status


class APIDelete(APIBase):
    status: Optional[JSON]
    path: str

    def delete(self, data: str) -> None:
        raise NotImplementedError()
