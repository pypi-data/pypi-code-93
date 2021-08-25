from selenium import webdriver

from Samuranium.Config import Config
from Samuranium.DriverManager import DriverManager
from Samuranium.Logger import Logger
from Samuranium.WebElement import WebElement
from Samuranium.WebElements import WebElements


class Samuranium:
    def __init__(self, custom_logger=None, headless=None, agent=None):
        self.logger = custom_logger or Logger()
        self.config = Config()
        self.driver_manager = DriverManager(self.config, self.logger, headless=headless, agent=agent)
        self.selected_browser = self.config.browser
        self.max_wait_time = self.config.default_wait_time
        self.driver: webdriver = self.driver_manager.get_driver()

    def navigate(self, url):
        self.driver.get(url)

    def find_element(self, selector: str = None,
                     max_wait_time: float = None) -> WebElement:
        return WebElement(self, selector=selector, max_wait_time=max_wait_time)

    def find_elements(self, selector: str = None):
        return WebElements(self, selector=selector)

    def is_web_mobile(self):
        return self.driver.execute_script(
            'return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test('
            'navigator.userAgent)')
