#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/27
from typing import List

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from easy_automation.utils.custom_logging import Logs

log = Logs(__name__)


class SeleniumMixin:
    EXPLICIT_WAIT = 8

    def find(self, element_selector, timeout=EXPLICIT_WAIT) -> WebElement:
        """
        :param timeout:
        :param element_selector:
        if target element can be location, return this element
        :return:
        selenium element
        """
        return WebDriverWait(self.driver, timeout=timeout)\
            .until(EC.presence_of_element_located(element_selector))

    def finds(self, element_selector, timeout=EXPLICIT_WAIT) -> List[WebElement]:
        """
        :param  timeout:
        :param element_selector:
        if all target elements can be location, return elements list
        :return:
        selenium elements list
        """
        log.info('find element {1} by {0}'.format(*element_selector))
        return WebDriverWait(self.driver, timeout=timeout)\
            .until(EC.presence_of_all_elements_located(element_selector))

    def click_element(self, element_selector, timeout=EXPLICIT_WAIT):
        """
        :param element_seletctor:
        :param timeout:
        :return:
        """
        element = WebDriverWait(self.driver, timeout=timeout)\
            .until(EC.element_to_be_clickable(element_selector))
        element.click()

    def click_elements(self, element_selector, timeout=EXPLICIT_WAIT, _slice=None):
        """
        :param element_seletctor:
        :param timeout:
        :param _slice
        :return:
        """
        log.info('click elements {1} by {0}'.format(*element_selector))
        elements = self._clickable_elements(element_selector, timeout)
        if _slice and isinstance(_slice, slice):
            elements = elements[_slice]
        for element in elements:
            element.click()

    def get_element_text(self, element_selector, timeout=EXPLICIT_WAIT) -> str:
        return self.find(element_selector, timeout).text

    def get_elements_text(self, element_selector, timeout=EXPLICIT_WAIT, _slice=None) -> List[str]:
        elements = self.finds(element_selector, timeout)
        if _slice and isinstance(_slice, slice):
            elements = elements[_slice]
        return [ele.text for ele in elements]

    def send_value(self, element_selector, value, timeout=EXPLICIT_WAIT):
        self.find(element_selector, timeout).send_keys(value)

    def action_chain(self):
        return ActionChains(self.driver)

    def scroll_find(self, element_selector, timeout=EXPLICIT_WAIT) -> WebElement:
        element = WebDriverWait(self.driver, timeout=timeout).until(EC.presence_of_element_located(element_selector))
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        return element

    def scroll_click(self, element_selector, timeout=EXPLICIT_WAIT):
        self.scroll_find(element_selector, timeout).click()

    def _clickable_elements(self, element_selector, timeout=EXPLICIT_WAIT) -> WebElement:
        """
        :param element_seletctor:
        :param timeout:
        :return:
        """
        elements = WebDriverWait(self.driver, timeout=timeout)\
            .until(elements_to_be_clickable(element_selector))
        return elements


class elements_to_be_clickable(object):
    """ An Expectation for checking al elements is visible and enabled such that
    you can click they."""
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        elements = EC.visibility_of_all_elements_located(self.locator)(driver)
        clickable_elements = []
        if elements:
            for element in elements:
                if element.is_enabled():
                    clickable_elements.append(element)
                else:
                    return False
            return clickable_elements
        else:
            return False
