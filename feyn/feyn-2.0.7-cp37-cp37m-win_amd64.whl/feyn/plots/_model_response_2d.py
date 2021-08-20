"""
Functions for creating a 2D response plot of an Abzu model.
"""
from typing import Dict, Union, Optional, Any

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

import feyn
import _feyn
import warnings
from feyn._typings import check_types

from pandas import DataFrame


def plot_partial2d(
    model: feyn.Model,
    data: DataFrame,
    fixed: Optional[Dict[str, Any]] = None,
    ax: Optional[Axes] = None,
    resolution: int = 1000,
) -> Axes:
    """
    Visualize the response of a model to numerical inputs using a partial plot. Works for both classification and regression problems. The partial plot comes in two parts:

    1. A colored background indicating the response of the model in a 2D space given the fixed values. A lighter color corresponds to a bigger output from the model.
    2. Scatter-plotted data on top of the background. In a classification scenario, green corresponds to positive class, and pink corresponds to the negative class. For regression, the color gradient shows the true distribution of the output value. Two sizes are used in the scatterplot, the larger dots correspond to the data that matches the values in fixed and the smaller ones have data different from the values in fixed.

    Arguments:
        model {feyn.Model} -- The feyn Model we want a partial plot of.
        data {DataFrame} -- The data that will be scattered in the model.

    Keyword Arguments:
        fixed {Optional[Dict[str, Any]]} -- Dictionary with values we fix in the model. The key is a feature name in the model and the value is a number that the feature is fixed to. (default: {None})
        ax {Optional[plt.Axes.axes]} -- Optional matplotlib axes in which to make the partial plot. (default: {None})
        resolution {int} -- The resolution at which we sample the 2D feature space for the background. (default: {1000})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if the model features names minus the fixed value names are more than two, meaning that you need to fix more values to reduce the dimensionality and make a 2D plot possible.
        ValueError: if fixed contains a feature not in the model inputs.
    """

    warnings.warn(
        "plot_partial2d is deprecated and will not be available in future releases. Use plot_model_response_2d for same functionality.",
        category=FutureWarning,
    )

    return plot_model_response_2d(model, data, fixed, ax, resolution)


