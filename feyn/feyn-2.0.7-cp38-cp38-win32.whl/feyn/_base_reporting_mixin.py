from typing import Iterable, Optional
import feyn
from pandas import DataFrame
from matplotlib.axes import Axes
from feyn._typings import check_types


class BaseReportingMixin:
    @check_types()
    def squared_error(self, data: DataFrame):
        """
        Compute the model's squared error loss on the provided data.

        This function is a shorthand that is equivalent to the following code:
        > y_true = data[<output col>]
        > y_pred = model.predict(data)
        > se = feyn.losses.squared_error(y_true, y_pred)

        Arguments:
            data {DataFrame} -- Data set including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.

        Returns:
            nd.array -- The losses as an array of floats.

        """
        pred = self.predict(data)
        return feyn.losses.squared_error(data[self.target], pred)

    @check_types()
    def absolute_error(self, data: DataFrame):
        """
        Compute the model's absolute error on the provided data.

        This function is a shorthand that is equivalent to the following code:
        > y_true = data[<output col>]
        > y_pred = model.predict(data)
        > se = feyn.losses.absolute_error(y_true, y_pred)

        Arguments:
            data {DataFrame} -- Data set including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.

        Returns:
            nd.array -- The losses as an array of floats.

        """
        pred = self.predict(data)
        return feyn.losses.absolute_error(data[self.target], pred)

    @check_types()
    def binary_cross_entropy(self, data: DataFrame):
        """
        Compute the model's binary cross entropy on the provided data.

        This function is a shorthand that is equivalent to the following code:
        > y_true = data[<output col>]
        > y_pred = model.predict(data)
        > se = feyn.losses.binary_cross_entropy(y_true, y_pred)

        Arguments:
            data {DataFrame} -- Data set including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.

        Returns:
            nd.array -- The losses as an array of floats.

        """
        pred = self.predict(data)
        return feyn.losses.binary_cross_entropy(data[self.target], pred)

    @check_types()
    def accuracy_score(self, data: DataFrame):
        """
        Compute the model's accuracy score on a data set.

        The accuracy score is useful to evaluate classification models. It is the fraction of the preditions that are correct. Formally it is defned as

        (number of correct predictions) / (total number of preditions)

        Arguments:
            data {DataFrame} -- Data set including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.

        Returns:
            accuracy score for the predictions
        """
        pred = self.predict(data)
        return feyn.metrics.accuracy_score(data[self.target], pred)

    @check_types()
    def accuracy_threshold(self, data: DataFrame):
        """
        Compute the accuracy score of predictions with optimal threshold

        The accuracy score is useful to evaluate classification models. It is the fraction of the preditions that are correct. Accuracy is normally calculated under the assumption that the threshold that separates true from false is 0.5. Hovever, this is not the case when a model was trained with another population composition than on the one which is used.

        This function first computes the threshold limining true from false classes that optimises the accuracy. It then returns this threshold along with the accuracy that is obtained using it.

        Arguments:
            data {DataFrame} -- Dataset to evaulate accuracy and accuracy threshold

        Returns a tuple with:
            threshold that maximizes accuracy
            accuracy score obtained with this threshold

        """
        pred = self.predict(data)
        return feyn.metrics.accuracy_threshold(data[self.target], pred)

    @check_types()
    def roc_auc_score(self, data: DataFrame):
        """
        Calculate the Area Under Curve (AUC) of the ROC curve.

        A ROC curve depicts the ability of a binary classifier with varying threshold.

        The area under the curve (AUC) is the probability that said classifier will
        attach a higher score to a random positive instance in comparison to a random
        negative instance.

        Arguments:
            data {DataFrame} -- Data set including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.

        Returns:
            AUC score for the predictions
        """
        pred = self.predict(data)
        return feyn.metrics.roc_auc_score(data[self.target], pred)

    @check_types()
    def r2_score(self, data: DataFrame):
        """
        Compute the model's r2 score on a data set

        The r2 score for a regression model is defined as
        1 - rss/tss

        Where rss is the residual sum of squares for the predictions, and tss is the total sum of squares.
        Intutively, the tss is the resuduals of a so-called "worst" model that always predicts the mean. Therefore, the r2 score expresses how much better the predictions are than such a model.

        A result of 0 means that the model is no better than a model that always predicts the mean value
        A result of 1 means that the model perfectly predicts the true value

        It is possible to get r2 scores below 0 if the predictions are even worse than the mean model.

        Arguments:
            data {DataFrame}-- Data set including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.

        Returns:
            r2 score for the predictions
        """
        pred = self.predict(data)
        return feyn.metrics.r2_score(data[self.target], pred)

    @check_types()
    def mae(self, data: DataFrame):
        """
        Compute the model's mean absolute error on a data set.

        Arguments:
            data {DataFrame}-- Data set including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.

        Returns:
            MAE for the predictions
        """
        pred = self.predict(data)
        return feyn.metrics.mae(data[self.target], pred)

    @check_types()
    def mse(self, data: DataFrame):
        """
        Compute the model's mean squared error on a data set.

        Arguments:
            data {DataFrame} -- Data set including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.

        Returns:
            MSE for the predictions
        """
        pred = self.predict(data)
        return feyn.metrics.mse(data[self.target], pred)

    @check_types()
    def rmse(self, data: DataFrame):
        """
        Compute the model's root mean squared error on a data set.

        Arguments:
            data {DataFrame}-- Data set including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.

        Returns:
            RMSE for the predictions
        """
        pred = self.predict(data)
        return feyn.metrics.rmse(data[self.target], pred)

    @check_types()
    def plot_confusion_matrix(
        self,
        data: DataFrame,
        threshold: Optional[float] = 0.5,
        labels: Optional[Iterable] = None,
        title: str = "Confusion matrix",
        color_map: str = "feyn-primary",
        ax: Optional[Axes] = None,
    ) -> None:

        """
        Compute and plot a Confusion Matrix.

        Arguments:
            data {DataFrame}-- Data set including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.
            threshold -- Boundary of True and False predictions, default 0.5
            labels -- List of labels to index the matrix
            title -- Title of the plot.
            color_map -- Color map from matplotlib to use for the matrix
            ax -- matplotlib axes object to draw to, default None
        """
        pred = self.predict(data) >= threshold
        feyn.plots.plot_confusion_matrix(
            data[self.target], pred, labels, title, color_map, ax
        )

    @check_types()
    def plot_segmented_loss(
        self,
        data: DataFrame,
        by: Optional[str] = None,
        loss_function: str = "squared_error",
        title: str = "Segmented Loss",
        ax: Optional[Axes] = None,
    ) -> None:
        """
        Plot the loss by segment of a dataset.

        This plot is useful to evaluate how a model performs on different subsets of the data.

        Example:
        > models = qlattice.sample_models(["age","smoker","heartrate"], output="heartrate")
        > models = feyn.fit_models(models, data)
        > best = models[0]
        > feyn.plots.plot_segmented_loss(best, data, by="smoker")

        This will plot a histogram of the model loss for smokers and non-smokers separately, which can help evaluate wheter the model has better performance for euther of the smoker sub-populations.

        You can use any column in the dataset as the `by` parameter. If you use a numerical column, the data will be binned automatically.

        Arguments:
            data {DataFrame} -- The dataset to measure the loss on.
            by -- The column in the dataset to segment by.
            loss_function -- The loss function to compute for each segmnent,
            title -- Title of the plot.
            ax -- matplotlib axes object to draw to
        """

        feyn.plots.plot_segmented_loss(
            self, data, by=by, loss_function=loss_function, title=title, ax=ax
        )

    @check_types()
    def plot_roc_curve(
        self,
        data: DataFrame,
        threshold: Optional[float] = None,
        title: str = "ROC curve",
        ax: Optional[Axes] = None,
        **kwargs
    ) -> None:
        """
        Plot the model's ROC curve.

        This is a shorthand for calling feyn.plots.plot_roc_curve.

        Arguments:
            data {DataFrame} -- Data set including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.
            threshold -- Plots a point on the ROC curve of the true positive rate and false positive rate at the given threshold. Default is None
            title -- Title of the plot.
            ax -- matplotlib axes object to draw to, default None
            **kwargs -- additional options to pass on to matplotlib
        """
        pred = self.predict(data)
        feyn.plots.plot_roc_curve(
            data[self.target], pred, threshold, title, ax, **kwargs
        )

    @check_types()
    def plot_probability_scores(
        self,
        data: DataFrame,
        title: str = "",
        nbins: int = 10,
        ax: Optional[Axes] = None,
        **kwargs
    ):
        """Plots the histogram of probability scores in binary
        classification problems, highlighting the negative and
        positive classes. Order of truth and prediction matters.

        Arguments:
            data {DataFrame} -- Data set including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.
        Keyword Arguments:
            title {str} -- plot title (default: {''})
            nbins {int} -- number of bins (default: {10})
            ax {matplotlib.axes._subplots.AxesSubplot} -- axes object (default: {None})
            kwargs {dict} -- histogram kwargs (default: {None})
        """

        true = data[self.target]
        pred = self.predict(data)

        feyn.plots.plot_probability_scores(true, pred, title, nbins, ax, **kwargs)

    @check_types()
    def plot_regression(
        self,
        data: DataFrame,
        title: str = "Actuals vs Prediction",
        ax: Optional[Axes] = None,
    ):
        """This plots the true values on the x-axis and the predicted values on the y-axis.
        On top of the plot is the line of equality y=x.
        The closer the scattered values are to the line the better the predictions.
        The line of best fit between y_true and y_pred is also calculated and plotted. This line should be close to the line y=x

        Arguments:
            data {DataFrame} -- The dataset to determine regression quality. It contains input names and output name of the model as columns

        Keyword Arguments:
            title {str} -- (default: {"Actuals vs Predictions"})
            ax {AxesSubplot} -- (default: {None})
        """

        y_true = data[self.target]
        y_pred = self.predict(data)

        feyn.plots.plot_regression(y_true, y_pred, title, ax)

    @check_types()
    def plot_residuals(
        self, data: DataFrame, title: str = "Residuals plot", ax: Optional[Axes] = None
    ):
        """This plots the predicted values against the residuals (y_true - y_pred).

        Arguments:
            data {DataFrame} -- The dataset containing the samples to determine the residuals of.

        Keyword Arguments:
            title {str} -- (default: {"Residual plot"})
            ax {} -- (default: {None})
        """

        y_true = data[self.target]
        y_pred = self.predict(data)

        feyn.plots.plot_residuals(y_true, y_pred, title, ax)
