#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>

"""
import asyncio

import httpx
from cdumay_http_client.client import HttpClient


async def request_wrapper(**kwargs):
    # we remve streaming, not supported yet!
    kwargs.pop('stream')

    async with httpx.AsyncClient(verify=kwargs.pop('verify')) as client:
        return await client.request(**kwargs)


class AsyncHttpClient(HttpClient):
    """Asynchronous HTTP client"""

    def _request_wrapper(self, **kwargs):
        return asyncio.run(request_wrapper(**kwargs))
