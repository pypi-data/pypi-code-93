from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from Samuranium.Config import Config
from Samuranium.WebElement import WebElement
from selenium import webdriver
from Samuranium.utils.SelectorStrategies import SelectorStrategies


class WebElements:
    def __init__(self, samuranium_instance, selector):
        self.config = Config()
        self.samuranium_instance = samuranium_instance
        self.driver: webdriver = samuranium_instance.driver
        self.selector_strategies = SelectorStrategies(selector)
        self.logger = samuranium_instance.logger
        self.selector = selector
        self.elements = self.find_elements()

    def __len__(self):
        return len(self.elements)

    def find_elements(self):
        elements = []
        for strategy_name, method in self.selector_strategies.finder_strategies().items():
            if method == By.XPATH:
                elements = self.__find_all_by_xpath()
                if len(elements) > 0:
                    break
            elements = self.driver.find_elements(method, self.selector)
            if len(elements) > 0:
                break
        if elements:
            return [WebElement(samuranium_instance=self.samuranium_instance,
                               selector=self.selector,
                               element=element) for element in elements]

    def __find_all_by_xpath(self):
        for finder_name, xpath_strategy in self.selector_strategies.xpath_strategies().items():
            try:
                elements = self.driver.find_elements_by_xpath(xpath_strategy.format(self.selector))
                if elements:
                    return elements
            except NoSuchElementException:
                pass
        return []

