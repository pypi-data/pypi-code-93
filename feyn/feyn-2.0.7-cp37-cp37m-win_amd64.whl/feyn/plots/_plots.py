"""Various helper functions to compute and plot metrics."""
import itertools

import matplotlib.pyplot as plt
import numpy as np

from typing import Optional, Iterable, Union
import feyn.losses
import feyn.metrics
import feyn
import pandas as pd

import matplotlib as mpl
from matplotlib.axes import Axes

from ._themes import Theme
from feyn._validation import _validate_bool_values
from feyn._typings import check_types
from feyn.reference import BaseReferenceModel

# Sets the default theme and triggers matplotlib stylings
Theme.set_theme()


@check_types()
def plot_confusion_matrix(
    y_true: Iterable[Union[bool, float]],
    y_pred: Iterable[Union[bool, float]],
    labels: Optional[Iterable] = None,
    title: str = "Confusion matrix",
    color_map: str = "feyn-primary",
    ax: Optional[Axes] = None,
) -> Axes:
    """
    Compute and plot a Confusion Matrix.

    Arguments:
        y_true -- Expected values (Truth) as boolean or 0/1 values.
        y_pred -- Predicted values, rounded as boolean or 0/1 values.
        labels -- List of labels to index the matrix
        title -- Title of the plot.
        color_map -- Color map from matplotlib to use for the matrix
        ax -- matplotlib axes object to draw to, default None

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if y_true is not bool-like (bool or 0/1).
        ValueError: if y_pred is not bool-like (bool or 0/1).
        ValueError: if y_true and y_pred are not same size.


    Returns:
        matplotlib.axes.Axes -- matplotlib confusion matrix
    """

    if not _validate_bool_values(y_true):
        raise ValueError("y_true must be an iterable of booleans or 0s and 1s")

    if not _validate_bool_values(y_pred):
        raise ValueError("y_pred must be an iterable of booleans or 0s and 1s")

    if not len(y_true) == len(y_pred):
        raise ValueError(f"the lengths of y_true {len(y_true)} and y_pred {len(y_pred)} do not match.")

    if ax is None:
        ax = plt.gca()

    if labels is None:
        labels = np.union1d(y_pred, y_true)

    y_true = np.array(list(y_true))
    y_pred = np.array(list(y_pred))

    cm = feyn.metrics.confusion_matrix(y_true, y_pred)

    ax.set_title(title)
    tick_marks = range(len(labels))
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(labels, rotation=45)

    ax.set_yticks(tick_marks)
    ax.set_yticklabels(labels)

    thresh = (cm.max() + cm.min()) / 2.0
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        ax.text(
            j,
            i,
            format(cm[i, j], "d"),
            horizontalalignment="center",
            color=Theme.color("light") if cm[i, j] > thresh else Theme.color("dark"),
        )

    ax.set_ylabel("Expected")
    ax.set_xlabel("Predicted")

    img = ax.imshow(cm, interpolation="nearest", cmap=color_map)
    plt.colorbar(img, ax=ax)

    return ax


@check_types()
def plot_segmented_loss(
    model: Union[feyn.Model, BaseReferenceModel],
    data: pd.DataFrame,
    by: Optional[str] = None,
    loss_function: str = "squared_error",
    title: str = "Segmented Loss",
    ax: Optional[Axes] = None,
) -> Axes:
    """
    Plot the loss by segment of a dataset.

    This plot is useful to evaluate how a model performs on different subsets of the data.

    Example:
    > qg = qlattice.get_regressor(["age","smoker","heartrate"], output="heartrate")
    > qg.fit(data)
    > best = qg[0]
    > feyn.plots.plot_segmented_loss(best, data, by="smoker")

    This will plot a histogram of the model loss for smokers and non-smokers separately, which can help evaluate wheter the model has better performance for euther of the smoker sub-populations.

    You can use any column in the dataset as the `by` parameter. If you use a numerical column, the data will be binned automatically.

    Arguments:
        model -- The model to plot.
        data -- The dataset to measure the loss on.
        by -- The column in the dataset to segment by.
        loss_function -- The loss function to compute for each segmnent,
        title -- Title of the plot.
        ax -- matplotlib axes object to draw to

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if by is not in data.

    Returns:
        matplotlib.axes.Axes -- the axes for plotting.
    """
    if by is None:
        by = model.target
    elif by not in data:
        raise ValueError(
            "Argument `by` not in data"
        )

    bins, cnts, statistic = feyn.metrics.segmented_loss(model, data, by, loss_function)

    if ax is None:
        ax = plt.gca()

    ax.set_title(title)

    ax.set_xlabel("Segmented by " + by)
    ax.set_ylabel("Number of samples")

    if type(bins[0]) == tuple:
        bins = [(e[0] + e[1]) / 2 for e in bins]
        w = 0.8 * (bins[1] - bins[0])
        ax.bar(bins, height=cnts, width=w)
    else:
        ax.bar(bins, height=cnts)

    ax2 = ax.twinx()
    ax2.set_ylabel("Loss")
    ax2.plot(bins, statistic, c=Theme.color("accent"), marker="o")
    ax2.set_ylim(bottom=0)

    return ax

