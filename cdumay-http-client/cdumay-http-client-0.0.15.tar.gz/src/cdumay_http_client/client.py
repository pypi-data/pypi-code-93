#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>

"""
import logging
import time

import requests
import requests.exceptions
from cdumay_error import Error
from cdumay_error.types import InternalError
from cdumay_http_client import errors

logger = logging.getLogger(__name__)


class HttpClient(object):
    """HttpClient"""

    def __init__(self, server, timeout=None, headers=None, username=None,
                 password=None, ssl_verify=True, retry_number=None,
                 retry_delay=None):
        self.server = server
        self.timeout = timeout or 10
        self.headers = headers or dict()
        self.auth = (username, password) if username and password else None
        self.ssl_verify = ssl_verify
        self.retry_number = retry_number or 10
        self.retry_delay = retry_delay or 30

    def __repr__(self):
        return 'Connection: %s' % self.server

    def _do_request(self, url, method, headers, timeout=None, params=None,
                    payload=None, stream=False, parse_output=True, **kwargs):
        request_start_time = time.time()
        extra = dict(url=url, server=self.server, method=method)
        try:
            response = self._request_wrapper(
                method=method, url=url, params=params, data=payload,
                auth=self.auth, headers=headers, stream=stream,
                timeout=timeout or self.timeout, verify=self.ssl_verify,
                **kwargs
            )
        except requests.exceptions.RequestException as e:
            raise errors.InternalServerError(
                message=getattr(e, 'message', "Internal Server Error"),
                extra=extra
            )
        finally:
            execution_time = time.time() - request_start_time

        if response is None:
            raise errors.MisdirectedRequest(extra=extra)

        extra.setdefault(
            "request_id", response.headers.get('x-request-id', None)
        )

        content = getattr(response, 'content', "")
        logger.info(
            f"[{method}] - {url} - {response.status_code}: {len(content)} - "
            f"{round(execution_time, 3)}s",
            extra=dict(
                exec_time=execution_time, status_code=response.status_code,
                content_lenght=len(content), **extra
            )
        )
        if response.status_code >= 300:
            raise errors.from_response(response, payload=payload, **extra)

        if parse_output is True:
            return self._parse_response(response)
        else:
            return response

    def _request_wrapper(self, **kwargs):
        return requests.request(**kwargs)

    # noinspection PyMethodMayBeStatic
    def _format_data(self, data):
        return data

    # noinspection PyMethodMayBeStatic
    def _parse_response(self, response):
        return response.text

    def do_request(self, method, path, params=None, data=None, headers=None,
                   timeout=None, parse_output=True, stream=False,
                   no_retry_on=None, **kwargs):
        """Perform request"""
        req_url = ''.join([self.server.rstrip('/'), path])
        req_headers = headers or dict()
        req_headers.update(self.headers)
        payload = self._format_data(data)
        last_error = None
        no_retry_on = no_retry_on or list()

        for req_try in range(1, self.retry_number + 1):
            logger.info(f"[{method}] - {req_url} (try: {req_try})")
            try:
                return self._do_request(
                    url=req_url, method=method, headers=req_headers,
                    timeout=timeout, params=params, payload=payload,
                    stream=stream, parse_output=parse_output, **kwargs
                )
            except Error as err:
                last_error = err
                logger.error(
                    f"[{method}] - {req_url!r} (try: {req_try}) : {err} "
                    f"({err.code})"
                )
                if err.__class__ in no_retry_on:
                    raise err
                time.sleep(self.retry_delay)
        if last_error:
            logger.error(
                f"Failed to perform request {method!r} on {req_url!r} after "
                f"{self.retry_number} retries : {last_error} "
                f"({last_error.code})",
                extra=dict(
                    url=req_url, server=self.server, method=method,
                    status_code=last_error.code,
                    content_lenght=len(last_error.message),
                )
            )
            raise last_error
        else:
            raise InternalError(
                f"Unexcepected error, failed to perform request {method!r} on "
                f"{req_url!r} after {self.retry_number} retries",
                extra=dict(url=req_url, server=self.server, method=method)
            )
