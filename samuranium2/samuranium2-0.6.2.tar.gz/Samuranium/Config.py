import configparser
import os
import argparse

from Samuranium.utils.paths import PROJECT_ROOT_PATH


class Config:
    def __init__(self, context=None):
        self.config_file_location = os.path.join(PROJECT_ROOT_PATH, '.samuranium')
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_location)
        self.agent = self.__user_agent()
        self.context = context

    @property
    def is_mobile(self):
        return True

    def __user_agent(self):
        return {
            'mobile': self.browser_options.get('mobile_agent')
        }.get(os.getenv('agent', None), None)

    @property
    def default_browser_options(self):
        return {
            'browser': 'CHROME',
            'headless': False
        }

    @property
    def browser(self):
        return self.get_property('browser', 'browser')

    @property
    def browser_options(self):
        if self.config.has_section('browser'):
            return dict(self.config.items('browser'))
        return self.default_browser_options

    @property
    def default_wait_time(self):
        default_wait_time = 30
        return float(self.get_property('browser', 'max_wait_time') or default_wait_time)

    def get_property(self, category, key, optional=None):
        try:
            return self.config.get(category, key).replace('"', '').replace("'", '')
        except:
            return optional
