import logging
from urllib.parse import quote

import requests
from requests.packages.urllib3.util.retry import Retry  # pylint: disable=import-error
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from inspector.metric import Metric


class TimeoutHTTPAdapter(HTTPAdapter):
    """Mountable timeout adapter for http(s) calls:
    https://github.com/psf/requests/issues/3070#issuecomment-205070203
    """

    DEFAULT_TIMEOUT = 5  # seconds

    def __init__(self, *args, **kwargs):
        if "timeout" in kwargs:
            self.timeout = kwargs.pop("timeout")
        else:
            self.timeout = self.DEFAULT_TIMEOUT
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):  # pylint: disable=arguments-differ
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


class Telemetry:  # pylint: disable=too-few-public-methods
    TIMEOUT = 1.5
    RETRIES = 2
    BASE_URL = "https://telemetry.robocorp.com/metric-v1/"

    def __init__(self, debug=False):
        self.logger = logging.getLogger(__name__)
        self.debug = debug

        try:
            self.session = requests.Session()
            self._set_adapters()
            self._set_hooks()
        except RequestException as exc:
            self.logger.warning("Cannot initialize telemetry: %s", exc)
            self.session = None

    def _set_adapters(self):
        timeout = TimeoutHTTPAdapter(timeout=Telemetry.TIMEOUT)
        self.session.mount("https://", timeout)
        self.session.mount("http://", timeout)

        retry = HTTPAdapter(max_retries=self._retry_strategy())
        self.session.mount("https://", retry)
        self.session.mount("http://", retry)

    def _set_hooks(self):
        # pylint: disable=unused-argument
        def assert_status_hook(response, *args, **kwargs):
            response.raise_for_status()

        self.session.hooks["response"] = [assert_status_hook]

    def _retry_strategy(self) -> Retry:
        return Retry(
            total=self.RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["PUT"],
        )

    def send(self, metric: Metric):
        if self.debug:
            self.logger.info("Suppressing telemetry post: PUT metric: %s", metric)
            return

        if not self.session:
            return

        self.logger.debug("PUT metric: %s", metric)
        url = self.BASE_URL + quote(
            f"{metric.type}/"
            + f"{metric.timestamp}/"
            + f"{metric.instance_id}/"
            + f"{metric.key}/"
            + f"{metric.value}"
        )

        try:
            self.session.put(url)
        except RequestException as error:
            self.logger.warning("Cannot send telemetry: %s", error)
