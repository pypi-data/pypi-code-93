import matplotlib.pyplot as plt
import numpy as np
from typing import Iterable, Optional, Union
import matplotlib as mpl

from matplotlib.axes import Axes
from ._themes import Theme
from feyn._validation import (
    _validate_prob_values,
    _validate_bool_values,
)
from feyn.metrics import precision_recall, accuracy_score, f1_score, false_positive_rate
from feyn._typings import check_types

@check_types()
def plot_roc_curve(
    y_true: Iterable[Union[bool, float]],
    y_pred: Iterable[float],
    threshold: Optional[float] = None,
    title: str = "ROC curve",
    ax: Optional[Axes] = None,
    **kwargs,
) -> Axes:
    """
    Plot a ROC curve for a classification model.

    A receiver operating characteristic curve, or ROC curve, is an illustration of the diagnostic ability of a binary classifier. The method was developed for operators of military radar receivers, which is why it is so named.

    Arguments:
        y_true -- Expected values (Truth).
        y_pred -- Predicted values.
        threshold -- Plots a point on the ROC curve of the true positive rate and false positive rate at the given threshold. Default is None
        title -- Title of the plot.
        ax -- matplotlib axes object to draw to, default None

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: When y_true is not boolean (or 0/1).
        ValueError: When y_true and y_pred do not have same shape.
        ValueError: When threshold is not between 0 and 1.
    """

    if not _validate_bool_values(y_true):
        raise ValueError("true values must be an iterable of booleans or 0s and 1s")

    if not _validate_prob_values(y_pred):
        raise ValueError("predictions must be an iterable of floats between 0 and 1")

    if not len(y_pred) == len(y_true):
        raise ValueError("The lengths of predictions and true values do not match")

    if ax is None:
        ax = plt.gca()

    import sklearn.metrics

    fpr, tpr, _ = sklearn.metrics.roc_curve(y_true, y_pred)
    roc_auc = sklearn.metrics.auc(fpr, tpr)

    ax.set_title(title)

    if threshold is not None:
        if threshold > 1 or 0 > threshold:
            raise ValueError("threshold must be between 0 and 1")

        y_pred_rounded = y_pred >= threshold

        false_pos_rate = false_positive_rate(y_true, y_pred_rounded)
        precision, recall = precision_recall(y_true, y_pred_rounded)
        accuracy = accuracy_score(y_true, y_pred_rounded)
        f1 = f1_score(y_true, y_pred_rounded)

        ax.vlines(x=false_pos_rate, ymin=0, ymax=recall, ls="--", lw=1.5)
        ax.hlines(y=recall, xmin=0, xmax=false_pos_rate, ls="--", lw=1.5)
        ax.scatter(false_pos_rate, recall, marker="o", s=50, c="k")
        ax.annotate(
            text=f"({false_pos_rate:.2f}, {recall:.2f})",
            xy=(false_pos_rate, recall),
            xytext=(3, -10),
            textcoords="offset points",
        )

        text_str = "\n".join(
            (
                f"Threshold: {threshold: .2f}",
                f"Accuracy: {accuracy: .2f}",
                f"F1 score: {f1: .2f}",
                f"Precision: {precision: .2f}",
                f"Recall: {recall: .2f}",
            )
        )
        props = dict(boxstyle="round", facecolor="white", alpha=0.5)
        ax.text(0.975, 0.05, text_str, bbox=props, ha="right")

    else:
        if "label" in kwargs:
            kwargs["label"] += " AUC = %0.2f" % roc_auc
        else:
            kwargs["label"] = "AUC = %0.2f" % roc_auc

    ax.plot(fpr, tpr, **kwargs)

    if threshold is None:
        ax.legend(loc="lower right")

    ax.plot([0, 1], [0, 1], "--", c=Theme.color("dark"), lw=1.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_ylabel("True Positive Rate")
    ax.set_xlabel("False Positive Rate")

    return ax
