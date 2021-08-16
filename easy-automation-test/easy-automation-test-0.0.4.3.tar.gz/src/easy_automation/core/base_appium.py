#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/8/5
from abc import ABC, abstractmethod
import os
from appium.webdriver import Remote

from ..utils.setting import setting
from ..utils.exception import SeleniumHubNotSet, SeleniumHubUrlInvalid,\
    AppiumServerNotSet, AppiumServerUrlInvalid


class BaseAppium(ABC):
    env_dist = os.environ

    def __init__(self):
        appium_model = self.env_dist.get('appium_model', 'prod')
        # debug model will just use local appium server, prod model will use remote
        # selenium hub to run.
        DESIRED_CAPABILITIES = setting.DESIRED_CAPABILITIES
        if appium_model == 'prod':
            try:
                SELENIUM_HUB_URL = setting.SELENIUM_HUB_URL
                command_executor = SELENIUM_HUB_URL
            except AttributeError:
                raise SeleniumHubNotSet
            finally:
                if len(SELENIUM_HUB_URL) == 0:
                    raise SeleniumHubUrlInvalid(SELENIUM_HUB_URL)
        else:
            try:
                APPIUM_SERVER_URL = setting.APPIUM_SERVER_URL
                command_executor = APPIUM_SERVER_URL
            except AttributeError:
                raise  AppiumServerNotSet
            finally:
                if len(APPIUM_SERVER_URL) == 0:
                    raise AppiumServerUrlInvalid(APPIUM_SERVER_URL)

        self.webdriver_init = self._WebdriverRemote(command_executor=command_executor,
                                                    desired_capabilities=DESIRED_CAPABILITIES)

    class _WebdriverRemote:

        def __init__(self, command_executor, desired_capabilities):
            self.command_executor = command_executor
            self.desired_capabilities = desired_capabilities

        def __call__(self, **kwargs):
            return Remote(self.command_executor,
                          self.desired_capabilities,
                          **kwargs)

    @abstractmethod
    def launch(self):
        '''
        this method, should implement app launch will enter main page,
        and return main page instance.
        :return:
        '''
