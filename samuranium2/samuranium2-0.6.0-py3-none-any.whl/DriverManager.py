from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from Samuranium import Config, Logger
from Samuranium.utils.general import parse_bool_string_to_bool


class DriverManager:
    def __init__(self, config: Config, logger: Logger, headless=None, agent=None):
        self.logger = logger
        self.config = config
        self.browser_options = self.config.browser_options
        self.headless = self.__get_headless_config(headless_arg=headless)
        self.agent = agent or self.config.agent
        self.options = None

    def __get_headless_config(self, headless_arg):
        if headless_arg is not None:
            return headless_arg
        return parse_bool_string_to_bool(self.browser_options.get('headless', False))

    @property
    def chrome_options(self):
        if not self.options or not self.options.capabilities.get('goog:chromeOptions'):
            return []
        return self.options.capabilities.get('goog:chromeOptions').get('args')

    def get_driver(self) -> webdriver:
        return self.__get_chrome()

    def __get_chrome(self) -> webdriver:
        self.logger.debug('Configuring chrome')
        self.options = ChromeOptions()
        if self.headless:
            self.logger.debug('Chrome will start in headless mode')
            self.options.headless = True
            self.options.add_argument('-headless')
            self.options.add_argument("-disable-gpu")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-dev-shm-usage")
            self.options.add_argument("--remote-debugging-port=9222")
        if self.agent:
            self.logger.debug('Chrome will be configured to use a user-agent')
            self.options.add_argument(f'user-agent={self.agent}')
        return webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                                options=self.options)