@check_types()
def plot_model_response_2d(
    model: feyn.Model,
    data: DataFrame,
    fixed: Optional[Dict[str, Any]] = None,
    ax: Optional[Axes] = None,
    resolution: int = 1000,
) -> Axes:
    """
    Visualize the response of a model to numerical inputs. Works for both classification and regression problems. The plot comes in two parts:

    1. A colored background indicating the response of the model in a 2D space given the fixed values. A lighter color corresponds to a bigger output from the model.
    2. Scatter-plotted data on top of the background. In a classification scenario, green corresponds to positive class, and pink corresponds to the negative class. For regression, the color gradient shows the true distribution of the output value. Two sizes are used in the scatterplot, the larger dots correspond to the data that matches the values in fixed and the smaller ones have data different from the values in fixed.

    Arguments:
        model {feyn.Model} -- The feyn Model we want to plot the response.
        data {DataFrame} -- The data that will be scattered in the model.

    Keyword Arguments:
        fixed {Optional[Dict[str, Any]]} -- Dictionary with values we fix in the model. The key is a feature name in the model and the value is a number that the feature is fixed to. (default: {None})
        ax {Optional[plt.Axes.axes]} -- Optional matplotlib axes in which to make the partial plot. (default: {None})
        resolution {int} -- The resolution at which we sample the 2D feature space for the background. (default: {1000})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if the model features names minus the fixed value names are more than two, meaning that you need to fix more values to reduce the dimensionality and make a 2D plot possible.
        ValueError: if fixed contains a feature not in the model inputs.
    """
    if len(model.inputs) < 2:
        raise ValueError("model needs at least two inputs. Plot_response_1d is better suited for models with a single input")

    fixed = {} if fixed is None else fixed
    _validate_fixed(model, fixed)

    # Make explicit copy of model for further operations
    model = feyn.Model._from_dict(model._to_dict(include_state=True))
    pp2d = PartialPlot2D(model, data, fixed, resolution)

    if ax is None:
        plot_colorbar = True
        fig, ax = plt.subplots()
    else:
        plot_colorbar = False

    # Plot background
    im = ax.imshow(
        pp2d.synth_pred.reshape((resolution, resolution)),
        alpha=0.4,
        origin="lower",
        cmap="feyn-diverging",
    )

    # Set up axes ticks and labels
    check_length = lambda label: len(str(label)) > 4
    ax.set_xticks(pp2d.x_ticks * pp2d.a_x + pp2d.b_x)
    ax.set_xticklabels(
        pp2d.x_labels,
        rotation="vertical"
        if (any(map(check_length, pp2d.x_labels)) | len(pp2d.x_labels) > 5)
        else None,
    )

    ax.set_yticks(pp2d.y_ticks * pp2d.a_y + pp2d.b_y)
    ax.set_yticklabels(pp2d.y_labels)

    ax.set_xlabel(pp2d.x_name)
    ax.set_ylabel(pp2d.y_name)

    # Scatter data
    available_data = pp2d.data[pp2d.available_index]
    missing_data = pp2d.data[~pp2d.available_index]

    if pp2d.x_name in pp2d.categoricals:
        available_x = available_data[pp2d.x_name + "_num"] * pp2d.a_x + pp2d.b_x
        missing_x = missing_data[pp2d.x_name + "_num"] * pp2d.a_x + pp2d.b_x
    else:
        available_x = available_data[pp2d.x_name] * pp2d.a_x + pp2d.b_x
        missing_x = missing_data[pp2d.x_name] * pp2d.a_x + pp2d.b_x

    if pp2d.y_name in pp2d.categoricals:
        available_y = available_data[pp2d.y_name + "_num"] * pp2d.a_y + pp2d.b_y
        missing_y = missing_data[pp2d.y_name + "_num"] * pp2d.a_y + pp2d.b_y
    else:
        available_y = available_data[pp2d.y_name] * pp2d.a_y + pp2d.b_y
        missing_y = missing_data[pp2d.y_name] * pp2d.a_y + pp2d.b_y

    # Output within half a standard deviation of data[model.target]
    ax.scatter(
        available_x,
        available_y,
        c=available_data[model.target],
        cmap="feyn-diverging",
        s=25,
        alpha=0.9,
    )

    # Output outside of data[model.target]
    ax.scatter(
        missing_x,
        missing_y,
        c=missing_data[model.target],
        cmap="feyn-diverging",
        s=2,
        alpha=0.2,
    )

    # Add colorbar
    if plot_colorbar:
        fig.colorbar(im, ax=ax)

    return ax


