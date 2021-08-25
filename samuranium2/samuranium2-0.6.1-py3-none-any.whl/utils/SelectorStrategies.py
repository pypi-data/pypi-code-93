import os.path
from pathlib import Path

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from Samuranium.utils.classes import get_class_variables_dict
from Samuranium.utils.paths import PROJECT_ROOT_PATH


class SelectorStrategies:
    def __init__(self, selector):
        self.selector = selector
        self.config_file_location = os.path.join(PROJECT_ROOT_PATH, 'selectors.json')

    def load_custom_selectors(self):
        if self.config_file_location:
            pass

    @staticmethod
    def finder_strategies():
        return get_class_variables_dict(By)

    @staticmethod
    def xpath_strategies():
        return {'match_xpath': '{}', 'exact_text': '//*[text()="{}"]',
                'normalize_text': '//*[not(self::script)][text()[normalize-space()="{}"]]',
                'contains_text': '//*[not(self::script)][contains(text(),"{}")]',
                'normalize_contains_text':
                    '//*[not(self::script)][contains(normalize-space(.), "{}")]',
                }

    @staticmethod
    def css_strategies():
        return {'match_css': '{}', 'class_name': '.{}', 'id': '#{}'}


