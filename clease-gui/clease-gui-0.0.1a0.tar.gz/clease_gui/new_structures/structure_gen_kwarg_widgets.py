from typing import Dict, Any
from abc import ABC, abstractmethod
from IPython.display import display
import ipywidgets as widgets
import ase
import clease
from clease_gui import WidgetStyleMixin, utils
import clease_gui as gui


class SimpleWidget(WidgetStyleMixin, ABC):
    def __init__(self, app_data):
        self.app_data = app_data
        self._widget_dct = self._make_widgets()

    @property
    def widget_dct(self):
        return self._widget_dct

    def get_values(self) -> Dict[str, Any]:
        return {key: self.get_value(key) for key in self.widget_dct.keys()}

    def get_value(self, key: str) -> Any:
        return self.widget_dct[key].value

    def display(self):
        display(*self.widget_dct.values())

    @abstractmethod
    def _make_widgets(self):
        """Construct the widget(s)"""


class AtomsWidget(SimpleWidget):
    """Widget for passing in an atoms object stored on disk."""
    def _make_widgets(self):
        self.atoms_widget = widgets.Text(
            description='Atoms:',
            value='',
            **self.DEFAULT_STYLE_KWARGS,
        )

        label = widgets.Label(
            'Template for structure generation. Leave empty to use a random template.'
        )
        box = widgets.HBox(children=[self.atoms_widget, label])

        return {'atoms': box}

    def get_value(self, key):
        if key == 'atoms':
            value = self.atoms_widget.value
            if value == '':
                return None
            cwd = self.app_data[gui.AppDataKeys.CWD]
            return ase.io.read(cwd / value, index=-1)
        return super().get_value(key)


class GSAtomsWidget(SimpleWidget):
    """Atoms widget for ground structure. Slightly different from the regular
    atoms widget """
    def _make_widgets(self):
        self.atoms_widget = widgets.Text(
            description='Atoms:',
            value='',
            **self.DEFAULT_STYLE_KWARGS,
        )

        label = widgets.Label(
            'Template for structure generation. Leave empty to use a random template.'
        )
        box = widgets.HBox(children=[self.atoms_widget, label])

        return {'atoms': box}

    @property
    def settings(self) -> clease.settings.ClusterExpansionSettings:
        return self.app_data[gui.AppDataKeys.SETTINGS]

    def get_value(self, key):
        if key == 'atoms':
            value = self.atoms_widget.value
            if value == '':
                # TODO: Do something better than a random template
                atoms = self.settings.template_atoms.weighted_random_template()
                return atoms
            cwd = self.app_data[gui.AppDataKeys.CWD]
            return ase.io.read(cwd / value, index=-1)
        return super().get_value(key)


class ProbeStructTemp(SimpleWidget):
    """Widget specifically for temperature estimation for ProbeStructure, since it
    can have init_temp and final_temp=None, which turns on automatic temperature
    estimation. This requires having the init_temp and final_temp widgets linked to
    a checkbox"""
    def _make_widgets(self):

        self.auto_temp = widgets.Checkbox(
            description='Automatically determine temperature?',
            value=True,
            **self.DEFAULT_STYLE_KWARGS,
        )

        self.init_temp = widgets.BoundedFloatText(
            value=2000.0,
            description='Initial temperature:',
            min=0,
            max=1e8,
            **self.DEFAULT_STYLE_KWARGS,
        )

        self.final_temp = widgets.BoundedFloatText(
            value=1.0,
            description='Final temperature:',
            min=0,
            max=1e8,
            **self.DEFAULT_STYLE_KWARGS,
        )

        def _on_change_auto(change):
            if not utils.is_value_change(change):
                return
            self._update_widgets()

        self._update_widgets()
        self.auto_temp.observe(_on_change_auto)

        return dict(init_temp=self.init_temp, final_temp=self.final_temp)

    def display(self):
        display(self.auto_temp)
        super().display()

    def get_value(self, key):
        auto = self.auto_temp.value
        if key == 'init_temp' or key == 'final_temp':
            auto = self.auto_temp.value
            if auto:
                return None
        return super().get_value(key)

    def _update_widgets(self):
        """Update the widgets according to whether
        we automatically determine temp"""
        # If auto = True, we disable
        disabled = self.auto_temp.value

        self.init_temp.disabled = disabled
        self.final_temp.disabled = disabled


class InitTemp(SimpleWidget):
    def _make_widgets(self):
        return dict(init_temp=widgets.BoundedFloatText(
            value=2000.0,
            description='Initial temperature:',
            min=0,
            max=1e8,
            **self.DEFAULT_STYLE_KWARGS,
        ))


class FinalTemp(SimpleWidget):
    def _make_widgets(self):
        return dict(final_temp=widgets.BoundedFloatText(
            value=1.0,
            description='Final temperature:',
            min=0,
            max=1e8,
            **self.DEFAULT_STYLE_KWARGS,
        ))


class NumTemp(SimpleWidget):
    def _make_widgets(self):
        return dict(num_temp=widgets.BoundedIntText(
            value=10,
            description='Num. temperatures:',
            min=1,
            max=1e8,
            **self.DEFAULT_STYLE_KWARGS,
        ))


class NumStepsPerTemp(SimpleWidget):
    def _make_widgets(self):
        return dict(num_steps_per_temp=widgets.BoundedIntText(
            value=1000,
            description='Num. steps per temp:',
            min=1,
            max=1e8,
            **self.DEFAULT_STYLE_KWARGS,
        ))


class ApproxMeanVar(SimpleWidget):
    def _make_widgets(self):
        dct = {}
        default_value = True
        mean_var = widgets.Checkbox(
            value=default_value,
            description='Approximate mean variance?',
            **self.DEFAULT_STYLE_KWARGS,
        )
        dct['approx_mean_var'] = mean_var

        num_samples_var = widgets.IntText(
            value=10000,
            disabled=not default_value,
            description='Num. samples for approx.',
            **self.DEFAULT_STYLE_KWARGS,
        )
        dct['num_samples_var'] = num_samples_var

        # num_samples_var is only enabled for approx_mean_var == True
        def on_mean_var_change(change):
            if utils.is_value_change(change):
                num_samples_var.disabled = change['new'] is not True

        mean_var.observe(on_mean_var_change)

        return dct


class RandomComposition(SimpleWidget):
    def _make_widgets(self):
        return dict(random_composition=widgets.Checkbox(
            value=True,
            description='Random composition?',
            **self.DEFAULT_STYLE_KWARGS,
        ))
