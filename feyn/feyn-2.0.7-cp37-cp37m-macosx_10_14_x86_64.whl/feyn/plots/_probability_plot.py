from typing import Iterable, Optional, Union
import numpy as np
import matplotlib.pyplot as plt
from feyn._validation import (
    _validate_bool_values,
    _validate_prob_values,
)

from matplotlib.axes import Axes
from feyn._typings import check_types

def _pos_neg_classes(y_true, y_pred):
    """Finds the probability distribution
    of the positive and negative classes.
    Order of truth and prediction matters.

    Arguments:
        y_true {np.array} -- Expected values (Truth)
        y_pred {np.array} -- Predicted values
    """

    # Hits and non-hits
    hits = y_pred[np.round(y_pred) == y_true]  # TP and TN
    non_hits = y_pred[np.round(y_pred) != y_true]  # FP and FN

    # Positive and Negative classes:
    pos_class = np.append(
        hits[np.round(hits) == 1], non_hits[np.round(non_hits) == 0]
    )  # TP and FN
    neg_class = np.append(
        hits[np.round(hits) == 0], non_hits[np.round(non_hits) == 1]
    )  # TN and FP

    return pos_class, neg_class


def _hist_args_styler(data, nbins):
    """Styler for histograms. It gives them
    an edge and transparency.

    Arguments:
        data {array_like} -- data array
        nbins {int} -- number of bins
    """
    range_t = (np.min(data), np.max(data))
    bin_edges = np.histogram_bin_edges(data, bins=nbins, range=range_t)

    h_args = {
        "bins": bin_edges,
        "range": range_t,
        "edgecolor": "k",
        "lw": 1.5,
        "alpha": 0.7,
    }

    return h_args

@check_types()
def plot_probability_scores(
    y_true: Iterable[Union[bool, float]],
    y_pred: Iterable[float],
    title: str = "",
    nbins: int = 10,
    ax: Optional[Axes] = None,
    **kwargs,
) -> Axes:
    """Plots the histogram of probability scores in binary
    classification problems, highlighting the negative and
    positive classes. Order of truth and prediction matters.

    Arguments:
        y_true {array_like} -- Expected values (Truth)
        y_pred {array_like} -- Predicted values

    Keyword Arguments:
        title {str} -- plot title (default: {''})
        nbins {int} -- number of bins (default: {10})
        ax {matplotlib.axes._subplots.AxesSubplot} -- axes object (default: {None})
        kwargs -- histogram kwargs (default: {None})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if y_true is not bool-like (boolean or 0/1).
        ValueError: if y_pred is not bool-like (boolean or 0/1).
        ValueError: if y_pred and y_true are not same size.

    Returns:
        matplotlib.axes.Axes -- the axes to plot.
    """

    if not _validate_bool_values(y_true):
        raise ValueError("y_true must be an iterable of booleans or 0s and 1s")

    if not _validate_prob_values(y_pred):
        raise ValueError("y_true must be an iterable of floats between 0 and 1")

    if not len(y_pred) == len(y_true):
        raise ValueError("The lengths of y_pred and y_true do not match")

    y_pred = np.array(list(y_pred))

    pos_class, neg_class = _pos_neg_classes(y_true, y_pred)
    if not kwargs:
        unip_data = np.linspace(0.0, 1.0, 100)
        kwargs = _hist_args_styler(unip_data, nbins)

    if ax == None:
        fig = plt.figure()
        ax = fig.add_subplot()

    ax.hist(neg_class, label="Negative Class", **kwargs)
    ax.hist(pos_class, label="Positive Class", **kwargs)

    ax.legend(loc="upper center", fontsize=12)
    ax.set_ylabel("Number of ocurrences", fontsize=14)
    ax.set_xlabel("Probability Score", fontsize=14)
    ax.set_title(title, fontsize=14)

    return ax
