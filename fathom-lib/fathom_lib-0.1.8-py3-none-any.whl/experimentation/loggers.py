import base64
import json
import os
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime
from io import BytesIO
from pprint import pprint
from typing import Optional

import mlflow
from PIL import Image
import pandas as pd

from fathom_lib.pipeline_runner import PipelineRunner, Picklable
from fathom_lib.utils import flatten, add_docs_from


class Logger(ABC):
    @abstractmethod
    def log_params(self, params: dict):
        pass

    @abstractmethod
    def log_metrics_and_params(self, metrics: dict, params: dict):
        pass

    @abstractmethod
    def log_model(self, model):
        pass

    @abstractmethod
    def log_figure(self, figure):
        pass

    @abstractmethod
    def log_plot(self, figure, file_name):
        pass

    @abstractmethod
    def log_text_artifact(self, content, filename):
        """
        Can save any text data csv, html, txt, etc
        :param content:
        :param filename:
        :return:
        """
        pass


class PythonLogger(Logger):
    """
    Simple logger used to log to console and save files to disk.

    params:
        directory: a directory in which the stuff (model, metrics, figures, ...) will be saved
    """

    def __init__(self, directory: str = "."):
        self.directory = directory

    def log_metrics(self, metrics):
        metrics_to_save = {
            str(timestamp): value for timestamp, value in metrics.items()
        }
        self._log_dict(metrics_to_save, "metrics.json")

    def log_params(self, params: dict):
        self._log_dict(params, "params.json")

    def log_metrics_and_params(self, metrics: dict, params: dict):
        self.log_metrics(metrics)
        self.log_params(params)

    def log_model(self, model: Picklable):
        model.save(os.path.join(self.directory, "model_fitted"))

    def log_figure(self, figure):
        image = Image.open(BytesIO(base64.b64decode(figure)))
        # image.show()
        path = os.path.join(self.directory, "shap.png")
        image.save(path)
        print(f"Figure saved to {path}")

    def log_plot(self, figure, filename):
        path = os.path.join(self.directory, filename)
        with open(path, "wb") as out:
            out.write(figure.read())
        print(f"Figure saved to {path}")

    def log_text_artifact(self, content, filename):
        path = os.path.join(self.directory, filename)
        with open(path, "wt") as out:
            out.write(content)
        print(f"Saved {filename}")

    def _log_dict(self, dct: dict, name: str):
        pprint(dct)
        path = os.path.join(self.directory, name)
        with open(path, "w") as file:
            json.dump(dct, file, indent=4)
        print(f"Saved {path}")


class MlflowLogger(Logger):
    """
    Mlflow logger that logs stuff (model, metrics, figures, ...) to MLflow server.
    Note that the server should already be running when using this class.

    params:
        tracking_uri: URI of mlflow tracking server e.g. http://localhost:8010/
        experiment_name: the name of experiment in which the stuff should be logged. By default
            the logger logs to the default experiment.
    """

    MLFLOW_MODEL_PATH = "Model"
    PICKLE_MODEL_FILENAME = "model.pkl"

    def __init__(
        self, tracking_uri="http://localhost:8010/", experiment_name: str = None
    ):
        mlflow.set_tracking_uri(tracking_uri)
        # for now always create the experiment because the run is not finishing
        # TODO: fix this
        mlflow.end_run()
        self.experiment_id = mlflow.create_experiment(
            f"{experiment_name} {datetime.now()}"
        )
        # self.experiment_id = self._get_or_create_experiment(experiment_name)
        mlflow.start_run(experiment_id=self.experiment_id)

    def log_params(self, params: dict):
        mlflow.log_params(params)

    def log_metrics_and_params(self, metrics: dict, params: dict):
        # This cannot be done using log_metrics and log_params methods, because of complications
        # with nested run. If one tries to do that, it will be impossible to plot scores vs params
        # in mlflow ui. This problem is because multiple metric log from rolling validation vs
        # single parameter set for all steps in that validation.
        self.log_params(params)  # log to superrun too
        self._log_run_date()
        mlflow.log_metrics(self._compute_mean_metrics(metrics))
        for test_set_beginning_timestamp, metrics_dict in metrics.items():
            with mlflow.start_run(
                run_name=self._make_run_name(test_set_beginning_timestamp),
                experiment_id=self.experiment_id,
                nested=True,
            ):
                self._log_test_set_start_date(test_set_beginning_timestamp)
                self._log_run_date()
                self.log_params(params)
                mlflow.log_metrics(flatten(metrics_dict))

    def log_model(self, model: Picklable):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, self.PICKLE_MODEL_FILENAME)
            model.save(path)
            mlflow.log_artifact(path)
            context_pickle_model_path_key = "model_pickle_path"
            artifacts = {
                context_pickle_model_path_key: mlflow.get_artifact_uri(
                    self.PICKLE_MODEL_FILENAME
                )
            }
            mlflow.pyfunc.log_model(
                self.MLFLOW_MODEL_PATH,
                python_model=self._make_model_wrapper(context_pickle_model_path_key),
                artifacts=artifacts,
            )
            # Log pickle again (workaround because of some mlflow internal problems):
            mlflow.log_artifact(path, f"{self.MLFLOW_MODEL_PATH}/artifacts")

    def log_text_artifact(self, content, filename):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, filename)
            with open(path, "wt") as out:
                out.write(content)
            mlflow.log_artifact(path)

    @staticmethod
    def _make_model_wrapper(context_pickle_model_path_key: str):
        class ModelWrapper(mlflow.pyfunc.PythonModel):
            def load_context(self, context):
                path = context.artifacts[context_pickle_model_path_key]
                self.pipeline = PipelineRunner.load(path)

            def predict(self, context, model_input):
                return self.pipeline.predict(model_input)

        return ModelWrapper()

    def log_figure(self, figure):
        with tempfile.TemporaryDirectory() as directory:
            image = Image.open(BytesIO(base64.b64decode(figure)))
            path = os.path.join(directory, "shap.png")
            image.save(path)
            mlflow.log_artifact(path)

    def log_plot(self, figure, filename):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, filename)
            with open(path, "wb") as out:
                out.write(figure.read())
            mlflow.log_artifact(path)

    def _log_test_set_start_date(self, timestamp):
        mlflow.log_param("_test_set_start_date", timestamp)

    def _compute_mean_metrics(self, metrics: dict) -> dict:
        rows = [flatten(metrics_dict) for metrics_dict in metrics.values()]
        return pd.DataFrame.from_records(rows).mean().to_dict()

    def _log_run_date(self):
        mlflow.log_param("_run_date", datetime.today())

    def _get_or_create_experiment(self, experiment_name: Optional[str]) -> int:
        if experiment_name is None:
            experiment_name = "Default"
        existing_experiment = mlflow.get_experiment_by_name(experiment_name)
        if existing_experiment is None:
            return mlflow.create_experiment(experiment_name)
        else:
            return existing_experiment.experiment_id

    def _make_run_name(self, date):
        print(type(date), date)
        try:
            return date.strftime("%d %b %Y")
        except:
            return str(datetime.now())


@add_docs_from(PythonLogger, MlflowLogger)
def make_logger(type: str, **params) -> Logger:
    """This function is used as a logger factory. See loggers details below."""
    if type == "PythonLogger":
        return PythonLogger(**params)
    elif type == "MlflowLogger":
        return MlflowLogger(**params)
    else:
        raise ValueError("Incorrect model type.")
