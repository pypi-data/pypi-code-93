import time
from timeit import default_timer as timer

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

from Samuranium.Config import Config
from Samuranium.utils.SelectorStrategies import SelectorStrategies
from Samuranium.utils.time import get_current_time


class WebElement:
    """
    Web element class
    """

    def __init__(self, samuranium_instance, selector, exact_selector=False,
                 max_wait_time=None, element: SeleniumWebElement = None):
        self.config = Config()
        self.browser = samuranium_instance.driver
        self.logger = samuranium_instance.logger
        self.selector = selector
        self.selector_strategies = SelectorStrategies(selector)
        self.exact_selector = exact_selector
        self.max_wait_time = max_wait_time if max_wait_time else self.config.default_wait_time
        """__selenium_element can be used to pass elements found using the webdriver externally"""
        self.__selenium_element = element
        self.__element = self.__selenium_element or None

    @property
    def element(self):
        """
        :return: web element
        """
        if not self.__element:
            self.__element: SeleniumWebElement = self.__find_element()
        return self.__element

    def update(self):
        self.__element = None
        return self.element

    @property
    def text(self):
        return self.element.text

    @property
    def is_present(self):
        return self.element is not None

    def ensure_element_exists(self):
        if not self.is_present():
            raise NoSuchElementException(
                'Element with selector "{}" was not found after {} seconds'.
                    format(self.selector, self.max_wait_time))

    def __find_element(self):
        """
        This method tries a variety of strategies to find a web element
        Instead of using selenium's implicit wait, it uses a timer and tries several times
        until an element is returned, or the timer runs out.
        :return: Selenium WebElement if found, None if not
        """
        start_time = get_current_time()
        while timer() - start_time < self.max_wait_time:
            for strategy_name, method in self.selector_strategies.finder_strategies().items():
                try:
                    if method == By.XPATH:
                        element: SeleniumWebElement = self.__find_by_xpath()
                        if element:
                            return element
                    elif method == By.CSS_SELECTOR:
                        element: SeleniumWebElement = self.__find_by_css_selector()
                        if element:
                            return element
                    else:
                        element: SeleniumWebElement = self.__find_by_strategy(method)
                        if element:
                            return element
                    if not self.exact_selector:
                        element: SeleniumWebElement = self.browser.find_element(method,
                                                                                self.selector)
                        return element
                except NoSuchElementException:
                    pass
        self.logger.error(f'Element with selector: {self.selector} was not found after '
                          f'{self.max_wait_time}')
        return None

    def __find_by_xpath(self):
        """
        This method tries to find an element using all defined xpath strategies
        :return: Selenium WebElement
        """
        for finder_name, xpath_strategy in self.selector_strategies.xpath_strategies().items():
            try:
                if self.exact_selector:
                    return self.browser.find_element_by_xpath(self.selector)
                return self.browser.find_element_by_xpath(xpath_strategy.format(self.selector))
            except NoSuchElementException:
                pass
        return None

    def __find_by_css_selector(self):
        """
        This method tries to find an element using all defined css strategies
        :return: Selenium WebElement
        """
        for finder_name, css_strategy in self.selector_strategies.css_strategies().items():
            try:
                if self.exact_selector:
                    return self.browser.find_element_by_css_selector(self.selector)
                return self.browser.find_element_by_css_selector(css_strategy.format(self.selector))
            except NoSuchElementException:
                pass
        return None

    def __find_by_strategy(self, strategy):
        """
        This method tries to find an element using all Selenium finder strategies
        :return: Selenium WebElement
        """
        try:
            return self.browser.find_element(strategy, self.selector)
        except NoSuchElementException:
            pass
        return None

    def is_displayed(self):
        try:
            return self.element.is_displayed()
        except AttributeError:
            return False

    def exists(self):
        return self.element and self.is_present

    def click(self):
        try:
            self.element.click()
            return True
        except Exception as e:
            self.logger.error('Not possible to click on element with selector {}'.format(
                self.selector), e)
            return False

    def input_text(self, text):
        """
        Inputs text on the element
        :param text: string
        :return: True if the text was inputted correctly
        """
        for _ in range(5):
            try:
                self.element.send_keys(text)
                return True
            except Exception as e:
                self.logger.error('Not possible to send text {} to element with selector {}'.format(
                    text, self.selector), e)
                self.logger.debug("Waiting 1 second until element is interactable")
                time.sleep(1)
        return False

    def get_attribute(self, attr):
        """
        Gets an attribute of the element:
        <a href="/index" />
        To get the href: get_attribute('href') -> "/index"
        :param attr: attribute name
        :return: str
        """
        return self.element.get_attribute(attr)

    def scroll_into_view(self):
        self.browser.execute_script("arguments[0].scrollIntoView(true);", self.element)
        return self.element.is_displayed()
