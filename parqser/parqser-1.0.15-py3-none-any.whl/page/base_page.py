from typing import Dict, Any
from parqser.page import DownloadState


class BasePage:
    def __init__(self, source_html: str, status: DownloadState):
        self.source_html = source_html
        self.status = status
        self._parsed_params = {}

    def get_source(self) -> str:
        return self.source_html

    def add_parsed_parameter(self, name: str, value: Any):
        if name in self._parsed_params.keys():
            raise AttributeError(f'Parameter {name} has already parsed')
        self._parsed_params[name] = value

    def to_dict(self) -> Dict[str, Any]:
        return self._parsed_params
