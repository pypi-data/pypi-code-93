from selenium.webdriver.common.by import By


class InvalidLocatorStrategy(Exception):
    def __init__(self, strategy=None):
        self.strategy = strategy
        self.allowed_strategies = dir(By)

    def __str__(self):
        if not self.strategy:
            return f'InvalidLocatorStrategy: no selector strategy was provided. \n' \
                   f'Needs to be one of: {self.allowed_strategies}'
        return f'InvalidLocatorStrategy: "{self.strategy}" is not a valid selector strategy . \n' \
               f'Needs to be one of: {self.allowed_strategies}'
