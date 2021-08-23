import json

from collections import namedtuple
from functools import wraps

from requests import Response
from requests import Session

from . import exceptions

# TODO API_CONFIG
# TODO CLIENT_CONFIG
ResponseObject = namedtuple("ResponseObject",
                            ["success", "data", "code", "messages"])


def handle_response(func):
    @wraps(func)
    def func_wrapper(self, *args, **kwargs):
        response = func(self, *args, **kwargs)
        return self.resolve(response)

    return func_wrapper


class RequestSession:
    def __init__(self, ip, connect_timeout=15, read_timeout=10):
        self.ip_address = ip
        self._connect_key = "Moku-Client-Key"
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self._session = Session()

    def _update_session(self, key):
        if key:
            self._session.headers.update({self._connect_key: key})

    def _get_url(self, group, operation):
        return f'http://{self.ip_address}/api/{group}/{operation}'

    @handle_response
    def get(self, group, operation, **kwargs):
        return self._session.get(self._get_url(group, operation),
                                 timeout=(
                                     self.connect_timeout, self.read_timeout),
                                 **kwargs)

    @handle_response
    def post(self, group, operation, params=None, **kwargs):
        if operation == 'get_data':
            read_timeout = self.read_timeout + int(params.get('timeout', 0))
        else:
            read_timeout = self.read_timeout
        return self._session.post(self._get_url(group, operation), json=params,
                                  timeout=(
                                      self.connect_timeout, read_timeout),
                                  headers={'Content-type': 'application/json'},
                                  **kwargs)

    def get_file(self, group, operation, local_path):
        with self._session.get(self._get_url(group, operation),
                               stream=True) as r:
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    @handle_response
    def post_file(self, group, operation, data):
        return self._session.post(self._get_url(group, operation),
                                  data=data,
                                  timeout=(
                                      self.connect_timeout, self.read_timeout)
                                  )

    @handle_response
    def delete_file(self, group, operation):
        return self._session.delete(self._get_url(group, operation),
                                    timeout=(
                                        self.connect_timeout,
                                        self.read_timeout)
                                    )

    @staticmethod
    def handle_http_error(response):
        if response.status_code == 500:
            raise exceptions.MokuException(
                "Unhandled error received from Moku.")
        if response.status_code == 400:
            raise exceptions.OperationNotFound(
                "Method not found. Make sure python_moku_sdk is compatible "
                "with the firmware version running")
        else:
            raise exceptions.MokuException(
                f"Unknown exception. Status code:{response.status_code}")

    @staticmethod
    def handle_error(code, messages):
        if code == "NO_PLATFORM_BIT_STREAM":
            raise exceptions.NoPlatformBitstream(messages)
        elif code == "NO_BIT_STREAM":
            raise exceptions.NoInstrumentBitstream(messages)
        elif code == "INVALID_PARAM":
            raise exceptions.InvalidParameterException(messages)
        elif code == "INVALID_REQUEST":
            raise exceptions.InvalidRequestException(messages)
        elif code == "NETWORK_ERROR":
            raise exceptions.NetworkError(messages)
        elif code == "UNEXPECTED_CHANGE":
            raise exceptions.UnexpectedChangeError(messages)
        else:
            raise exceptions.MokuException(messages)

    @staticmethod
    def echo_warnings(messages):
        if messages:
            print("\nWarning: ".join(messages))

    @staticmethod
    def _normalize_nan_inf(arg):
        return {"-inf": -float("inf"),
                "inf": float("inf"),
                "nan": float("nan")}[arg]

    def _check_and_normalize_nan_inf(self, content):
        try:
            return json.loads(content)
        except json.decoder.JSONDecodeError:
            content = content.replace('nan', '"nan"')
            content = content.replace('inf', '"inf"')
            return json.loads(content, parse_constant=self._normalize_nan_inf)

    def resolve(self, response: Response):
        def _parse_to_object(content):
            content = content.decode("utf-8")
            content = self._check_and_normalize_nan_inf(content)
            return ResponseObject(
                success=content['success'],
                data=content['data'],
                code=content['code'],
                messages=content['messages']
            )

        self._update_session(response.headers.get(self._connect_key))
        if response is not None:
            if response.status_code == 200:
                data = _parse_to_object(response.content)
                if data.success is True:
                    self.echo_warnings(data.messages)
                    return data.data
                elif data.success is False:
                    self.handle_error(data.code, data.messages)
            else:
                self.handle_http_error(response)
        else:
            raise Exception('Response object empty')
