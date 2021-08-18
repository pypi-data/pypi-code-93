"""
    binalyzer_template_provider.extension
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements the Binalyzer Template Provider extension.
"""
import io
import requests

from typing import Optional
from binalyzer_core import Binalyzer, BinalyzerExtension

from .xml import XMLTemplateParser


class XMLTemplateProviderExtension(BinalyzerExtension):
    def __init__(self, binalyzer=None):
        super(XMLTemplateProviderExtension, self).__init__(binalyzer, "xml")

    def init_extension(self):
        super(XMLTemplateProviderExtension, self).init_extension()

    def from_file(self, template_file_path: str, data_file_path: Optional[str] = None):
        template_text = ""
        with open(template_file_path, "r") as template_file:
            template_text = template_file.read()

        data = bytes()
        if data_file_path:
            with open(data_file_path, "rb") as data_file:
                data = data_file.read()

        return self.from_str(template_text, data)

    def from_url(self, template_url: str, data_url: Optional[str] = None, **kwargs):
        template_response = requests.get(template_url, **kwargs)
        data = None
        if data_url:
            data_response = requests.get(data_url, **kwargs)
            data = data_response.content
        return self.from_str(template_response.text, data)

    def from_str(self, text: str, data: Optional[bytes] = None):
        """Reads an XML string and creates a template object model.
        """
        template = XMLTemplateParser(text, binalyzer=self.binalyzer).parse()
        if data:
            self.binalyzer.data = io.BytesIO(data)
        self.binalyzer.template = template
        return self.binalyzer
