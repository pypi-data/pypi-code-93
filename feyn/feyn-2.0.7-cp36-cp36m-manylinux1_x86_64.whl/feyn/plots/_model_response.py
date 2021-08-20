import feyn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import product
from mpl_toolkits.axes_grid1 import make_axes_locatable
from typing import Iterable, Optional, Tuple
import warnings
from matplotlib.axes import Axes

from feyn._typings import check_types


def plot_partial(
    model: feyn.Model,
    data: pd.DataFrame,
    by: str,
    fixed: Optional[dict] = None,
    ax: Optional[Axes] = None,
) -> Tuple[Axes]:
    """
    Plot a partial dependence plot.
    This plot is useful to interpret the effect of a specific feature on the model output.

    Example:
    > models = qlattice.sample_models(["age","smoker","heartrate"], output="heartrate")
    > models = feyn.fit_models(models, data)
    > best = models[0]
    > feyn.plots.plot_partial(best, data, by="age")

    You can use any column in the dataset as the `by` parameter.
    If you use a numerical column, the feature will vary from min to max of that varialbe in the training set.
    If you use a categorical column, the feature will display all categories, sorted by the average prediction of that category.

    Arguments:
        model -- The model to plot.
        data -- The dataset to measure the loss on.
        by -- The column in the dataset to interpret by.
        fixed -- A dictionary of features and associated values to hold fixed
    """

    warnings.warn(
        "plot_partial is deprecated and will not be available in future releases. Use plot_model_response_1d for same functionality.",
        category=FutureWarning,
    )

    return plot_model_response_1d(model, data, by, fixed, ax)


@check_types()
def plot_model_response_1d(
    model: feyn.Model,
    data: pd.DataFrame,
    by: str,
    input_constraints: Optional[dict] = None,
    ax: Optional[Axes] = None,
) -> Tuple[Axes]:
    """Plot the response of a model to a single feature given by `by`.
    The remaining model features are fixed by default as the middle
    quantile (median). Additional quantiles are added if the model has
    a maximum of 3 features. You can change this behavior by determining
    `input_constraints` yourself. Any number of model features can be added to it.

    Arguments:
        model {feyn.Model} -- Model to be analysed
        data {DataFrame} -- DataFrame
        by {str} -- Model feature to plot model response

    Keyword Arguments:
        input_contraints {Optional[dict]} -- Feature values to be fixed (default: {None})
        ax {matplotlib.axes} -- matplotlib axes object to draw to (default: {None})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if by is not in the columns of data or inputs to the model.
        ValueError: if by is also in input_constraints.
        ValueError: if input_constraints contains a feature that is not in data.
        ValueError: if model.output is not in data.

    Returns:
        (ax, ax_top, ax_right) -- The three axes (main, top, right) that make up the plot
    """

    if by not in data.columns:
        raise ValueError(f"{by} is not in columns of data.")

    if by not in model.inputs:
        raise ValueError(f"{by} is not in the inputs of the model")

    if input_constraints:
        if by in input_constraints.keys():
            raise ValueError("f{by} should not be in input_constraints.")

        if not all([key in data.columns for key in input_constraints.keys()]):
            raise ValueError(
                "input_contraints contains a feature that does not belong in data"
            )

    if model.output not in data.columns:
        raise ValueError(f"{model.output} is not in columns of data.")

    cat_list = _determine_categories(model)
    is_categorical = by in cat_list

    fixed_combinations = _input_constraints_to_their_value_combinations(
        data[model.features], by, input_constraints, cat_list
    )

    if fixed_combinations == [{}]:
        legend_title = None
        fixed_labels = ["model_response"]

    else:
        legend_title, fixed_labels = _determine_legend(fixed_combinations)

    by_input = _determine_by_input(data, by, is_categorical)

    pred_axes_list = _compute_model_response_to_data_series(
        model, by, by_input, fixed_combinations
    )

    # This will ensure the output is always a number
    output_actuals = data[model.output].astype('float64')

    actual_axes = [data[by], output_actuals]

    pred_axes_list, actual_axes, ticks_loc, ranges = _process_data_to_plot(
        actual_axes, pred_axes_list, by_input, is_categorical
    )

    if ax is None:
        _, ax = plt.subplots(figsize=(8, 8))

    actuals_plot, prediction_plots = _initialize_plots(ax, fixed_combinations)

    ax, ax_top, ax_right = _append_xyaxes(ax)
    top_histogram, right_histogram = _initialize_histograms(ax_top, ax_right)

    _update_plots_with_data(
        actual_axes,
        pred_axes_list,
        fixed_labels,
        is_categorical,
        actuals_plot,
        prediction_plots,
    )

    _update_histograms_with_data(actual_axes, top_histogram, right_histogram)

    axes_labels = [by, f"Predicted {model.output}"]
    _redrawing_plots(ax, axes_labels, ticks_loc, by_input, is_categorical)

    _redrawing_histograms(ax_top, ax_right)

    ax.legend(title=legend_title, loc="center left", bbox_to_anchor=(1.35, 0.5))

    ax.set_xlim(*ranges[0])
    ax.set_ylim(*ranges[1])

    return ax, ax_top, ax_right


