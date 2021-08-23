import logging
import functools
from contextlib import contextmanager
from ipywidgets import DOMWidget
from .logging_widget import register_logger

__all__ = [
    'is_value_change',
    'disable_widget_context',
    'disables_widget',
    'disable_cls_widget',
]

logger = logging.getLogger(__name__)
register_logger(logger)


def is_value_change(change: dict):
    """Determine if a widget change is due to a change in value.
    This change comes from the widget.observe() function.
    """
    return change['type'] == 'change' and change['name'] == 'value'


@contextmanager
def disable_widget_context(widget: DOMWidget):
    """Context manager which disables a widget.
    Usage:

    with disable_widget_context(my_widget):
        do_stuff()
    """
    if not isinstance(widget, DOMWidget):
        raise TypeError(
            f'Widget must be of type DOMWidget, got {type(widget)}')
    widget.disabled = True
    logger.debug('Widget disabled')
    try:
        yield
    finally:
        widget.disabled = False
        logger.debug('Widget enabled')


def disables_widget(widget):
    """Decorator which disables a widget while function is executing.
    Usage:
    @disables_widget(my_widget)
    def my_func():
        # While this function is executing, the widget "my_widget" is disabled.
        do_stuff()
    """
    def decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            with disable_widget_context(widget):
                return func(*args, **kwargs)

        return _wrapper

    return decorator


def disable_cls_widget(widget_name: str):
    """Decorator which disables a widget of a class which is a member of "self"
    Assumes the widget name exists in "self", i.e. it uses getattr(self, widget_name)
    to access the widget.

    @disables_widget('my_widget_name')
    def my_func(self):
        do_stuff()
    """
    def decorator(func):
        @functools.wraps(func)
        def _wrapper(self, *args, **kwargs):
            widget = getattr(self, widget_name)
            with disable_widget_context(widget):
                return func(self, *args, **kwargs)

        return _wrapper

    return decorator
