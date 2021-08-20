from typing import Iterable, Optional, Dict, Union, List, Any
import feyn
from pandas import DataFrame, Series
from matplotlib.axes import Axes
from feyn._typings import check_types

class PlotsMixin:

    @check_types()
    def plot(
        self,
        data: DataFrame,
        compare_data: Optional[Union[DataFrame, List[DataFrame]]] = None,
        corr_func: Optional[str] = None,
        labels: Optional[Iterable[str]] = None,
    ) -> "HTML":
        """
        Plot the model's summary metrics and show the signal path.

        This is a shorthand for calling feyn.plots.plot_model_summary.

        Arguments:
            data {DataFrame} -- Data set including both input and expected values.

        Keyword Arguments:
            compare_data {Optional[Union[DataFrame, List[DataFrame]]]} -- Additional data set(s) including both input and expected values. (default: {None})
            corr_func {Optional[str]} -- Correlation function to use in showing the importance of individual nodes. Must be either "mutual_information", "pearson" or "spearman". (default: {None} -> "pearson")
            labels {Optional[Iterable[str]]} - A list of labels to use instead of the default labels. Must be size 2 if using comparison dataset, else 1.

        Raises:
            TypeError: if inputs don't match the correct type.

        Returns:
            HTML -- HTML report of the model summary.
        """
        return feyn.plots._model_summary.plot_model_summary(
            self, data, compare_data=compare_data, corr_func=corr_func, labels=labels
        )

    @check_types()
    def plot_flow(self, data: DataFrame, sample: Union[DataFrame, Series]) -> "SVG":
        """Plots the flow of activations through the model, for the provided sample. Uses the provided data as background information for visualization.
        Arguments:
            data {DataFrame} -- Data set including both input and expected values.
            sample { Union[DataFrame, Series]} -- A data sample to plot the activations for.

        Raises:
            TypeError: if inputs don't match the correct type.

        Returns:
            HTML -- HTML object containing the SVG of the model activation flow.
        """
        return feyn.plots.plot_activation_flow(self, data, sample)

    @check_types()
    def plot_response_2d(
        self,
        data: DataFrame,
        fixed: Optional[Dict[str, Any]] = None,
        ax: Optional[Axes] = None,
        resolution: int = 1000,
    ) -> None:
        """
        Visualize the response of a model to numerical inputs. Works for both classification and regression problems. The plot comes in two parts:

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
        feyn.plots.plot_model_response_2d(self, data, fixed, ax, resolution)

    @check_types()
    def plot_partial2d(
        self,
        data: DataFrame,
        fixed: Optional[Dict[str, Any]] = None,
        ax: Optional[Axes] = None,
        resolution: int = 1000,
    ) -> None:
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
        feyn.plots.plot_partial2d(self, data, fixed, ax, resolution)

    @check_types()
    def plot_response_1d(
        self, data: DataFrame, by: str, input_constraints: Optional[dict] = None, ax: Optional[Axes] = None,
    ) -> None:

        """Plot the response of a model to a single feature given by `by`.
        The remaining model features are fixed by default as the middle
        quantile (median). Additional quantiles are added if the model has
        a maximum of 3 features. You can change this behavior by determining
        `input_contraints` yourself. Any number of model features can be added to it.

        Arguments:
            data {DataFrame} -- The dataset to plot on.
            by {str} -- Model feature to plot model response by.

        Keyword Arguments:
            input_contraints {Optional[dict]} -- Feature values to be fixed (default: {None}).
            ax {Optional[matplotlib.axes]} -- matplotlib axes object to draw to (default: {None}).

        Raises:
            TypeError: if inputs don't match the correct type.
            ValueError: if by is not in the columns of data or inputs to the model.
            ValueError: if by is also in input_constraints.
            ValueError: if input_constraints contains a feature that is not in data.
            ValueError: if model.output is not in data.
        """

        feyn.plots.plot_model_response_1d(self, data, by, input_constraints, ax)

    @check_types()
    def plot_partial(
        self, data: DataFrame, by: str, fixed: Optional[dict] = None, ax: Optional[Axes] = None,
    ):
        """
        Plot a partial dependence plot.
        This plot is useful to interpret the effect of a specific feature on the model output.

        Example:
        > models = qlattice.sample_models(["age","smoker","heartrate"], output="heartrate")
        > models = feyn.fit_models(models, data)
        > best = models[0]
        > best.plot_partial(data, by="age")

        You can use any column in the dataset as the `by` parameter.
        If you use a numerical column, the feature will vary from min to max of that varialbe in the training set.
        If you use a categorical column, the feature will display all categories, sorted by the average prediction of that category.

        Arguments:
            data {DataFrame} -- The dataset to plot on.
            by {str} -- The column in the dataset to interpret by.
            fixed {Optional[dict]} -- A dictionary of features and associated values to hold fixed.
            ax {matplotlib.axes} -- matplotlib axes object to draw to (default: {None}).

        Raises:
            TypeError: if inputs don't match the correct type.
            ValueError: if by is not in the columns of data or inputs to the model.
            ValueError: if by is also in input_constraints.
            ValueError: if input_constraints contains a feature that is not in data.
            ValueError: if model.output is not in data.
        """
        feyn.plots.plot_partial(self, data, by, fixed, ax)

    @check_types()
    def plot_signal(
        self,
        data: DataFrame,
        compare_data: Optional[Union[DataFrame, List[DataFrame]]] = None,
        corr_func: Optional[str] = None,
        labels: Optional[Iterable[str]] = None
    ):
        """
        Plot a model displaying the signal path and summary metrics for the provided feyn.Model and DataFrame.

        Arguments:
            dataframe {DataFrame} -- A Pandas DataFrame for showing metrics.

        Keyword Arguments:
            corr_func {Optional[str]} -- A name for the correlation function to use as the node signal, either 'mutual_information', 'pearson' or 'spearman' are available. (default: {None} defaults to 'pearson')
            compare_data {Optional[Iterable]} -- A Pandas DataFrame or list of DataFrames for showing additional metrics. (default: {None})
            labels {Optional[Iterable[str]]} - A list of labels to use instead of the default labels. Should match length of comparison data + 1.

        Raises:
            TypeError: if inputs don't match the correct type.
            ValueError: if the name of the correlation function is not understood.
            ValueError: if invalid dataframes are passed.

        Returns:
            HTML -- HTML of the model signal.
        """
        return feyn.plots.plot_model_signal(
            self, data, compare_data=compare_data, corr_func=corr_func,  labels=labels
        )
