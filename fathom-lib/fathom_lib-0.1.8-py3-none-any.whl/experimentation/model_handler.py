import fire

from fathom_lib.pipeline_runner import PipelineRunner
from fathom_lib.experimentation.loggers import make_logger
from fathom_lib.validation.validation import *


class App:
    """
    Script for training and validating pipeline model. For help just type `python <this file name>`.

    params:
        logger: One of: 'PythonLogger', 'MlflowLogger'.
        logger_params: They are parameters specific to chosen logger. For details check out
            command help_on_loggers

    examples:
        python model_handler.py \
               --logger=PythonLogger \
               --directory=. \
               - \
               fit \
               --data_path=fathom_library/fathom/datasources/example_data.csv \
               --pipeline_path=model_7
        python model_handler.py \
               --logger=MlflowLogger \
               --port=5001 \
               - \
               validate \
               --data_path=fathom_library/fathom/datasources/example_data.csv \
               --pipeline_path=model_7 \
               --y_columns="next_failure_in_30_days" \
               --time_column="timestamp" \
               --train_cutoff_window_str="30 days" \
               --test_cutoff_window_str="30 days" \
               --model_type="classifier"
    """

    def __init__(self, logger="PythonLogger", **logger_params):
        self.logger = make_logger(logger, **logger_params)

    def validate(
        self,
        pipeline_path,
        data_path,
        y_columns,
        time_column,
        train_cutoff_window_str,
        test_cutoff_window_str,
        model_type,
    ):
        """
        # TODO: Pawel, mozesz tu dodac docstringa z opisem dzialania ten metody i opisem parametrow
        #       w formacie jak w metodzie fit?
        """

        pipeline, data = self._prepare_pipeline_and_data(pipeline_path, data_path)
        metrics = self._choose_metrics(model_type, y_columns)
        scores = expanding_window_validation(
            pipeline=pipeline,
            X=data,
            y_columns=y_columns,
            time_column=time_column,
            train_cutoff_window_str=train_cutoff_window_str,
            test_cutoff_window_str=test_cutoff_window_str,
            model_type=model_type,
            metrics=metrics,
        )
        figure = scores.pop("shap_feature_importance")
        self.logger.log_figure(figure)
        self.logger.log_metrics_and_params(metrics=scores, params=pipeline.get_params())

    def help_on_loggers(self):
        """
        Displays help on possible loggers. Use this if unsure what parameters need to be specified
        for each logger to work.
        """
        print(make_logger.__doc__)

    def fit(self, pipeline_path, data_path):
        """
        Fits the model.

        params:
            pipeline_path: path to pickled model which will be trained.
            data_path: path to the csv containing training data.
        """
        pipeline, data = self._prepare_pipeline_and_data(pipeline_path, data_path)
        pipeline.fit(data)
        self.logger.log_model(pipeline)
        self.logger.log_params(params=pipeline.get_params())

    @staticmethod
    def _prepare_pipeline_and_data(
        pipeline_path, data_path
    ):  # TODO: remove this after testing
        pipeline = PipelineRunner.load(pipeline_path)
        data = pd.read_csv(data_path)
        data = data.sample(2500, replace=True).fillna(
            0
        )  # TODO: I changed 25k to 2500 to test fast
        data["timestamp"] = pd.to_datetime(data["timestamp"] * 1_000_000)
        data = data.sort_values("timestamp")
        data.fillna(0, inplace=True)
        data["next_failure_in_30_days"] = (
            data["next_failure_in_30_days"].fillna(30) < 15
        )
        return pipeline, data

    @staticmethod
    def _choose_metrics(model_type, y_columns):
        # TODO: move it to script parameters after Pawel J. approves
        if model_type == "classifier":
            return ['SklearnMetrics(["roc_auc_score", "accuracy_score"])']
        elif model_type == "regressor":
            if isinstance(y_columns, list):
                return ["AftConcordanceIndex()", "AftAccuracy()"]
            else:
                return ['SklearnMetrics(["r2_score", "mean_squared_error"])']
        else:
            raise ValueError(
                "Incorrect value of parameter model_type. "
                "Allowed values are: 'regressor', 'classifier'"
            )


if __name__ == "__main__":
    fire.Fire(App)
