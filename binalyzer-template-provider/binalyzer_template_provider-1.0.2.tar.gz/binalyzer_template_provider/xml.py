# -*- coding: utf-8 -*-
"""
    binalyzer_template_provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Template providers are used to create a template tree from a description.

    :copyright: 2020 Denis Vasilík
    :license: MIT
"""
import antlr4

from typing import Optional

from binalyzer_core import (
    Binalyzer,
    PropertyBase,
    ValueProperty,
    ReferenceProperty,
    AutoSizeValueProperty,
    StretchSizeProperty,
    OffsetValueProperty,
    RelativeOffsetReferenceProperty,
    Template,
    TemplateProvider,
    TemplateValueProvider,
    DataProvider,
    BindingContext,
)

from .generated import XMLParserListener, XMLLexer, XMLParser


class XMLTemplateParser(XMLParserListener):

    DEFAULT_ADDRESSING_MODE = "relative"
    DEFAULT_SIZING = "auto"

    ATTRIBUTES = {
        "name",
        "offset",
        "size",
        "count",
        "signature",
        "text",
        "hint",
        "padding-before",
        "padding-after",
        "boundary",
    }

    def __init__(
        self,
        template: str,
        data: Optional[bytes] = None,
        binalyzer: Optional[Binalyzer] = None,
    ):
        self._input_stream = antlr4.InputStream(template.strip())
        self._lexer = XMLLexer(self._input_stream)
        self._common_token_stream = antlr4.CommonTokenStream(self._lexer)
        self._parser = XMLParser(self._common_token_stream)
        self._parse_tree = self._parser.document()
        self._parse_tree_walker = antlr4.ParseTreeWalker()
        self._root = None
        self._templates = []
        self._data = data
        self._binalyzer = binalyzer

    def parse(self):
        self._parse_tree_walker.walk(self, self._parse_tree)
        return self._root

    def enterElement(self, ctx):
        parent = None
        if self._templates:
            parent = self._templates[-1]

        template = self._parse_attributes(Template(), parent, ctx)

        if not parent:
            self._root = template

        self._templates.append(template)

    def exitElement(self, ctx):
        if self._templates:
            self._templates.pop()

    def _parse_attributes(self, template, parent, ctx):
        self._parse_sizing_attribute(template, ctx)

        for attribute_name in self.ATTRIBUTES:
            for attribute in ctx.attribute():
                if attribute_name == attribute.Name().getText():
                    fn_name = (
                        "_parse_" + attribute_name.replace("-", "_") + "_attribute"
                    )
                    self.__class__.__dict__[fn_name](self, attribute, template, ctx)

        template.parent = parent
        return template

    def enterText(self, ctx):
        hex_str = ctx.children[0].children[0].symbol.text.strip()
        hex_str = ''.join(hex_str.split())
        if hex_str:
            self._templates[-1].text = bytes.fromhex(hex_str)

    def _parse_name_attribute(self, attribute, template, ctx):
        if attribute.binding() is not None:
            raise RuntimeError("Using a reference for a name attribute is not allowed.")
        template.name = attribute.value().getText()[1:-1]

    def _parse_count_attribute(self, attribute, template, ctx):
        template.count_property = self._parse_attribute_value(attribute, template)

    def _parse_signature_attribute(self, attribute, template, ctx):
        template.signature_property = self._parse_signature_attribute_value(
            attribute, template
        )

    def _parse_text_attribute(self, attribute, template, ctx):
        template.text = self._parse_text_attribute_value(attribute, template)

    def _parse_hint_attribute(self, attribute, template, ctx):
        template.hint_property = self._parse_hint_attribute_value(attribute, template)

    def _parse_offset_attribute(self, attribute, template, ctx):
        offset_property = self._parse_attribute_value(attribute, template)
        addressing_mode = self._parse_addressing_mode_attribute(ctx)

        if addressing_mode == "absolute":
            template.offset_property = offset_property
        elif addressing_mode == "relative":
            if isinstance(offset_property, ReferenceProperty):
                reference_name = offset_property.reference_name
                template.offset_property = RelativeOffsetReferenceProperty(
                    template, reference_name
                )
            else:
                template.offset_property = OffsetValueProperty(
                    template, offset_property.value
                )
        else:
            raise RuntimeError("Expected 'absolute' or 'relative'.")

    def _parse_addressing_mode_attribute(self, ctx):
        for attribute in ctx.attribute():
            if attribute.Name().getText() == "addressing-mode":
                return attribute.value().getText()[1:-1]
        return self.DEFAULT_ADDRESSING_MODE

    def _parse_size_attribute(self, attribute, template, ctx):
        template.size_property = self._parse_attribute_value(attribute, template)

    def _parse_sizing_attribute(self, template, ctx):
        sizing = self.DEFAULT_SIZING
        for attribute in ctx.attribute():
            if attribute.Name().getText() == "sizing":
                sizing = attribute.value().getText()[1:-1]

        if sizing == "fix":
            template.size_property = ValueProperty()
        elif sizing == "auto":
            template.size_property = AutoSizeValueProperty(template)
        elif sizing == "stretch":
            template.size_property = StretchSizeProperty(template)
        else:
            raise RuntimeError("Expected 'auto', 'fix' or 'stretch'.")

    def _parse_boundary_attribute(self, attribute, template, ctx):
        template.boundary_property = self._parse_attribute_value(attribute, template)

    def _parse_padding_before_attribute(self, attribute, template, ctx):
        template.padding_before_property = self._parse_attribute_value(
            attribute, template
        )

    def _parse_padding_after_attribute(self, attribute, template, ctx):
        template.padding_after_property = self._parse_attribute_value(
            attribute, template
        )

    def _parse_hint_attribute_value(self, attribute, template):
        return attribute.value().getText()[1:-1]

    def _parse_signature_attribute_value(self, attribute, template):
        hex_str = attribute.value().getText()[3:-1]
        return bytes.fromhex(hex_str)

    def _parse_text_attribute_value(self, attribute, template):
        hex_str = attribute.value().getText()[3:-1]
        return bytes.fromhex(hex_str)

    def _parse_attribute_value(self, attribute, template):
        if attribute.value() is not None:
            value = int(attribute.value().getText()[1:-1], base=0)
            return ValueProperty(value, template=template)

        if attribute.binding() is not None:
            return self._parse_attribute_value_reference(attribute, template)

        return ValueProperty()

    def _parse_attribute_value_reference(self, attribute, template):
        reference_name = None
        names = attribute.binding().sequence().BRACKET_NAME()

        if not "name" in names:
            name = names[0].getText()
            if not name == "byteorder" and not name == "provider":
                reference_name = name

        byteorder = "little"
        extension_name = None
        provider_name = ""
        for i, name in enumerate(names):
            if name.getText() == "name":
                reference_name = names[i + 1].getText()
            elif name.getText() == "byteorder":
                byteorder = names[i + 1].getText()
            elif name.getText() == "provider":
                provider_path = (names[i + 1].getText()).split(".")
                extension_name = provider_path[0]
                provider_name = provider_path[1]

        if reference_name:
            ref_property = ReferenceProperty(template, reference_name)
            ref_property.value_provider = self._get_custom_value_provider(
                extension_name, provider_name, ref_property
            )
            if isinstance(ref_property.value_provider, TemplateValueProvider):
                ref_property.value_provider.byteorder = byteorder
            return ref_property
        else:
            value_property = PropertyBase(template)
            value_property.value_provider = self._get_custom_value_provider(
                extension_name, provider_name, value_property
            )
            return value_property

    def _get_custom_value_provider(self, extension_name, provider_name, property):
        if not extension_name:
            return property.value_provider
        extension = self._binalyzer.extension(extension_name)
        return extension.__class__.__dict__[provider_name](extension, property)
