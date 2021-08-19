from typing import List
from parqser.page import BasePage


class BaseScrapper:
    def __init__(self, *args, **kwargs):
        raise NotImplemented

    def load_page(self, *args, **kwargs) -> BasePage:
        raise NotImplemented

    def load_pages(self, urls: List[str]) -> List[BasePage]:
        return list(map(self.load_page, urls))
