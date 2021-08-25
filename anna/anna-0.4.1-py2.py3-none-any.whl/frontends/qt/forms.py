# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from anna.adaptors import ConfigurationAdaptor as Adaptor
from anna.adaptors import JSONAdaptor, XMLAdaptor
from anna.exceptions import InvalidPathError
from anna.parameters import get_proxied_parameter, SubstitutionParameterGroup
from . import pyqt45
from .parameters import from_type
from .widgets import Folder

Widgets = pyqt45.Widgets


class ParameterForm(Widgets.QWidget):
    """QWidget that contains input forms for a list of parameters."""

    def __init__(self, parameters, parent=None):
        """
        Initialize the form with input fields for the given parameters.

        Parameters
        ----------
        parameters : list
            List of parameters
        parent : QWidget or None
        """
        super(ParameterForm, self).__init__(parent)

        self._input_fields = {}

        if parameters:
            nonexpert_parameters = list(filter(
                lambda p: not (p.is_expert or p.is_optional),
                parameters
            ))
            expert_parameters = list(filter(
                lambda p: p.is_expert or p.is_optional,
                parameters
            ))

            v_layout = Widgets.QVBoxLayout()
            v_layout.addWidget(Widgets.QLabel('<u>Parameters:</u>'))
            v_layout.addLayout(self._layout_parameters(nonexpert_parameters))

            if expert_parameters:
                advanced_panel = Folder(title='Advanced options')
                advanced_panel.setContentLayout(self._layout_parameters(expert_parameters))
                v_layout.addWidget(advanced_panel)

            self.setLayout(v_layout)

    def __iter__(self):
        return iter(self.input_fields.items())

    def dump_as_xml(self):
        """"
        Dump the for as an xml adaptor.

        Returns
        -------
        config : ``XMLAdaptor``
        """
        return self.dump_as('xml')

    def dump_as_json(self):
        """
        Dump the for as an json adaptor.

        Returns
        -------
        config : ``JSONAdaptor``
        """
        return self.dump_as('json')

    def dump_as(self, format_):
        """
        Dump the form as a configuration adaptor.

        Parameters
        ----------
        format_ : unicode
            Specifies the format in which the content should be saved ("xml" or "json").

        Returns
        -------
        config : :py:class:`ConfigurationAdaptor` derived class
        """
        if format_ == 'xml':
            config = XMLAdaptor()
        elif format_ == 'json':
            config = JSONAdaptor()
        else:
            raise ValueError(
                'format_ must be either "xml" or "json" (got "%s" instead)'
                % format_
            )
        for path, input_field in iter(self._input_fields.items()):
            input_field.validate_input()
            if input_field.needs_to_be_dumped:
                try:
                    config.insert_element(path, input_field.as_adaptor_element())
                except NotImplementedError:
                    config.insert_config(path, input_field.as_config(format_))
        return config

    def load_from_source(self, configuration):
        """
        Fill the form with values from the given configuration source.

        Parameters
        ----------
        configuration : :py:class:`ConfigurationAdaptor`
        """
        for path, input_field in iter(self._input_fields.items()):
            try:
                input_field.load_from_adaptor_element(configuration.get_element(path))
            except InvalidPathError:
                input_field.load_default()
            except NotImplementedError:
                input_field.load_from_source(configuration.get_configuration(path))

    def _layout_parameters(self, parameters):
        layout = Widgets.QVBoxLayout()
        for parameter in parameters:
            input_field = from_type(parameter)
            if isinstance(get_proxied_parameter(parameter), SubstitutionParameterGroup):
                self._input_fields[parameter.path] = input_field
            else:
                self._input_fields[
                    Adaptor.join_paths(parameter.path, input_field.name)] = input_field
            layout.addWidget(input_field)

        return layout
