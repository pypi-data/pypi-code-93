from typing import Dict, NoReturn
from jinja2 import Environment, FileSystemLoader
import os
from fathom_lib.experimentation.loggers import Logger
from fathom_lib.metrics.sklearn_metrics import SklearnMetrics
from fathom_lib.pipeline_runner import PipelineRunner
from fathom_lib.runnable.components import Runnable
from fathom_lib.validation.validation import single_split_validation
import fathom_lib.report.template_inputs as ti


class SingleSplitValidator(Runnable):
    """
    Single split validation component.

    Parameters
    ----------
    y_columns :  str or List[str]
        Column name or names with predicted variable
    model_type : str
        Information about the model type, either "classifier"
        or "regressor"
    split_at : float
        Fraction of data to be used as the training set
    """

    def __init__(
        self,
        y_columns,
        model_type="classifier",
        split_at=0.8,
    ):
        if model_type == "classifier":
            metrics = ['SklearnMetrics(["roc_auc_score", "accuracy_score"])']
        elif model_type == "regressor":
            metrics = ['SklearnMetrics(["r2_score", "mean_squared_error"])']

        self._validation_params = dict(
            y_columns=y_columns,
            model_type=model_type,
            metrics=metrics,
            split_at=split_at,
        )
        self._validation_results = None
        self._shap_plot = None

    def run(self, model: PipelineRunner, context: Dict) -> NoReturn:
        """
        Parameter ``context`` is required to have keys: `data` and `logger`
        """
        self._validation_params["X"] = context["data"]
        logger: Logger = context["logger"]

        validation_results = single_split_validation(
            pipeline=model, **self._validation_params
        )

        self._shap_plot = validation_results.pop("shap_feature_importance")
        logger.log_figure(self._shap_plot)

        if "results_by_id" in validation_results:
            results = validation_results.pop("results_by_id")
            logger.log_text_artifact(results, "results_by_id.html")

        if "prediction_plot" in validation_results:
            plot = validation_results.pop("prediction_plot")
            logger.log_plot(plot, "plot.png")

        y_test_pred = validation_results.pop("y_test_pred")
        y_test_pred_prob = validation_results.pop("y_test_pred_prob")
        pipeline = validation_results.pop("pipeline")
        X_test = validation_results.pop("X_test")
        X_train = validation_results.pop("X_train")
        y_test = validation_results.pop("y_test")
        X_columns = validation_results.pop("X_columns")
        recent_test_data = validation_results.pop("recent_test_data")
        metrics_ = validation_results.copy()

        self._validation_results = validation_results
        logger.log_metrics_and_params(
            metrics=validation_results, params=model.get_params()
        )

        try:
            env = Environment(
                loader=FileSystemLoader(searchpath=os.path.dirname(ti.__file__))
            )
            html_report = env.get_template("classification_report_template.html")
            algorithm_dict, preparation_dict = ti.algorithm_and_preparation(
                model.get_params()
            )
            logger.log_text_artifact(
                html_report.render(
                    classifier_name=ti.classifier_name(model.get_params()),
                    test_size=metrics_["validation"]["test_size"],
                    test_accuracy=metrics_["validation"]["accuracy_score"][
                        "test_accuracy_score"
                    ],
                    VariablesI=ti.features_imp(pipeline, X_columns),
                    PartialD=ti.partial_d(pipeline, X_train, X_columns),
                    ConfusionM=ti.confusion_m(y_test, y_test_pred_prob, pipeline),
                    DecisionC=ti.decision_c(y_test, y_test_pred_prob),
                    CalibrationC=ti.calibration_c(y_test, y_test_pred_prob),
                    ROCC=ti.roc_c(y_test_pred_prob, y_test),
                    DensityC=ti.density_c(y_test, y_test_pred_prob),
                    metrics_dict=ti.metrics_input(metrics_),
                    preparation_dict=preparation_dict,
                    Features=ti.features(recent_test_data),
                    algorithm_dict=algorithm_dict,
                ),
                "classification_report.html",
            )
        except AttributeError:
            print("Lack of attributes needed for html report generation.")

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
