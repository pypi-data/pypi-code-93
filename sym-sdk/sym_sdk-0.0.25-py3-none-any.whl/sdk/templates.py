"""Workflow templates that can be declaratively provisioned."""

from abc import ABC

from sym.sdk.resource import SymResource


class Template(SymResource, ABC):
    """The :class:`~sym.sdk.templates.Template` object represents a
    common security workflow supported out of the box by Sym.

    Read more about `Templates <https://docs.symops.com/docs/available-templates>`_.
    """


class ApprovalTemplate(Template):
    """The :class:`~sym.sdk.templates.ApprovalTemplate` object represents
    a security workflow for access management supported out of the box by Sym.

    Read more about the `sym:approval <https://docs.symops.com/docs/sym-approval>`_
    :class:`~sym.sdk.templates.Template`.
    """
