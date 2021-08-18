import os
import pytest
import logging
import requests
import traceback

from collections import namedtuple
from urllib.parse import urlsplit
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from selenium.common.exceptions import WebDriverException

from promium.assertions import (
    WebDriverSoftAssertion,
    RequestSoftAssertion
)
from promium.exceptions import PromiumException
from promium.device_config import CHROME_DESKTOP_1920_1080
from promium.browsers import (
    FirefoxBrowser, ChromeBrowser, OperaBrowser, RemoteBrowser
)
from promium.logger import (
    request_logging,
    logger_for_loading_page
)
from promium.common import upload_screenshot


TEST_PROJECT = os.environ.get('TEST_PROJECT')
TEST_CASE = os.environ.get('TEST_CASE')

log = logging.getLogger(__name__)

DRIVERS = {
    'firefox': 'Firefox',
    'chrome': 'Chrome',
    'safari': 'Safari',
    'opera': 'Opera',
    'ie': 'Ie',
}

MAX_LOAD_TIME = 10


def create_driver(
        device, proxy_server=None, env_var='SE_DRIVER', default='chrome://'
):
    """
    Examples:

        - 'chrome://'
        - 'firefox://'
        - 'opera://'

    """
    driver_options = {
        "device": device,
        "proxy_server": proxy_server,
        "is_headless": (
            True if os.environ.get("HEADLESS") == "Enabled" else False
        ),
    }

    driver_dsn = os.environ.get(env_var) or default

    if not driver_dsn:
        raise RuntimeError(f'Selenium WebDriver is not set in the {env_var} '
                           f'environment variable')
    try:
        scheme, netloc, url, _, _ = urlsplit(driver_dsn)
    except ValueError:
        raise ValueError(f'Invalid url: {driver_dsn}')

    if scheme in DRIVERS:
        if scheme == "chrome":
            return ChromeBrowser(**driver_options)
        elif scheme == "firefox":
            return FirefoxBrowser(device=device)
        elif scheme == "opera":
            return OperaBrowser(device=device)
        else:
            raise ValueError(f'Unknown client specified: {scheme}')

    elif scheme.startswith('http+'):
        proto, _, client = scheme.partition('+')
        if not netloc:
            raise ValueError(f'Network address is not specified: {driver_dsn}')

        if client not in DRIVERS:
            raise ValueError(f'Unknown client specified: {client}')

        driver_options["client"] = client
        driver_options["hub"] = f'{proto}://{netloc}{url}'

        try:
            driver = RemoteBrowser(**driver_options)
        except WebDriverException:
            log.warning("Second attempt for remote driver connection.")
            driver = RemoteBrowser(**driver_options)
        except KeyError as e:
            log.warning(str(e))
            if "status" in str(e):
                raise PromiumException(
                    "Session timed out because the browser was idle too long."
                    "Or no free slots for create new session."
                )
            raise
        return driver

    raise ValueError(f'Unknown driver specified: {driver_dsn}')


class TDPException(Exception):

    def __init__(self, *args):
        self.message = (
            "exception caught during execution test data preparing.\n"
            "Look at the original traceback:\n\n%s\n"
            ) % ("".join(traceback.format_exception(*args)))

    def __str__(self):
        return self.message


class TDPHandler:
    """
    TDP - Test Data Preparation
    context manager for handling any exception
    during execution test data preparing.
    We need to raise a specific custom exceptions.
    :example:
    with self.tdp_handler():
        some code
    """

    def __init__(self):
        pass

    def __enter__(self):
        log.info("[TDP] Start test data preparing...")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        log.info("[TDP] Finish test data preparing")
        if exc_type:
            raise TDPException(exc_type, exc_value, exc_tb)
        return


class TestCase(object):
    xrequestid = None
    test_case_url = None
    assertion_errors = None
    proxy_server = None

    def tdp_handler(self):
        """
        Use this context manager for prepare of test data only,
        not for business logic!
        """
        return TDPHandler()

    def get_failed_test_command(self):
        return "Please, add run command in your TestCase class."


