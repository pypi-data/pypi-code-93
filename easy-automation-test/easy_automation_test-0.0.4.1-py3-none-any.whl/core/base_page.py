#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/17
import os
from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from ..utils.setting import setting
from ..utils.exception import BrowserNotSupport, SeleniumHubNotSet, SeleniumHubUrlInvalid


class BasePage(ABC):
    env_dist = os.environ
    _support_browser = {'chrome': (webdriver.Chrome, DesiredCapabilities.CHROME),
                        'firefox': (webdriver.Firefox, DesiredCapabilities.FIREFOX),
                        'edge': (webdriver.Edge, DesiredCapabilities.EDGE),
                        'safari': (webdriver.Safari, DesiredCapabilities.SAFARI),
                        'opera': (webdriver.Opera, DesiredCapabilities.OPERA),
                        'ie': (webdriver.Ie, DesiredCapabilities.INTERNETEXPLORER)}

    def __init__(self):
        browser = self.env_dist.get('browser_type', 'chrome')
        if browser.lower() not in self._support_browser.keys():
            raise BrowserNotSupport(browser)

        selenium_model = self.env_dist.get('selenium_model', 'prod')
        # debug model will just use local driver to run, prod model will use remote
        # selenium hub to run.
        browser_drivers = self._support_browser.get(browser.lower())
        if selenium_model == 'prod':
            try:
                SELENIUM_HUB_URL = setting.SELENIUM_HUB_URL
            except AttributeError:
                raise SeleniumHubNotSet
            finally:
                if len(SELENIUM_HUB_URL) == 0:
                    raise SeleniumHubUrlInvalid(SELENIUM_HUB_URL)

            self.webdriver_init = self._WebdriverRemote(command_executor=SELENIUM_HUB_URL,
                                                        desired_capabilities=browser_drivers[1])
        else:
            self.webdriver_init = browser_drivers[0]

    class _WebdriverRemote:

        def __init__(self, command_executor, desired_capabilities):
            self.command_executor = command_executor
            self.desired_capabilities = desired_capabilities

        def __call__(self, **kwargs):
            return webdriver.Remote(command_executor=self.command_executor,
                                    desired_capabilities=self.desired_capabilities,
                                    **kwargs)

    @abstractmethod
    def launch(self):
        '''
        this method, should implement self.driver.get() open web_template index project_page,
        and return index project_page object.
        :return:
        '''





