from django import template

from ..rst.rst import RstHelper

register = template.Library()


@register.filter
def app_doc(code: str) -> str:
    """
    deprecated by rst_doc

    docutils document embed in html
    """
    return RstHelper.publish_app_doc(code)
