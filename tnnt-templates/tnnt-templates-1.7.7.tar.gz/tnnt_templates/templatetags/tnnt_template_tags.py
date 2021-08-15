"""
Template filter for Terra Nanotech templates
"""

from django.template.defaulttags import register


@register.filter
def startswith(value, arg):
    """
    Usage, {% if value|starts_with:"arg" %}
    """

    return value.startswith(arg)
