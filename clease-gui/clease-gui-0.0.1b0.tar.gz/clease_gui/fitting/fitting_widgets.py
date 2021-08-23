from abc import ABC, abstractmethod
from pathlib import Path
import ipywidgets as widgets
from IPython.display import display, clear_output
import numpy as np
from clease import regression
from clease_gui import utils, WidgetCollection, SingleWidget
import clease_gui as gui


class RegressionScheme(ABC, gui.WidgetStyleMixin):
    HYPERPARAMS = None
    NAME = None

    def __init__(self, output=None):
        assert self.HYPERPARAMS is not None, "Set the required hyperparameters!"
        assert self.NAME is not None, "Set the name!"
        self.output = output or widgets.Output()
        self.hyper_widget_dct = {}
        self.hyper_output = widgets.Output()
        self._initialize()

    def display(self):

        # display the hyperparameter dropdown next to the hyperparameter output
        # widget.
        box = widgets.HBox(
            children=[self.hyper_dropdown, self.hyper_output],
            layout={'align_items': 'center'},
        )
        with self.output:
            clear_output(wait=True)
            display(box)
            self.hyper_dropdown.value.display()

    def _initialize(self):

        options = []
        for param in self.HYPERPARAMS:
            if param == 'alpha':
                widget = Alpha(output=self.hyper_output)
                self.hyper_widget_dct[param] = widget
                options.append((param, widget))
            else:
                raise ValueError(f'Cannot handle parameter: {param}')

        # Make dropdown widget
        dropdown = widgets.Dropdown(options=options,
                                    description='Hyperparameter:',
                                    **self.DEFAULT_STYLE_KWARGS)

        def _on_change(change):
            """If we change the dropdown value, we should updatea the
            hyperparameter display"""
            if not utils.is_value_change(change):
                return
            # Display the new selected widget
            change.new.display()

        dropdown.observe(_on_change)
        self.hyper_dropdown = dropdown

    def make_parameters(self):
        params = {}
        for key, widget in self.hyper_widget_dct.items():
            value = widget.get_param()
            params[key] = value

        return params

    @abstractmethod
    def get_fitting_scheme(self):
        """Return the name of the fitting scheme"""

    @abstractmethod
    def get_fitting_scheme_class(self):
        """Return the fitting scheme class"""

    def make_fitting_instance(self, **params):
        """Make an instance of the fitting algorithm
        with a set of parameters"""
        # params = self.make_parameters()
        fit_cls = self.get_fitting_scheme_class()
        return fit_cls(**params)


class LassoScheme(RegressionScheme):
    HYPERPARAMS = ('alpha', )
    NAME = 'Lasso'

    def get_fitting_scheme(self):
        return 'lasso'

    def get_fitting_scheme_class(self):
        return regression.Lasso


class L2Scheme(RegressionScheme):
    HYPERPARAMS = ('alpha', )
    NAME = 'L2'

    def get_fitting_scheme(self):
        return 'l2'

    def get_fitting_scheme_class(self):
        return regression.Tikhonov


