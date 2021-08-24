# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending

from typing import Union
from requests_cache import CachedSession, ExpirationTime, CachedResponse
from abc import abstractmethod
from requests import Response
from requests.adapters import HTTPAdapter


class CachedAPI:
    def __init__(self, cache_name):
        # TODO: Setup a database for this
        self.session = CachedSession(backend='memory', cache_name=cache_name, expire_after=-1)
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))

    def get_with_cache_timeout(self, url: str, timeout: ExpirationTime = -1) -> Union[Response, CachedResponse]:
        """
        Make a request with a specified time to cache the response
        :param url: URL to request
        :param timeout: Time to remain cached
        :return: Response or CachedResponse
        """
        if timeout == 0:
            return self.get_bypass_cache(url)
        return self.session.request("get", url, expire_after=timeout, timeout=10)
        # with self.session.request_expire_after(timeout):
        #     return self.session.get(url)

    def get_bypass_cache(self, url: str) -> Response:
        """
        Make a request without using any cached responses
        :param url: URL to request
        :return: Response
        """
        with self.session.cache_disabled():
            return self.session.get(url, timeout=10)

    @abstractmethod
    def handle_query(self, **kwargs) -> dict:
        """
        Handles an incoming query and provides a response
        :param kwargs: keyword arguments as required by APIs
        :return: dict response data
        """
