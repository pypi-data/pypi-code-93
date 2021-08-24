# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import django
from contrast.extern.webob.headers import ResponseHeaders
from contrast.agent.middlewares.response_wrappers.base_response_wrapper import (
    BaseResponseWrapper,
)


class DjangoResponseWrapper(BaseResponseWrapper):
    def __init__(self, response):
        self._response = response
        self._streaming_cache = None

    @property
    def body(self):
        if self._response.streaming:
            return self._get_streaming_content()
        return self._response.content

    @property
    def headers(self):
        """
        In django, response headers are normalized. The outermost key is the normalized header
        value, and value is a tuple of (original_header_key, header_value). For example:
        {'content-type': ('CoNtEnt-TyPe', 'text/html'), .... }

        Conveniently, we can pass these values into the constructor for webob's ResponseHeaders
        object.

        :return: webob.headers.ResponseHeaders object which conforms to BaseResponseWrapper's
            requirements for this property.
        """
        headers = (
            self._response.headers
            if django.VERSION >= (3, 2)
            else self._response._headers.values()
        )

        return ResponseHeaders(headers)

    @property
    def status_code(self):
        return self._response.status_code

    def _get_streaming_content(self):
        """
        Safely extract the content of a streaming response body. This method guarantees that the
        response body is restored after extraction. Unfortunately, this is likely a performance hit
        to applications streaming large response bodies.

        :return: body of a streaming response as bytes
        """
        if not self._streaming_cache:
            body = b"".join(self._response.streaming_content)
            self._response.streaming_content = [body]
            self._streaming_cache = body
            return self._streaming_cache

        return self._streaming_cache
