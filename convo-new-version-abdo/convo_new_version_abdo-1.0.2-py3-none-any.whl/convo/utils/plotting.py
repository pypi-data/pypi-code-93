import logging
import itertools
import os

import numpy as np
from typing import List, Text, Optional, Union, Any
import matplotlib

import convo.shared.utils.io
from convo.constants import OUTCOME_FILES

log = logging.getLogger(__name__)


def fixing_matplot_lib_backend() -> None:
    """Tries to fix a broken matplotlib backend..."""
    # At first, matplotlib will be initialized with default OS-specific
    # available backend
    if matplotlib.get_backend() == "TkAgg":
        try:
            # on OSX sometimes the tkinter package is broken and can't be imported.
            # we'll try to import it and if it fails we will use a different backend
            import tkinter  # skipcq: PYL-W0611
        except (ImportError, ModuleNotFoundError):
            log.debug("Setting matplotlib backend to 'agg'")
            matplotlib.use("agg")

    # if no backend is set by default, we'll try to set it up manually
    elif matplotlib.get_backend() is None:  # pragma: no cover
        try:
            # If the `tkinter` package is available, we can use the `TkAgg` backend
            import tkinter  # skipcq: PYL-W0611

            log.debug("Setting matplotlib backend to 'TkAgg'")
            matplotlib.use("TkAgg")
        except (ImportError, ModuleNotFoundError):
            log.debug("Setting matplotlib backend to 'agg'")
            matplotlib.use("agg")


# we call the fix as soon as this package gets imported
fixing_matplot_lib_backend()


def matrix_plot_confusion(
    matrix_confusion: np.ndarray,
    classes: Union[np.ndarray, List[Text]],
    normalize: bool = False,
    title: Text = "Confusion matrix",
    colored_map: Any = None,
    zmin: int = 1,
    output_file: Optional[Text] = None,
) -> None:
    """
    Print and plot the provided confusion matrix.
    Normalization can be applied by setting `normalize=True`.

    Args:
        matrix_confusion: confusion matrix to plot
        classes: class labels
        normalize: If set to true, normalization will be applied.
        title: title of the plot
        colored_map: color mapping
        zmin:
        output_file: output file to save plot to

    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm

    z_max = matrix_confusion.max() if len(matrix_confusion) > 0 else 1
    plt.clf()
    if not colored_map:
        colored_map = plt.cm.Blues
    plt.imshow(
        matrix_confusion,
        interpolation="nearest",
        cmap=colored_map,
        aspect="auto",
        norm=LogNorm(vmin=zmin, vmax=z_max),
    )
    plt.title(title)
    plt.colorbar()
    check_marks = np.arange(len(classes))
    plt.xticks(check_marks, classes, rotation=90)
    plt.yticks(check_marks, classes)

    if normalize:
        matrix_confusion = (
                matrix_confusion.astype("float")
                / matrix_confusion.sum(axis=1)[:, np.newaxis]
        )
        log.info(f"Normalized confusion matrix: \n{matrix_confusion}")
    else:
        log.info(f"Confusion matrix, without normalization: \n{matrix_confusion}")

    threshold = z_max / 2.0
    for i, j in itertools.product(
        range(matrix_confusion.shape[0]), range(matrix_confusion.shape[1])
    ):
        plt.text(
            j,
            i,
            matrix_confusion[i, j],
            horizontalalignment="center",
            color="white" if matrix_confusion[i, j] > threshold else "black",
        )

    plt.ylabel("True label")
    plt.xlabel("Predicted label")

    # save confusion matrix to file before showing it
    if output_file:
        figure = plt.gcf()
        figure.set_size_inches(20, 20)
        figure.savefig(output_file, bbox_inches="tight")


def plotting_histogram(
    hist_data: List[List[float]], title: Text, output_file: Optional[Text] = None
) -> None:
    """
    Plot a histogram of the confidence distribution of the predictions in two columns.

    Args:
        hist_data: histogram data
        output_file: output file to save the plot ot
    """
    import matplotlib.pyplot as plt

    plt.gcf().clear()

    # Wine-ish colour for the confidences of hits.
    # Blue-ish colour for the confidences of misses.
    colour = ["#009292", "#920000"]
    collection_bins = [0.05 * i for i in range(1, 21)]

    plt.xlim([0, 1])
    plt.hist(hist_data, bins=collection_bins, color=colour)
    plt.xticks(collection_bins)
    plt.title(title)
    plt.xlabel("Confidence")
    plt.ylabel("Number of Samples")
    plt.legend(["hits", "misses"])

    if output_file:
        figure = plt.gcf()
        figure.set_size_inches(10, 10)
        figure.savefig(output_file, bbox_inches="tight")


def plotting_curve(
    output_directory: Text,
    number_of_examples: List[int],
    x_label_text: Text,
    y_label_text: Text,
    graph_path: Text,
) -> None:
    """Plot the results from a model comparison.

    Args:
        output_directory: Output dir to save resulting plots to
        number_of_examples: Number of examples per run
        x_label_text: text for the y axis
        y_label_text: text for the y axis
        graph_path: output path of the plot
    """
    import matplotlib.pyplot as plt

    xy = plt.gca()

    # load results from file
    data_set = convo.shared.utils.io.reading_json_file(
        os.path.join(output_directory, OUTCOME_FILES)
    )
    y = number_of_examples

    # compute mean_val of all the runs for different configs
    for label in data_set.keys():
        if len(data_set[label]) == 0:
            continue
        mean_val = np.mean(data_set[label], axis=0)
        standard = np.std(data_set[label], axis=0)
        xy.plot(y, mean_val, label=label, marker=".")
        xy.fill_between(
            y,
            [m - s for m, s in zip(mean_val, standard)],
            [m + s for m, s in zip(mean_val, standard)],
            color="#6b2def",
            alpha=0.2,
        )
    xy.legend(loc=4)

    xy.set_xlabel(x_label_text)
    xy.set_ylabel(y_label_text)

    plt.savefig(graph_path, format="pdf")

    log.info(f"Comparison graph saved to '{graph_path}'.")
