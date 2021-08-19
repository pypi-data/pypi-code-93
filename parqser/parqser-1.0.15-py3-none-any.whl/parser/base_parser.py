from typing import List
from inspect import getmembers, isclass
from parqser.page import BasePage
from parqser.web_component import BaseComponent


class BaseParser:
    def __init__(self, components: List[BaseComponent]):
        self._components = components

    def parse(self, page: BasePage) -> BasePage:
        """Applies each web component parser to page"""
        for component in self._components:
            param_value = component.parse(page.get_source())
            page.add_parsed_parameter(component.name, param_value)
        return page

    @classmethod
    def from_module(cls, module):
        """Creates parser from all classes in given module using reflection"""
        web_components = getmembers(module, isclass)
        classnames, class_obj = zip(*web_components)
        instances = [CompCls() for CompCls in class_obj]
        return cls(instances)