class WebDriverTestCase(TestCase, WebDriverSoftAssertion):
    driver = None
    device = CHROME_DESKTOP_1920_1080  # default data
    excluded_browser_console_errors = []

    ALLOWED_HOSTS = []
    SKIPPED_HOSTS = []

    FailInfoSelenium = namedtuple('FailInfoSelenium', [
        'test_type', 'url', 'screenshot', 'test_case', 'run_command', 'txid'
    ])

    @logger_for_loading_page
    def get_url(self, url, cleanup=True):
        self.driver.get(url)
        if cleanup:
            try:
                self.driver.execute_script(
                    'localStorage.clear()'
                )
            except WebDriverException:
                pass
        return url

    def _is_skipped_error(self, error):
        for msg in self.excluded_browser_console_errors:
            if msg["msg"] in error and msg["comment"]:
                return True
        return False

    def check_render_errors(self):
        if hasattr(self.driver, "render_errors"):
            if self.driver.render_errors:
                return self.driver.render_errors
        return []

    def check_console_errors(self):
        if hasattr(self.driver, "console_errors"):
            if self.driver.console_errors:
                browser_console_errors = self.driver.console_errors
                if self.excluded_browser_console_errors:
                    try:
                        return list(filter(
                            lambda error: not self._is_skipped_error(error),
                            browser_console_errors
                        ))
                    except Exception as e:
                        raise PromiumException(
                            "Please check your excluded errors list. "
                            "Original exception is: %s" % e
                        )
                return browser_console_errors
        return []

    def setup_method(self, method):
        self.assertion_errors = []
        pytest.config.get_fail_debug = self.get_fail_debug
        pytest.config.assertion_errors = self.assertion_errors
        pytest.config.check_console_errors = self.check_console_errors
        pytest.config.get_screenshot_png = self.get_screenshot_png
        pytest.config.check_render_errors = self.check_render_errors

        if hasattr(self, 'pytestmark') and [
            m.args[0] for m in self.pytestmark if m.name == "device"
        ]:
            dev = [m.args[0] for m in self.pytestmark if m.name == "device"]
            if dev:
                self.device = dev[0]
        elif hasattr(method, 'pytestmark') and [
            m.args[0] for m in method.pytestmark if m.name == "device"
        ]:
            dev = [m.args[0] for m in method.pytestmark if m.name == "device"]
            if dev:
                self.device = dev[0]

        self.driver = create_driver(
            self.device, proxy_server=self.proxy_server
        )
        self.driver.xrequestid = self.xrequestid
        self.driver.console_errors = []
        self.driver.render_errors = []

    def teardown_method(self, method):

        self.xrequestid = None
        self.driver.console_errors = []
        self.driver.render_errors = []
        if self.driver:
            self.driver.xrequestid = None
            try:
                self.driver.quit()
            except WebDriverException as e:
                log.error(
                    "[PROMIUM] Original webdriver exception: %s" % e
                )
        if TEST_CASE == "True" and not self.test_case_url:
            raise PromiumException("Test don't have a test case url.")

    def get_screenshot_png(self):
        return self.driver.get_screenshot_as_png()

    def get_fail_debug(self):
        """Failed test report generator"""
        self.path_to_test = pytest.config.path_to_test

        alerts = 0
        try:
            while self.driver.switch_to.alert:
                alert = self.driver.switch_to.alert
                print('Unexpected ALERT: %s\n' % alert.text)
                alerts += 1
                alert.dismiss()
        except Exception:
            if alerts != 0:
                print('')
            pass
        url = self.driver.current_url
        screenshot = upload_screenshot(self.driver)
        return self.FailInfoSelenium(
            test_type='selenium',
            url=(url, [None])[0],
            screenshot=(screenshot, [None])[0],
            test_case=(self.test_case_url, [None])[0],
            run_command=(self.get_failed_test_command(), [None])[0],
            txid=(self.xrequestid, [None])[0],
        )


class RequestTestCase(TestCase, RequestSoftAssertion):
    session = None
    proxies = {}

    FailInfoRequest = namedtuple(
        'FailInfoRequest',
        [
            'test_type',
            'url',
            'test_case',
            'status_code',
            'run_command',
            'txid'
        ]
    )

    def setup_method(self, method):
        self.session = requests.session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[502, 503, 504],
            method_whitelist=["POST", "GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.url = (
            'Use self.get_response(url) for request tests or '
            'util methods for api tests!'
        )
        self.assertion_errors = []
        pytest.config.assertion_errors = self.assertion_errors
        pytest.config.get_fail_debug = self.get_fail_debug

    def teardown_method(self, method):

        if self.session:
            self.session.close()

        if TEST_CASE == "True" and not self.test_case_url:
            raise PromiumException("Test don't have a test case url.")

        self.xrequestid = None

    def get_fail_debug(self):
        self.path_to_test = pytest.config.path_to_test
        if not hasattr(self.session, 'status_code'):
            self.session.status_code = None

        """Failed test report generator"""
        return self.FailInfoRequest(
            test_type='request',
            url=(self.session.url, [None])[0],
            test_case=(self.test_case_url, [None])[0],
            status_code=(self.session.status_code, [None])[0],
            run_command=(self.get_failed_test_command(), [None])[0],
            txid=(self.xrequestid, [None])[0],
        )

    def get_response(
        self, url, method="GET", timeout=10, cookies=None, **kwargs
    ):
        self.session.url = url
        self.session.status_code = None
        request_cookies = {'xrequestid': self.xrequestid}
        if cookies:
            request_cookies.update(cookies)
        response = self.session.request(
            method=method,
            url=url,
            timeout=timeout,
            verify=False,
            cookies=request_cookies,
            hooks=dict(response=request_logging),
            **kwargs,
        )
        self.session.status_code = response.status_code
        return response