def _input_constraints_to_their_value_combinations(
    data, by, input_constraints, cat_list
):
    fixed = _determine_fixed_values(data, by, input_constraints, cat_list)
    fixed = _cleanse_fixed_values(fixed)

    fixed_combinations = _expand_fixed_value_combinations(fixed)

    return fixed_combinations


def _compute_model_response_to_data_series(model, by, by_input, fixed_combinations):
    pred_axes_list = []
    for fixed_combination in fixed_combinations:
        prediction_values = _get_prediction(model, by, by_input, fixed_combination)
        pred_axes_list.append([by_input, prediction_values])

    return pred_axes_list


def _get_data_ranges(data_axis_1, data_axis_2):
    ranges = []
    for data_1, data_2 in zip(data_axis_1, data_axis_2):
        min_val = min(data_1.min(), data_2.min())
        max_val = max(data_1.max(), data_2.max())
        ranges.append(_pad_axis_range(min_val, max_val))

    return ranges


def _process_data_to_plot(actual_axes, pred_axes_list, by_input, is_categorical):
    ranges = _get_data_ranges(pred_axes_list[0], actual_axes)
    ticks_loc = None
    if is_categorical:
        actual_axes = list(reversed(actual_axes))
        ranges = list(reversed(ranges))

        ticks_loc = np.linspace(0.0, 1.0, len(by_input))

        for axes_pred in pred_axes_list:
            # by_input for the prediction needs to match the ticks now.
            axes_pred[0] = ticks_loc

        # Sanitize actual data to be consistent with ticks
        actual_axes[1] = actual_axes[1].astype("category").cat.codes
        actual_axes[1] /= max(actual_axes[1])

    return pred_axes_list, actual_axes, ticks_loc, ranges


def _initialize_plots(ax, fixed_combinations):
    actuals_plot = ax.plot(0, 0, "o", color="grey", alpha=0.3)[0]
    prediction_plots = [ax.plot(0, 0)[0] for _ in fixed_combinations]

    return actuals_plot, prediction_plots


def _initialize_histograms(ax_top, ax_right):
    histogram_data = _get_histogram_data(0.0)
    top_histogram = ax_top.bar(*histogram_data, color="grey", alpha=0.6)
    right_histogram = ax_right.barh(*histogram_data, color="grey", alpha=0.6)

    return top_histogram, right_histogram


def _update_plots_with_data(
    actual_axes,
    pred_axes_list,
    fixed_labels,
    is_categorical,
    actuals_plot,
    prediction_plots,
):
    actuals_plot.set_data(*actual_axes)
    _set_partials_data(pred_axes_list, fixed_labels, prediction_plots, is_categorical)


def _update_histograms_with_data(actual_axes, top_histogram, right_histogram):
    _set_top_hist_data(top_histogram, actual_axes[0])
    _set_right_hist_data(right_histogram, actual_axes[1])


def _redrawing_plots(ax, axes_labels, ticks_loc, by_input, is_categorical):
    if is_categorical:
        axes_labels = list(reversed(axes_labels))
        # Ensure proper tick labels and spacing
        ax.set_yticks(ticks_loc)
        ax.set_yticklabels(by_input)

    ax.relim()
    ax.autoscale_view()

    _set_axes_labels(ax, axes_labels)


def _redrawing_histograms(ax_top, ax_right):
    ax_top.relim()
    ax_top.autoscale_view()
    ax_right.relim()
    ax_right.autoscale_view()


def _pad_axis_range(min_val, max_val):
    if isinstance(min_val, str) or isinstance(max_val, str):
        return -0.05, 1.05
    else:
        padding = (max_val - min_val) * 0.05
        return min_val - padding, max_val + padding


def _get_histogram_bin_width(bins):
    return (bins[1] - bins[0]) * 0.85


def _get_histogram_data(data):
    counts, bins = np.histogram(data, bins=31)

    return bins[:-1], counts


def _set_top_hist_data(histogram, axes):
    bin_locations, value_counts = _get_histogram_data(axes)
    bar_width = _get_histogram_bin_width(bin_locations)

    [bar.set_x(bin_locations[i]) for i, bar in enumerate(histogram)]
    [bar.set_height(value_counts[i]) for i, bar in enumerate(histogram)]
    [bar.set_width(bar_width) for bar in histogram]


def _set_right_hist_data(histogram, axes):
    bin_locations, value_counts = _get_histogram_data(axes)
    bar_width = _get_histogram_bin_width(bin_locations)

    [bar.set_y(bin_locations[i]) for i, bar in enumerate(histogram)]
    [bar.set_width(value_counts[i]) for i, bar in enumerate(histogram)]
    [bar.set_height(bar_width) for bar in histogram]


