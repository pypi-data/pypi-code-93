# -*- coding: utf-8 -*-
from typing import Dict
import requests
import json
import urllib3
from .others import load_config, add_proxy
from .data_models import ProxyModel, TargetAPI, RequestResponse, ApiClientConfig, LoggerConfig
from .logger_mixin import LoggerMixin
from .constants import KW_LOGGER_CONFIG


class ApiClient(LoggerMixin):
    def __init__(
        self,
        config_file_path: str,
        proxy: ProxyModel = None,
        disable_ssl_warning=True,
        **kwargs
    ) -> None:
        # inherit logger or default logger
        self.set_logger_up(kwargs.get(KW_LOGGER_CONFIG))

        if disable_ssl_warning:
            self.logger.debug('disable InsecureRequestWarning')
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if proxy:
            self.logger.info(f'add proxy {proxy}')
            add_proxy(proxy)
        self.config: ApiClientConfig = load_config(config_file_path)
        self.logger.debug(f'config file -> {self.config}')

    def _remove_allow_duplicated_string(self, key: str):
        while key.startswith('*'):
            key = key[1:]
        return key

    def _make_url_for_get_method(self, url: str, params: Dict) -> str:
        url += '?'
        for k, v in params.items():
            _k = self._remove_allow_duplicated_string(k)
            url += f'{str(_k)}={str(v)}&'
        if url.endswith('&'):
            url = url[0:-1]
        self.logger.debug(f'make url result -> {url}')
        return url

    def make_request(
        self,
        target_name: str,
        headers: Dict = None,
        parameters: Dict = None
    ) -> RequestResponse:
        target: TargetAPI = self.config.config.get(target_name)
        if not target:
            self.logger.error(f'not config for api endpoint -> {target_name}')
            return RequestResponse(message=f"not config for api endpoint {target_name}")

        _url = target.url
        _method = target.method
        _headers = target.header
        _parameters = target.parameters

        # update params
        if headers:
            _headers.update(headers)
            self.logger.debug(f'change request header -> {_headers}')
        if parameters:
            _parameters.update(parameters)
            self.logger.debug(f'change parameters header -> {_parameters}')

        # handle url for method get
        if _method.lower() == 'get':
            _url = self._make_url_for_get_method(_url, _parameters)
            response = requests.get(_url, headers=_headers, verify=False)
        elif _method.lower() == 'post':
            _jdata = json.dumps(_parameters)
            self.logger.debug(f'request body {_jdata}')
            response = requests.post(_url, headers=_headers, verify=False, data=_jdata)
        else:
            raise ValueError('just support get and post')

        self.logger.debug(f'response object {response}')
        try:
            response_data = json.loads(response.text)
        except Exception:
            response_data = None

        if 200 <= response.status_code <= 300:
            return RequestResponse(success=True, data=response_data, code=response.status_code)
        else:
            return RequestResponse(success=False, data=response_data, code=response.status_code)
