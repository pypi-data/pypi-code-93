"""This module defines the core for a Kwarg type widget"""
from typing import Tuple, Sequence, List
from abc import ABC, abstractmethod
from IPython.display import display, clear_output
import ipywidgets as widgets
from clease_gui import WidgetStyleMixin

__all__ = ['WidgetCollection', 'SingleWidget']


class SingleWidget(WidgetStyleMixin, ABC):
    def __init__(self,
                 name: str,
                 widget: widgets.CoreWidget,
                 priority: int = 0):
        self.name = name
        self.widget = widget
        self.priority = priority

    def display_widget(self):
        display(self.widget)

    @property
    def value(self):
        return self.widget.value

    @value.setter
    def value(self, value):
        self.set_value(value)

    def set_value(self, value):
        self.widget.value = value


class WidgetCollection(WidgetStyleMixin, ABC):
    """The kwarg widget contains a collection of widgets
    which gets certain key - value pairs for a function.
    All relevant widgets are constructed during initialization and registered.
    """
    def __init__(self, output=None):
        self._widgets = []

        for single_widget in self.make_widgets():
            self.register_widget(single_widget)
        self.output = output

    @abstractmethod
    def make_widgets(self) -> Sequence[SingleWidget]:
        """Make the relevant widgets, and register them."""

    def register_widget(self, widget: SingleWidget) -> None:
        name = widget.name

        if name in self.get_names():
            raise RuntimeError(f'Name {name} is already registered.')

        self.widgets.append(widget)
        self.widgets.sort(key=lambda wdgt: wdgt.priority, reverse=True)

    def get_internal_widgets(self) -> Tuple[widgets.CoreWidget]:
        """Get the raw CoreWidget objects"""
        return tuple(widget.widget for widget in self.widgets)

    @property
    def widgets(self) -> List[SingleWidget]:
        """Mapping of the internal widgets"""
        return self._widgets

    def get_names(self) -> List[str]:
        return [wdgt.name for wdgt in self.widgets]

    @property
    def value(self):
        """Return the desired value(s) from the collection of widgets."""
        return {
            widget.name: self.get_widget_value(widget)
            for widget in self.widgets
        }

    def get_widget_names(self):
        return tuple(widget.name for widget in self.widgets)

    def get_value_by_name(self, name):
        """Find a find widget of particular name, and return its value"""
        return self.get_widget_value(self.get_widget_by_name(name))

    def get_widget_by_name(self, name):
        index = self.get_widget_index(name)
        return self.widgets[index].widget

    def get_widget_index(self, name) -> int:
        for idx, widget in enumerate(self.widgets):
            if widget.name == name:
                return idx
        raise ValueError((f'Widget of name {name} not found. '
                          f'Available widgets: {self.get_widget_names()}'))

    def remove_widget(self, name):
        index = self.get_widget_index(name)
        del self.widgets[index]

    def get_widget_value(self, widget: SingleWidget):
        """Function to determine the value of a particular widget"""
        return widget.value

    def display_single_widget(self, widget: SingleWidget):
        """How to display the invidual widget"""
        widget.display_widget()

    def display_all_widgets(self):
        """How to display this collection of widgets"""
        for widget in self.widgets:
            self.display_single_widget(widget)

    def display_widgets(self, output=None, clear=True, wait=True):
        """Display the internal widgets."""
        def _display():
            if clear:
                clear_output(wait=wait)
            self.display_all_widgets()

        if output is not None:
            with output:
                _display()
        elif self.output is not None:
            with self.output:
                _display()
        else:
            _display()

    def set_widget_value(self, name, value):
        """Set the value of a widget"""
        widget = self.get_widget_by_name(name)
        widget.value = value
