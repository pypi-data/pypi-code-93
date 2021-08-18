# -*- coding: utf-8 -*-
"""
    binalyzer_core.binding
    ~~~~~~~~~~~~~~~~~~~~~~

    This module implements the binding engine that is used to bind templates to
    binary streams.

    :copyright: 2021 Denis Vasilík
    :license: MIT
"""
from .factory import TemplateFactory
from .properties import ValueProperty
from .template_provider import (
    TemplateProviderBase,
    TemplateProvider,
)
from .data_provider import (
    DataProviderBase,
    ZeroedDataProvider,
    PinnedBufferedIODataProvider,
)
from .utils import (
    leftsiblings,
    rightsiblings,
)


class BindingEngine(object):

    def __init__(self):
        self._template_factory = TemplateFactory()
        self._template_visitor = {
            lambda t: t.count > 1: self._expand,
            lambda t: t.count == 0: self._reduce,
            lambda t: t.signature: self._validate,
        }

    def bind(self, template, binding_context):
        template = self._template_factory.clone(template)
        template.binding_context = binding_context
        return self._process(template, binding_context)

    def _process(self, template, binding_context):
        processing = True
        while processing:
            processing = self._find_next_and_apply(
                template,
                self._template_visitor
            )
        return template

    def _find_next_and_apply(self, template, visitors):
        for predicate, fn in visitors.items():
            if predicate(template):
                fn(template)
                return True
        for child in template.children:
            found = self._find_next_and_apply(child, visitors)
            if found:
                return True
        return False

    def _validate(self, template):
        size = len(template.signature)
        template.binding_context.data_provider.data.seek(
            template.absolute_address)
        value = template.binding_context.data_provider.data.read(size)
        if template.hint is None and template.signature != value:
            raise RuntimeError(
                f"Signature validation failed for '{template.name}'."
            )
        elif template.hint and template.signature != value:
            template.parent = None
        template.signature = None

    def _reduce(self, template):
        template.parent = None

    def _expand(self, expandable):
        count = expandable.count
        parent = expandable.parent
        left = leftsiblings(expandable)
        right = rightsiblings(expandable)

        expandable.parent = None
        expandable.count_property = ValueProperty(1)

        duplicates = []
        for i in range(count):
            duplicates.append(self._template_factory.clone(expandable, id=i))

        parent_children = []
        parent_children.extend(left)
        parent_children.extend(duplicates)
        parent_children.extend(right)

        parent.children = parent_children
        template_name = expandable.name.replace("-", "_")
        parent.__dict__[template_name] = duplicates

        for i in range(count):
            del parent.__dict__[template_name + "_" + str(i)]


class BindingContext(object):
    """The :class:`BindingContext` stores information about the binding between a
    template and binary stream. It uses a :class:`~binalyzer.TemplateProvider` and
    a :class:`~binalyzer.DataProvider` to get templates and binary streams from
    various different sources.

    The :class:`~binalyzer.BackedBindingContext` for instance uses a
    :class:`~binalyzer.ZeroedDataProvider` to bind a given template to zeroed data.

    :param template_provider: a :class:`~binalyzer.TemplateProvider`
    :param data_provider: a :class:`~binalyzer.DataProvider`
    """

    def __init__(
        self,
        template_provider: TemplateProviderBase,
        data_provider: DataProviderBase,
        propagate=True
    ):
        #: The data provider to get the binary stream from.
        self.data_provider = data_provider

        self._binding_engine = BindingEngine()

        #: The template provider to get the template from.
        self.template_provider = template_provider

        if propagate:
            self.template_provider.template.binding_context = self
        else:
            self.template_provider.template._binding_context = self

        self._cached_dom = None

    @property
    def template(self):
        """A :class:`~binalyzer.template.Template` that is bound to the
        corresponding binary :attr:`~binalyzer.Binalyzer.data`.
        """
        return self._create_dom()

    @template.setter
    def template(self, value):
        self.template_provider.template = value
        self.template_provider.template.binding_context = self
        self._invalidate_dom()

    @property
    def data(self):
        """A buffered or unbuffered binary stream that inherits :class:`~io.IOBase`.
        It is bound to the corresponding :attr:`~binalyzer.Binalyzer.template`.
        """
        return self.data_provider.data

    @data.setter
    def data(self, value):
        self.data_provider.data = value

    def propagate(self, template):
        if template.children:
            for child in template.children:
                child.binding_context = self

    def _invalidate_dom(self):
        self._cached_dom = None

    def _create_dom(self):
        if self._cached_dom:
            return self._cached_dom
        self._cached_dom = self._binding_engine.bind(
            self.template_provider.template,
            self
        )
        return self._cached_dom


class BackedBindingContext(BindingContext):
    """ The :class:`~binalyzer.BackedBindingContext` uses a
    :class:`~binalyzer.ZeroedDataProvider` to bind a given template to zeroed
    data.
    """

    def __init__(self, template, propagate=True):
        super(BackedBindingContext, self).__init__(
            TemplateProvider(template), ZeroedDataProvider(), propagate)


class PinnedBindingContext(BindingContext):

    def __init__(self, template, propagate=True):
        super(PinnedBindingContext, self).__init__(
            TemplateProvider(template),
            PinnedBufferedIODataProvider(),
            propagate
        )

    def override(self, template):
        pass
