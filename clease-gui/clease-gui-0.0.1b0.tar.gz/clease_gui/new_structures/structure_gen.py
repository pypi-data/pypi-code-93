from typing import List
import logging
import functools
from abc import ABC, abstractmethod
from IPython.display import display, clear_output
import ipywidgets as widgets
import clease
from . import structure_gen_kwarg_widgets as kwwidgets
from clease_gui import BaseDashboard, utils, register_logger, WidgetStyleMixin
import clease_gui as gui

__all__ = ['StructureGenerationDashboard']

logger = logging.getLogger(__name__)
register_logger(logger)


class StructureGenerationDashboard(BaseDashboard):
    def initialize(self):
        self.scheme_output = widgets.Output()
        self.scheme_widgets = {
            'initial_pool':
            InitialPoolWidgets(self.app_data, self.scheme_output),
            'random_structure':
            RandomStructureWidgets(self.app_data, self.scheme_output),
            'ground_state_structure':
            GroundStateStructure(self.app_data, self.scheme_output),
            'probe_structure':
            ProbeStructure(self.app_data, self.scheme_output),
        }
        self.available_schemes_b = widgets.Dropdown(
            options=[
                ('Initial Pool', 'initial_pool'),
                ('Random Structure', 'random_structure'),
                ('Ground-State Structure', 'ground_state_structure'),
                ('Probe Structure', 'probe_structure'),
            ],
            description='Generation Scheme:',
            **self.DEFAULT_STYLE_KWARGS,
        )

        def on_scheme_change(change):
            if utils.is_value_change(change):
                self.update_scheme_widgets()

        self.available_schemes_b.observe(on_scheme_change)

    def display(self):
        self.update_scheme_widgets()
        display(self.available_schemes_b, self.scheme_output)

    @property
    def current_scheme(self) -> str:
        """Get the current generation scheme"""
        return self.available_schemes_b.value

    def get_scheme_widgets(self) -> 'BaseStructGenWidgets':
        scheme = self.current_scheme
        return self.scheme_widgets[scheme]

    def update_scheme_widgets(self):
        widgets = self.get_scheme_widgets()
        widgets.draw_widgets()

    def get_args(self):
        """Get the positional arguments for the scheme"""
        widgets = self.get_scheme_widgets()
        return widgets.make_args()

    def get_kwargs(self):
        """Get the keyword arguments for the scheme"""
        widgets = self.get_scheme_widgets()
        return widgets.make_kwargs()

    def get_generator_name(self):
        widgets = self.get_scheme_widgets()
        return widgets.generator_name()


class BaseStructGenWidgets(WidgetStyleMixin, ABC):
    def __init__(self, app_data, output):
        super().__init__()
        self.app_data = app_data

        self.output = output
        self._widgets_lst = []

        # Mapping from CLEASE kwarg to function which returns its value
        self._clease_kwargs = {}
        # Positional arguments for the CLEASE generator function.
        # Should contain the functions which returns the relevant value
        # in the order they are required.
        self._clease_args = []

    @property
    def widgets_lst(self) -> List[kwwidgets.SimpleWidget]:
        return self._widgets_lst

    @property
    def clease_kwargs(self):
        """Dictionary containing callable functions
        for generating the kwarg inputs.
        """
        return self._clease_kwargs

    @property
    def clease_args(self):
        """List containing callable functions,
        which generates the input arguments"""
        return self._clease_args

    def draw_widgets(self):
        with self.output:
            clear_output(wait=True)
            for widget in self.widgets_lst:
                widget.display()

    @abstractmethod
    def generator_name(self) -> str:
        """Name of the method in the NewStructures class
        to be called for structure generation """

    def make_args(self):
        """Evaluate the arguments"""
        return tuple(f() for f in self.clease_args)

    def make_kwargs(self) -> dict:
        """Evaluate kwargs"""
        kwargs = {name: f() for name, f in self.clease_kwargs.items()}
        logger.debug('New struct kwargs: %s', kwargs)
        return kwargs

    def register_kwarg_widget(self, *simple_widgets: kwwidgets.SimpleWidget):
        """Function to register a widget for a kwarg.
        One widget may register more than 1 key.
        """

        for simple_widget in simple_widgets:

            for key in simple_widget.widget_dct.keys():
                func = functools.partial(simple_widget.get_value, key)
                self.clease_kwargs[key] = func
            self.widgets_lst.append(simple_widget)

    def register_arg_widget(self, *simple_widgets: kwwidgets.SimpleWidget):
        """Register a widget to return an argument.
        Note that the ordering here matters.
        Can take multiple widgets.
        """
        for simple_widget in simple_widgets:
            for key in simple_widget.widget_dct.keys():
                func = functools.partial(simple_widget.get_value, key)

                self.clease_args.append(func)
            self.widgets_lst.append(simple_widget)


class InitialPoolWidgets(BaseStructGenWidgets):
    def __init__(self, app_data, output):
        widgets = [kwwidgets.AtomsWidget(app_data)]
        super().__init__(app_data, output)
        for widget in widgets:
            self.register_kwarg_widget(widget)

    def generator_name(self) -> str:
        return 'generate_initial_pool'


class RandomStructureWidgets(BaseStructGenWidgets):
    def __init__(self, app_data, output):
        widgets = [kwwidgets.AtomsWidget(app_data)]
        super().__init__(app_data, output)
        for widget in widgets:
            self.register_kwarg_widget(widget)

    def generator_name(self) -> str:
        return 'generate_random_structures'


class GroundStateStructure(BaseStructGenWidgets):
    def __init__(self, app_data, output):
        key_value_widgets = [
            # kwwidgets.AtomsWidget(app_data),
            kwwidgets.InitTemp(app_data),
            kwwidgets.FinalTemp(app_data),
            kwwidgets.NumTemp(app_data),
            kwwidgets.NumStepsPerTemp(app_data),
            kwwidgets.RandomComposition(app_data),
        ]
        super().__init__(app_data, output)

        atoms_widget = kwwidgets.GSAtomsWidget(app_data)
        self.register_arg_widget(atoms_widget)
        # Register getting ECI, but we don't actually need a
        # widget for this, it's contained in the app data
        self.clease_args.append(self.get_eci)

        self.register_kwarg_widget(*key_value_widgets)

    def generator_name(self) -> str:
        return 'generate_gs_structure'

    @property
    def settings(self) -> clease.settings.ClusterExpansionSettings:
        return self.app_data[gui.AppDataKeys.SETTINGS]

    def get_eci(self):
        return self.app_data[gui.AppDataKeys.ECI]

    def get_cwd(self):
        return self.app_data[gui.AppDataKeys.CWD]


class ProbeStructure(BaseStructGenWidgets):
    def __init__(self, app_data, output):
        widgets = [
            kwwidgets.AtomsWidget(app_data),
            kwwidgets.ProbeStructTemp(app_data),
            kwwidgets.NumTemp(app_data),
            kwwidgets.NumStepsPerTemp(app_data),
            kwwidgets.ApproxMeanVar(app_data),
        ]
        super().__init__(app_data, output)
        self.register_kwarg_widget(*widgets)

    def generator_name(self) -> str:
        return 'generate_probe_structure'