class PartialPlot2D:
    """
    Class to help with organizing a partial 2D plot.
    """

    def __init__(
        self,
        model: feyn.Model,
        data: "DataFrame",
        fixed: Optional[Dict[str, Union[int, float]]] = None,
        resolution: int = 1000,
    ) -> None:

        # Inputs
        self.model = model
        self.data = data.copy()
        self.fixed = {} if fixed is None else fixed
        self.resolution = resolution

        # Other constants
        self.n_labels = 7
        self.categoricals = []
        plot = set(model.features).difference(self.fixed.keys())
        if len(plot) > 2:
            raise ValueError("Not enough features fixed.")
        self.x_name, self.y_name = plot

        # set self.{}_ticks and self.{}_labels for x and y
        # And figure out scaling parameters for the data
        self._labels_ticks()

        # Add numerical data for categorical registers
        self._numdat_for_categoricals()

        # Replace categorical x and y with numerical registers in self.model
        self._replace_registers()

        # Generate data for the background
        self.synth_pred = self._synthetic_prediction()

        # Generate boolean index for which data to include in the scatter
        self.available_index = self._relevant_scatter()

    def _relevant_scatter(self):
        """Select data to use in a scatterplot."""
        available_data = np.ones(len(self.data), dtype=bool)
        for key, value in self.fixed.items():
            if not isinstance(value, str):
                std = self.data[key].std() / 2
                lower = value - std
                upper = value + std
                new_constraint = (self.data[key] >= lower) & (self.data[key] < upper)
                available_data = available_data & new_constraint
            else:
                available_data = available_data & (self.data[key] == value)

        return available_data

    def _synthetic_prediction(self):
        """
        Perform prediction on dense synthetic data in the range of x and y.
        """
        min_x, max_x = self.x_ticks[0], self.x_ticks[-1]
        min_y, max_y = self.y_ticks[0], self.y_ticks[-1]

        adjust_x = (
            max_x - min_x
        ) * 0.05  # 5% of the range to extend each border of the image.
        adjust_y = (
            max_y - min_y
        ) * 0.05  # 5% of the range to extend each border of the image.

        # Constants for scaling
        self.a_x = self.resolution / (max_x - min_x + 2 * adjust_x)
        self.b_x = -self.a_x * (min_x - adjust_x)
        self.a_y = self.resolution / (max_y - min_y + 2 * adjust_y)
        self.b_y = -self.a_y * (min_y - adjust_y)

        x_coords, y_coords = np.meshgrid(
            np.linspace(min_x - adjust_x, max_x + adjust_x, self.resolution),
            np.linspace(min_y - adjust_y, max_y + adjust_y, self.resolution),
        )
        synth_data = {self.x_name: x_coords.flatten(), self.y_name: y_coords.flatten()}
        ssize = len(synth_data[self.x_name])
        synth_data.update(
            {fname: np.full((ssize,), value) for fname, value in self.fixed.items()}
        )

        return self.model.predict(synth_data)

    def _replace_registers(self):
        """
        Replace categorical registers in the targeted 2D space
        with LR register.
        """

        x_idx = self._interaction_idx(self.x_name, self.model)
        y_idx = self._interaction_idx(self.y_name, self.model)

        new_x_register = self._cat_to_lr(self.model[x_idx])
        new_y_register = self._cat_to_lr(self.model[y_idx])

        new_model = feyn.Model._from_dict(self.model._to_dict(include_state=True))
        new_model[x_idx] = new_x_register
        new_model[y_idx] = new_y_register

        self.model = new_model

    def _numdat_for_categoricals(self):
        """
        Add numerical data for categorical registers.
        Used in the scatterplot.
        """
        for name in self.categoricals:
            register_idx = self._interaction_idx(name, self.model)
            weights_dict = dict(self.model[register_idx].state.categories)
            self.data[name + "_num"] = self.data[name].apply(
                lambda cat: weights_dict[cat]
            )

    def _labels_ticks(self):
        """Figure out axes labels and ticks."""

        x_idx = self._interaction_idx(self.x_name, self.model)
        y_idx = self._interaction_idx(self.y_name, self.model)

        x_reg = self.model[x_idx]
        y_reg = self.model[y_idx]

        def register_to_range(reg):
            if reg.spec.startswith("in:cat(c)"):
                # reg is a categorical register, so the domain is determined
                # by the weights.
                self.categoricals.append(reg.name)
                cats = reg.state.categories.copy()
                sorted_categories = list(sorted(cats, key=lambda x: x[1]))
                labels = []
                ticks = []
                for catname, w in sorted_categories:
                    labels.append(catname)
                    ticks.append(w)
                return labels, np.array(ticks)
            else:
                # Numerical register, domain is determined by the inputs themselves
                name = reg.name
                min_val, max_val = self.data[name].min(), self.data[name].max()
                labels = np.linspace(min_val, max_val, self.n_labels)
                return np.round(labels, 1), labels

        self.x_labels, self.x_ticks = register_to_range(x_reg)
        self.y_labels, self.y_ticks = register_to_range(y_reg)

    @staticmethod
    def _cat_to_lr(old_register):
        if not old_register.spec.startswith("in:cat(c)"):
            return old_register
        new_register = _feyn.Interaction(
            "in:linear(f)->i", old_register._latticeloc, name=old_register.name
        )
        # Bias from categorical, rest as 1
        new_register.state.bias = old_register.state.bias
        new_register.state.scale = 1
        new_register.state.w = 1
        return new_register

    @staticmethod
    def _interaction_idx(name, model):
        for idx, interaction in enumerate(model):
            if interaction.name == name:
                return idx
        raise Exception(f"{name} not found in model.")


def _validate_fixed(model, fixed):
    if fixed:
        if not all([key in model.inputs for key in fixed.keys()]):
            raise ValueError("Fixed contains a feature that is not an input to the model")

    if not len(model.inputs) - len(fixed) == 2:
        raise ValueError("The amount of fixed inputs should be two less than the amount of inputs in the model.")
