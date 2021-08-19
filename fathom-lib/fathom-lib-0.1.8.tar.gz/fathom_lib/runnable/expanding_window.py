from typing import Dict, NoReturn

import mlflow

from fathom_lib.experimentation.loggers import Logger
from fathom_lib.metrics.sklearn_metrics import SklearnMetrics
from fathom_lib.pipeline_runner import PipelineRunner
from fathom_lib.runnable.components import Runnable
from fathom_lib.validation.validation import expanding_window_validation


class ExpandingWindowValidator(Runnable):
    """
    Expanding window validation component for predictive maintenance tasks.

    Parameters
    ----------
    y_columns :  str or List[str]
        Column name or names with predicted variable
    time_column : str
        Column name with time information
    train_cutoff_window_str : str
        Length of training window e.g "60 days"
    test_cutoff_window_str : str
        Length of testing window e.g "30 days"
    test_freq : str
        Frequency of testing iterations e.g "m"
    model_type : str
        Information about the model type, either "classifier"
        or "regressor"
    """

    def __init__(
        self,
        y_columns,
        time_column,
        train_cutoff_window_str,
        test_cutoff_window_str,
        test_freq="m",
        model_type="classifier",
    ):
        if model_type == "classifier":
            metrics = ['SklearnMetrics(["roc_auc_score", "accuracy_score"])']
        elif model_type == "regressor":
            metrics = ['SklearnMetrics(["r2_score", "mean_squared_error"])']

        self._validation_params = dict(
            y_columns=y_columns,
            time_column=time_column,
            train_cutoff_window_str=train_cutoff_window_str,
            test_cutoff_window_str=test_cutoff_window_str,
            test_freq=test_freq,
            model_type=model_type,
            metrics=metrics,
        )
        self._validation_results = None
        self._shap_plot = None

    def run(self, model: PipelineRunner, context: Dict) -> NoReturn:
        """
        Parameter ``context`` is required to have keys: `data` and `logger`
        """
        self._validation_params["X"] = context["data"]
        logger: Logger = context["logger"]

        validation_results = expanding_window_validation(
            pipeline=model, **self._validation_params
        )

        if "shap_feature_importance" in validation_results:
            self._shap_plot = validation_results.pop("shap_feature_importance")
            logger.log_figure(self._shap_plot)

        if "results_by_id" in validation_results:
            results = validation_results.pop("results_by_id")
            logger.log_text_artifact(results, "results_by_id.html")

        if "prediction_plot" in validation_results:
            plot = validation_results.pop("prediction_plot")
            logger.log_plot(plot, "plot.png")

        if "prediction_plots_per_id" in validation_results:
            plots_per_id = validation_results.pop("prediction_plots_per_id")
            logger.log_plot(plots_per_id, "prediction_plots_per_id.html")

        self._validation_results = validation_results
        logger.log_metrics_and_params(
            metrics=validation_results, params=model.get_params()
        )

        # self.logger.log_metrics_and_params(metrics=scores, params=pipeline.get_params())

    def shap_plot(self):
        """This can be used as a socket outgoing from the component"""
        if self._shap_plot is None:
            raise RuntimeError(
                "Trying to return a plot before `run` method was executed."
            )
        return self._shap_plot

    def validation_results(self):
        """This can be used as a socket outgoing from the component"""
        if self._validation_results is None:
            raise RuntimeError(
                "Trying to return results before `run` method was executed."
            )
        return self._validation_results
