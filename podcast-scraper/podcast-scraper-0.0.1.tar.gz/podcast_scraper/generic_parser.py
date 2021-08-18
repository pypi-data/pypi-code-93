import abc
import os

from selenium.webdriver import DesiredCapabilities
from testcontainers.selenium import BrowserWebDriverContainer


class GenericParser:
    @abc.abstractmethod
    def get_urls(self, content):
        ...

    @abc.abstractmethod
    def get_next(self, webdriver):
        ...

    def connect(self, webdriver, user, password):
        # dummy implementation, to be overrided
        pass

    def format_url(self, urls):
        for url in urls:
            print(url)

    def print_urls(self, url):
        with BrowserWebDriverContainer(DesiredCapabilities.CHROME) as chrome:
            webdriver = chrome.get_driver()
            webdriver.get(url)
            self.connect(
                webdriver, os.getenv("USER", None), os.getenv("PASSWORD", None)
            )
            content = webdriver.page_source
            self.format_url(self.get_urls(content))

            while bool(self.get_next(webdriver)):
                result = webdriver.page_source
                self.format_url(self.get_urls(result))
