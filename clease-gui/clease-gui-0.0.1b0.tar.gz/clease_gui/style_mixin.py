import ipywidgets as widgets

__all__ = ['WidgetStyleMixin']

STYLE = {'description_width': '150px'}
LAYOUT = {'width': 'max-content'}


class WidgetStyleMixin:
    DEFAULT_STYLE_KWARGS = {'style': STYLE, 'layout': LAYOUT}
    DEFAULT_BUTTON_LAYOUT = widgets.Layout(**LAYOUT)