def _determine_categories(model):

    return [node.name for node in model if "cat" in node.spec]


def _determine_fixed_values(data, by, fixed, cat_list):

    if fixed is None:
        fixed = {}

    fixed.pop(by, None)

    quantiles = [0.5]
    amount_of_cats = 1

    for feature in _features_not_by_or_in_fixed(list(data.columns), fixed, by):

        if feature in cat_list:
            categories, counts = np.unique(data[feature], return_counts=True)
            sort_ascend_cats = categories[np.argsort(counts)]
            fixed[feature] = sort_ascend_cats[::-1][0:amount_of_cats]

        else:
            fixed[feature] = [data[feature].quantile(q) for q in quantiles]

    return fixed


def _features_not_by_or_in_fixed(feature_list, fixed, by):
    features_in_list = feature_list.copy()
    idx_by = features_in_list.index(by)
    features_in_list.pop(idx_by)

    features_in_fixed = set(fixed.keys())
    features_not_in_fixed = set(features_in_list).difference(features_in_fixed)

    return list(features_not_in_fixed)


def _cleanse_fixed_values(fixed):

    for key, value in fixed.items():
        if isinstance(value, Iterable) and not isinstance(value, str):
            continue
        else:
            fixed[key] = [value]

    return fixed


def _append_xyaxes(ax_main):
    # Takes axes and appends two axes on top and to right

    ax_main.set_aspect("auto")

    # Make the divisions
    divider = make_axes_locatable(ax_main)

    ax_x = divider.append_axes("top", size=1.4, pad=0.2, sharex=ax_main)
    ax_y = divider.append_axes("right", size=1.4, pad=0.2, sharey=ax_main)

    # Make nice ticks
    ax_main.tick_params(direction="in", top=True, right=True)
    ax_x.tick_params(direction="in", labelbottom=False)
    ax_y.tick_params(direction="in", labelleft=False)

    return ax_main, ax_x, ax_y


def _set_axes_labels(ax, labels):
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])


def _set_partials_data(prediction_axes, fixed_labels, plots, reverse_axis):
    for axes, fixed_label, plot in zip(prediction_axes, fixed_labels, plots):
        # Display
        if reverse_axis:
            plot.set_data(*reversed(axes))
            plot.set_linestyle("")
            plot.set_marker("D")
            plot.set_markersize(5)
            plot.set_label(fixed_label)
        else:
            plot.set_data(*axes)
            plot.set_linestyle("-")
            plot.set_linewidth(1.5)
            plot.set_marker("")
            plot.set_label(fixed_label)


def _expand_fixed_value_combinations(fixed):
    fixed_combinations = []
    combinations = product(*[fixed[key] for key in fixed])

    # Make the output as a list of dictionaries -> `fixed_inputs`
    for combination in combinations:
        d = {}
        for key, value in zip(fixed.keys(), combination):
            d[key] = value
        fixed_combinations.append(d)

    return fixed_combinations


def _determine_by_input(data, by, is_categorical):
    by_values = data[by]
    if is_categorical:
        by_values = np.unique(by_values)
    else:
        by_values = np.linspace(by_values.min(), by_values.max(), 100)
    return by_values


def _get_prediction(model, by, by_input, partial):
    input_dict = {**partial, **{by: by_input}}
    return model.predict(pd.DataFrame(input_dict))


def _value_to_string(value):

    return (
        f"{float(value):.3}"
        if isinstance(value, float) or isinstance(value, int)
        else str(value)
    )


def _determine_label(partial):
    values = partial.values()
    string_values = [_value_to_string(value) for value in values]

    return string_values


def _legend_table(partials):
    legend_table = []
    legend_table.append(list(partials[0].keys()))

    for partial in partials:
        legend_table.append(_determine_label(partial))

    return np.array(legend_table)


def _right_padding(string, size):
    return string.ljust(size)


def _left_padding(string, by):
    padding = len(string) + by
    return string.rjust(padding)


def _determine_max_char_len(arr):
    return max([len(char) for char in arr])


def _determine_spacing_of_cols(matrix, buffer):
    max_widths = np.apply_along_axis(_determine_max_char_len, axis=0, arr=matrix)
    buffer_arr = np.zeros(len(max_widths))
    buffer_arr[:-1] = buffer
    widths = max_widths + buffer_arr
    return widths.astype(int)


def _determine_legend(partials, buffer=2):
    legend_table = _legend_table(partials)
    widths = _determine_spacing_of_cols(legend_table, buffer)

    v_rpadding = np.vectorize(_right_padding)
    formatted_legend = v_rpadding(legend_table, widths)

    title = _left_padding("".join(formatted_legend[0]), 5)
    labels = []
    for row in formatted_legend[1:]:
        labels.append("".join(row))

    return title, labels