@check_types()
def plot_regression(
    y_true: Iterable[float],
    y_pred: Iterable[float],
    title: str = "Actuals vs Predictions",
    ax: Optional[Axes] = None,
) -> Axes:
    """This plots this true values on the x-axis and the predicted values on the y-axis.
    On top of the plot is the line of equality y=x.
    The closer the scattered values are to the line the better the predictions.
    The line of best fit between y_true and y_pred is also calculated and plotted. This line should be close to the line y=x

    Arguments:
        y_true {typing.Iterable} -- True values
        y_pred {typing.Iterable} -- Predicted values

    Keyword Arguments:
        title {str} -- (default: {"Actuals vs Predictions"})
        ax {AxesSubplot} -- (default: {None})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if y_pred and y_true are not same size.

    Returns:
        AxesSubplot -- Scatter plot of y_pred and y_true with line of best fit and line of equality
    """
    from sklearn.linear_model import LinearRegression

    if not len(y_true) == len(y_pred):
        raise ValueError("y_pred and y_true must be the same size")

    y_true = np.array(list(y_true))

    if ax is None:
        _, ax = plt.subplots()

    ax.scatter(y_true, y_pred)

    lin_reg = LinearRegression()
    lin_reg.fit(X=y_true.reshape(-1, 1), y=y_pred)
    coef = lin_reg.coef_[0]
    bias = lin_reg.intercept_

    mini = np.min([np.min(y_true), np.min(y_pred)])
    maxi = np.max([np.max(y_true), np.max(y_pred)])

    min_max_pred = lin_reg.predict(X=np.array([mini, maxi]).reshape(-1, 1))

    # Line of equality
    ax.plot([mini, maxi], [mini, maxi], ls="--", lw=1, label="line of equality")

    # Line of best fit of y_pred vs y_true
    ax.plot(
        [mini, maxi],
        min_max_pred,
        ls="--",
        lw=1,
        label=f"least squares: {coef:.2f}X + {bias:.2f}",
    )

    ax.set_title(title)
    ax.set_xlabel("Actuals")
    ax.set_ylabel("Predictions")
    ax.legend()

    return ax

@check_types()
def plot_residuals(
    y_true: Iterable[float],
    y_pred: Iterable[float],
    title: str = "Residual plot",
    ax: Optional[Axes] = None,
) -> Axes:
    """This plots the predicted values against the residuals (y_true - y_pred).

    Arguments:
        y_true {typing.Iterable} -- True values
        y_pred {typing.Iterable} -- Predicted values

    Keyword Arguments:
        title {str} -- (default: {"Residual plot"})
        ax {[type]} -- (default: {None})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if y_pred and y_true are not same size.

    Returns:
        AxesSubplot -- Scatter plot of residuals against predicted values
    """
    if not len(y_true) == len(y_pred):
        raise ValueError("y_pred and y_true must be the same size")

    if ax is None:
        _, ax = plt.subplots()

    y_true = np.array(list(y_true))
    y_pred = np.array(list(y_pred))

    residuals = y_true - y_pred

    ax.scatter(y_pred, residuals)
    ax.axhline(lw=1, ls="--")
    ax.set_title(title)
    ax.set_xlabel("Predictions")
    ax.set_ylabel("Residuals")

    return ax
