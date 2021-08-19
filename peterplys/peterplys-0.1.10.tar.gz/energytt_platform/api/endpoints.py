from serpyco import Serializer
from abc import abstractmethod
from typing import Optional, Any
from inspect import getfullargspec
from functools import cached_property


class Endpoint(object):
    """
    Represents a single HTTP API endpoint.
    """

    # Request and response schemas (dataclasses or None)
    Request = None
    Response = None

    @cached_property
    def request_serializer(self) -> Optional[Serializer]:
        """
        Returns serpyco Serializer for request model.
        """
        return self.build_request_serializer() \
            if self.Request is not None \
            else None

    @cached_property
    def response_serializer(self) -> Optional[Serializer]:
        """
        Returns serpyco Serializer for response model.
        """
        return self.build_response_serializer() \
            if self.Response is not None \
            else None

    def build_request_serializer(self) -> Serializer:
        """
        Builds serpyco Serializer for request model.
        """
        return Serializer(self.Request)

    def build_response_serializer(self) -> Serializer:
        """
        Builds serpyco Serializer for response model.
        """
        return Serializer(self.Response)

    @cached_property
    def requires_context(self) -> bool:
        """
        Returns True if handle_request() requires a Context passed as argument.
        """
        return 'context' in getfullargspec(self.handle_request)[0]

    @cached_property
    def should_parse_request_data(self) -> bool:
        """
        Returns True if handle_request() requires an instance of self.Request
        passed as argument.
        """
        return (self.Request is not None
                and 'request' in getfullargspec(self.handle_request)[0])

    @cached_property
    def should_parse_response_object(self) -> bool:
        """
        Returns True if handle_request() requires an instance of self.Request
        passed as argument.
        """
        return self.Response is not None

    @abstractmethod
    def handle_request(self, **kwargs) -> Optional[Any]:
        """
        Handle a HTTP request.
        """
        raise NotImplementedError


class HealthCheck(Endpoint):
    """
    Health check endpoint. Always returns status 200.
    """
    def handle_request(self):
        pass