class FloatHyperparameter(gui.WidgetStyleMixin):
    # Name of the hyperparameter to be passed
    # into a regression scheme
    FIXED = 'fixed_hyper'
    OPTIMIZE = 'optimize_hyper'

    # Settings in the optimization boxes
    MIN_SETTINGS = {
        'value': 0.01,
        'min': 0,
        'max': 9999999,
    }
    MAX_SETTINGS = {
        'value': 1,
        'min': 0,
        'max': 9999999,
    }
    STEP_SETTINGS = {
        'value': 25,
        'min': 0,
        'max': 9999999,
    }
    DEFAULT_VALUE = 0.01  # Default float hyperparam value

    def __init__(self, output=None):
        super().__init__()
        self.output = output or widgets.Output()
        self._initialize()

    def display(self):
        box = widgets.VBox(children=[
            self.optimize_box, self.float_box, self.spacing_dropdown,
            self.range_boxes
        ])
        with self.output:
            clear_output(wait=True)
            display(box)

    @property
    def mode(self):
        value = self.optimize_box.value
        if value:
            return self.OPTIMIZE
        return self.FIXED

    def _initialize(self):
        """Construct all relevant widgets"""
        self.optimize_box = widgets.Checkbox(
            value=False,
            description='Optimize Hyperparameter?',
            **self.DEFAULT_STYLE_KWARGS,
        )

        self.float_box = widgets.FloatText(
            value=self.DEFAULT_VALUE,
            description='Value:',
            **self.DEFAULT_STYLE_KWARGS,
        )
        # Boxes for optimization, disabled by default
        self.spacing_dropdown = widgets.Dropdown(options=[
            ('Linear Spacing', 'linspace'), ('Logarithmic Spacing', 'logspace')
        ],
                                                 description='Spacing type:',
                                                 **self.DEFAULT_STYLE_KWARGS)
        self.range_boxes = make_spacing_boxes(
            self.MIN_SETTINGS,
            self.MAX_SETTINGS,
            self.STEP_SETTINGS,
            style_kwargs=self.DEFAULT_STYLE_KWARGS)

        def on_opt_change(change):
            if not utils.is_value_change(change):
                return
            self.update_mode_widgets()

        self.update_mode_widgets()  # Update the first time

        self.optimize_box.observe(on_opt_change)

    @property
    def is_optimization(self):
        return self.mode == self.OPTIMIZE

    def update_mode_widgets(self) -> None:
        is_opt = self.is_optimization
        is_fixed = not is_opt

        self.float_box.disabled = is_opt
        self.spacing_dropdown.disabled = is_fixed
        for box in self.range_boxes.children:
            box.disabled = is_fixed

    def get_min_max_step(self):
        min_val = self.range_boxes.children[0].value
        max_val = self.range_boxes.children[1].value
        step_val = self.range_boxes.children[2].value
        return (min_val, max_val, step_val)

    def get_spacing_type(self):
        return self.spacing_dropdown.value

    def get_float_value(self):
        return self.float_box.value

    def get_param(self) -> np.ndarray:
        mode = self.mode
        if mode == self.FIXED:
            # return value in a 1 elem np array
            return np.array([self.get_float_value()])

        # Optimize, generate the spacing
        min_val, max_val, step_val = self.get_min_max_step()
        spacing_type = self.get_spacing_type()
        # Get the corresponding function from NumPy
        func = getattr(np, spacing_type)
        if spacing_type == 'logspace':
            # Logspace is in base 10 by default
            # Convert min and max to the corresponding log values
            min_val = np.log10(min_val)
            max_val = np.log10(max_val)
        return func(min_val, max_val, step_val)


class Alpha(FloatHyperparameter):
    DEFAULT_VALUE = 0.01
    MIN_SETTINGS = {
        'value': 1e-5,
        'min': 0,
        'max': 9999999,
    }
    MAX_SETTINGS = {
        'value': 1.0,
        'min': 0,
        'max': 9999999,
    }
    STEP_SETTINGS = {
        'value': 25,
        'min': 0,
        'max': 9999999,
    }


class ScoringSchemeWidget(WidgetCollection):
    """Widget to select the scoring scheme,
    and optionally the number of splits"""
    def make_widgets(self):
        self.scoring_scheme = widgets.Dropdown(
            options=[
                ('K-fold', 'k-fold'),
                ('Leave-one-out CV', 'loocv'),
            ],
            value='loocv',
            description='Scoring scheme:',
            **self.DEFAULT_STYLE_KWARGS,
        )

        self.nsplits = widgets.IntText(
            value=10,
            description='Number of splits:',
            **self.DEFAULT_STYLE_KWARGS,
            disabled=self.scoring_scheme.value == 'loocv',
        )

        def on_scheme_change(change):
            if utils.is_value_change(change):
                # Disable n-splits if scoring scheme is loocv
                self.nsplits.disabled = change.new == 'loocv'

        self.scoring_scheme.observe(on_scheme_change)
        widget_box = widgets.HBox(children=[self.scoring_scheme, self.nsplits])

        return [SingleWidget('WidgetBox', widget_box)]

    @property
    def value(self):
        return dict(scoring_scheme=self.scoring_scheme.value,
                    nsplits=self.nsplits.value)


class DBSelectWidget(WidgetCollection):
    """Optional select a database to fit ECI's to."""
    def make_widgets(self):
        # Store the text widget in the object, to make it easier to access
        self.db_select = widgets.Text(
            description='Select a database:',
            **self.DEFAULT_STYLE_KWARGS,
        )

        label = widgets.Label(
            'Leave empty to use the database specified in the main settings.')

        hbox = widgets.HBox(children=[self.db_select, label])
        # return dict(db_select=hbox)
        return [SingleWidget('db_select', hbox)]

    @property
    def value(self):
        value = self.db_select.value
        if value == '':
            return None
        return Path(value)


def make_spacing_boxes(min_dct: dict,
                       max_dct: dict,
                       steps_dct: dict,
                       style_kwargs=None):
    """Heplper function to make steps boxes"""
    style_kwargs = style_kwargs or {}

    range_min = widgets.BoundedFloatText(
        description='min:',
        **min_dct,
        **style_kwargs,
    )
    range_max = widgets.BoundedFloatText(
        description='max:',
        **max_dct,
        **style_kwargs,
    )
    range_steps = widgets.BoundedIntText(
        description='steps:',
        **steps_dct,
        **style_kwargs,
    )

    range_box = widgets.VBox(
        children=[range_min, range_max, range_steps],
        layout=dict(justify_content='space-between'),
    )
    return range_box
