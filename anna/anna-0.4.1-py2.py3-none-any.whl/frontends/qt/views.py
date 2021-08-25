# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os.path
import re

from anna.dependencies import Dependency
from anna.exceptions import InvalidPathError
from . import pyqt45
from .dialogs import ComponentInfoDialog
from .forms import ParameterForm
from .utils import convert_rst_to_html

QtGui = pyqt45.QtGui
Widgets = pyqt45.Widgets


class ComponentView(Widgets.QWidget):
    """
    QWidget containing the basic information (title, doc string) about a component
    *without* its parameters.
    """
    def __init__(self, component, title=None, parent=None):
        """
        Initialize the widget with a component.

        Parameters
        ----------
        component
            The component to be displayed
        title : unicode, optional
            An optional string to be displayed instead of the component's name
        parent : QWidget, optional
        """
        super(ComponentView, self).__init__(parent=parent)

        if not isinstance(component, type):
            raise TypeError('Requires a class as component (got %s instead)' % component)
        self._component = component

        info_button = Widgets.QPushButton(
            QtGui.QIcon(os.path.join(os.path.split(__file__)[0], 'icons/info.png')), ''
        )
        info_button.setFixedHeight(30)
        info_button.setFixedWidth(30)

        def show_info():
            dialog = ComponentInfoDialog(self._component, self)
            dialog.show()

        # noinspection PyUnresolvedReferences
        info_button.clicked.connect(show_info)

        doc_brief_widget = Widgets.QTextEdit()
        if component.__doc__ is not None:
            # Split at a double new line but not when preceded by "::" which indicates a following
            # related literal code block.
            # Don't strip because this could mess up indentation.
            doc_brief = re.split(r'(?<!::)\n[ ]*\n', component.__doc__)[0]
            doc_brief_widget.setText(convert_rst_to_html(doc_brief))
            doc_brief_widget.setReadOnly(True)

        layout = Widgets.QVBoxLayout()
        h_layout = Widgets.QHBoxLayout()
        h_layout.addWidget(Widgets.QLabel('<b>%s</b>' % (title or component.__name__)))
        h_layout.addStretch(1)
        h_layout.addWidget(info_button)
        layout.addLayout(h_layout)

        layout.addWidget(doc_brief_widget)
        layout.addStretch(1)

        self.setLayout(layout)


class ParametrizedComponentView(ComponentView):
    """
    QWidget containing input forms for all parameters of a component as well as for
    all dependency components.
    """
    def __init__(self, component, title=None, parent=None):
        """
        Initialize the widget with a component.

        Parameters
        ----------
        component
            The (parametrized) component to be displayed
        title : unicode, optional
            An optional string to be displayed instead of the component's name
        parent : QWidget, optional
        """
        super(ParametrizedComponentView, self).__init__(component, title, parent)

        # Remove the stretch from the inherited layout.
        self.layout().takeAt(self.layout().count() - 1)

        self._parameter_form = ParameterForm(component.get_parameters())
        self.layout().addWidget(self._parameter_form)

        self._dependency_views = []
        dependencies = self._get_dependencies()
        if dependencies:
            self.layout().addWidget(Widgets.QLabel('<u><b>Dependencies</b></u>'))
        for dependency in dependencies:
            self._dependency_views.append(ParametrizedComponentView(dependency.cls))
            self.layout().addWidget(self._dependency_views[-1])

        self.layout().addStretch(1)

    def dump_as_xml(self):
        return self.dump_as('xml')

    def dump_as_json(self):
        return self.dump_as('json')

    def dump_as(self, format_):
        if format_ not in ('json', 'xml'):
            raise ValueError(
                'format_ must be either "xml" or "json" (got "%s" instead)'
                % format_
            )
        config = self._parameter_form.dump_as(format_)
        for dependency in self._dependency_views:
            config.insert_config(self._component.CONFIG_PATH, dependency.dump_as(format_))
        return config

    def load_from_source(self, configuration):
        self._parameter_form.load_from_source(configuration)
        for dependency in self._dependency_views:
            try:
                dependency.load_from_source(
                    configuration.get_configuration(self._component.CONFIG_PATH)
                )
            except InvalidPathError:
                pass

    def _get_dependencies(self):
        return list(filter(
            lambda x: isinstance(x, Dependency),
            map(
                lambda x: getattr(self._component, x),
                dir(self._component)
            )
        ))
