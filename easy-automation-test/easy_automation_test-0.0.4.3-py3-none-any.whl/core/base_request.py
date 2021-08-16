#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/14
import requests

from ..utils.custom_logging import Logs
from ..utils.setting import setting
from ..utils.exception import ProjectHostNotSet


class RequestBase:
    log = Logs(__name__)

    def __init__(self):
        try:
            self._host = setting.PROJECT_HOST
        except AttributeError:
            raise ProjectHostNotSet
        self._session = requests.session()

    def send(self, method, url, *args, **kwargs):
        if not url.startswith('http'):
            url = ''.join((self._host, url))
        self.log.debug('{} {}'.format(method, url))
        return self._session.request(method, url, *args, **kwargs)

