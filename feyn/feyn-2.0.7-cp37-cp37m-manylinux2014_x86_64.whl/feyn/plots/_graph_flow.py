import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import feyn

from typing import Union
from feyn._typings import check_types

from feyn.plots._svg_toolkit import SVGGraphToolkit


def _get_min_max(model, data, samples=10000):
    # Magic support for pandas DataFrame
    if type(data).__name__ == "DataFrame":
        data = {col: data[col].values for col in data.columns}

    samples = min(len(next(iter(data.values()))), samples)

    permutation = np.random.permutation(samples)
    data = {key: values[permutation] for key, values in data.items()}

    minval, maxval = 0, 0
    for i in range(samples):
        sample = {key: values[i : i + 1] for key, values in data.items()}
        _ = model.predict(sample)
        gmin, gmax = min([node.activation[0] for node in model]), max(
            [node.activation[0] for node in model]
        )
        minval = min(gmin, minval)
        maxval = max(gmax, maxval)

    return minval, maxval

@check_types()
def plot_activation_flow(
    model: feyn.Model, data: DataFrame, sample: Union[DataFrame, Series]
):  # -> "SVG":
    """
    Plot a model of a model displaying the flow of activations.

    Arguments:
        model {feyn.Model}   -- A feyn.Model we want to describe given some data.
        data {DataFrame} -- A Pandas DataFrame to compute on.
        sample {Iterable} - The sample you want to visualize

    Raises:
        TypeError: if inputs don't match the correct type.

    Returns:
        SVG -- SVG of the model summary.
    """
    gtk = SVGGraphToolkit()

    # NOTE: Consider doing range [0,1] for classification
    # and min/max of prediction for regression to keep colors focused on output
    minmax = _get_min_max(model, data)

    model.predict(sample)
    activations = [np.round(node.activation[0], 2) for node in model]

    gtk.add_graph(model, label="Displaying activation of individual nodes")
    gtk.label_nodes(activations)
    gtk.color_nodes(by=activations, crange=minmax)
    gtk.add_colorbars(label="Activation strength")

    from IPython.display import HTML

    return HTML(gtk._repr_html_())
