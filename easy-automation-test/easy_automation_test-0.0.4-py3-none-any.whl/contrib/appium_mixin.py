#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/8/5
from typing import List

from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, InvalidElementStateException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.webelement import WebElement

from easy_automation.contrib import elements
from easy_automation.utils.custom_logging import Logs
from .after_error_hook import after_error_hook
from .before_click_hook import before_click_hook

log = Logs(__name__)


class AppiumMixin:
    EXPLICIT_WAIT = 8
    android_toast = elements.Xpath("//android.widget.Toast")

    # def __init__(self, driver: WebDriver):
    #     self.driver = driver.find_element()

    @after_error_hook
    def find(self, element_selector, timeout=EXPLICIT_WAIT) -> WebElement:
        log.info(f'Find element {element_selector[1]}')
        return WebDriverWait(self.driver, timeout)\
            .until(EC.presence_of_element_located(element_selector))

    @after_error_hook
    def finds(self, element_selector, timeout=EXPLICIT_WAIT) -> List:
        log.info(f'Find elements {element_selector[1]}')
        return WebDriverWait(self.driver, timeout)\
            .until(EC.presence_of_all_elements_located(element_selector))

    @after_error_hook
    def find_from_element(self, element: WebElement, element_selector) -> WebElement:
        return element.find_element(*element_selector)

    @after_error_hook
    def finds_from_element(self, element: WebElement, element_selector) -> List:
        return element.find_elements(*element_selector)

    @after_error_hook
    def click_element(self, element_selector, timeout=EXPLICIT_WAIT):
        element = WebDriverWait(self.driver, timeout) \
            .until(EC.element_to_be_clickable(element_selector))
        before_click_hook(self.driver)
        element.click()

    def click_position(self, position):
        before_click_hook(self.driver)
        self.driver.tap([position])

    def swipe(self, start_position: tuple, end_position: tuple):
        before_click_hook(self.driver)
        try:
            self.driver.swipe(*start_position, *end_position)
        except InvalidElementStateException as e:
            log.warning(e)

    @after_error_hook
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
            before_click_hook(self.driver)
            element.click()

    def send_value(self, element_selector, value, timeout=EXPLICIT_WAIT):
        ele = self.find(element_selector, timeout)
        ele.clear()
        ele.send_keys(value)

    @after_error_hook
    def scroll_up_find(self, element_selector, max_time=5) -> WebElement:
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        while max_time:
            element = self.driver.find_elements(*element_selector)
            log.debug(f'scroll up find {element}')
            if element:
                return element[0]
            else:
                start_position = (width * 0.5, height * 0.6)
                end_position = (width * 0.5, height * 0.3)
                self.swipe(start_position, end_position)
                max_time -= 1
        raise NoSuchElementException(element_selector[1])

    @after_error_hook
    def scroll_down_find(self, element_selector, max_time=5) -> WebElement:
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        while max_time:
            element = self.driver.find_elements(*element_selector)
            log.debug(f'scroll down find {element}')
            if element:
                return element[0]
            else:
                start_position = (width * 0.5, height * 0.3)
                end_position = (width * 0.5, height * 0.6)
                self.swipe(start_position, end_position)
                max_time -= 1
        raise NoSuchElementException(element_selector[1])

    @after_error_hook
    def swipe_element_left_find(self, element: WebElement, element_selector, max_time=5) -> WebElement:
        ele_location = element.location
        ele_size = element.size
        while max_time:
            element = self.driver.find_elements(*element_selector)
            log.debug(f'scroll left find {element}')
            if element:
                return element[0]
            else:
                width, height = ele_size['width'], ele_size['height']
                x, y = ele_location['x'], ele_location['y']
                start_position = (width * 0.8, y + height * 0.5)
                end_position = (width * 0.2, y + height * 0.5)
                self.swipe(start_position, end_position)
                max_time -= 1
        raise NoSuchElementException(element_selector[1])

    @after_error_hook
    def swipe_element_right_find(self, element: WebElement, element_selector, max_time=5) -> WebElement:
        ele_location = element.location
        ele_size = element.size
        while max_time:
            element = self.driver.find_elements(*element_selector)
            log.debug(f'scroll right find {element}')
            if element:
                return element[0]
            else:
                width, height = ele_size['width'], ele_size['height']
                x, y = ele_location['x'], ele_location['y']
                start_position = (width * 0.2, y + height * 0.5)
                end_position = (width * 0.8, y + height * 0.5)
                self.swipe(start_position, end_position)
                max_time -= 1
        raise NoSuchElementException(element_selector[1])

    def get_element_text(self, element_selector, timeout=EXPLICIT_WAIT) -> str:
        return self.find(element_selector, timeout).text

    def get_elements_text(self, element_selector, timeout=EXPLICIT_WAIT, _slice=None) -> List:
        elements = self.finds(element_selector,timeout)
        if _slice and isinstance(_slice, slice):
            elements = elements[_slice]
        return (element.text for element in elements)

    def get_toast(self, timeout=EXPLICIT_WAIT) -> str:
        return self.get_element_text(self.android_toast, timeout)

    def screenshot(self):
        log.info('Get screenshot.')
        return self.driver.get_screenshot_as_png()

    def _clickable_elements(self, element_selector, timeout=EXPLICIT_WAIT):
        """
        :param element_seletctor:
        :param timeout:
        :return:
        """
        elements = WebDriverWait(self.driver, timeout)\
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
