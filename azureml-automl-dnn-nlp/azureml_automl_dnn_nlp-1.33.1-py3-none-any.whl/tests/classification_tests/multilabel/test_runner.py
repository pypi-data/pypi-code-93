import pytest
import unittest
from unittest.mock import patch
import importlib

from azureml.automl.dnn.nlp.classification.multilabel import runner

horovod_spec = importlib.util.find_spec("horovod")
has_horovod = horovod_spec is not None


class MockExperiment:

    def __init__(self):
        self.workspace = "some_workspace"


class MockRun:

    def __init__(self):
        self.experiment = MockExperiment()
        self.metrics = {}
        self.duplicate_metric_logged = False

    def log(self, key, value):
        if key in self.metrics.keys():
            self.duplicate_metric_logged = True
        self.metrics[key] = value

    def get_environment(self):
        return "some_environment"


class MockTrainingSet:

    def __init__(self):
        self.tokenizer = "some_tokenizer"


class MockTrainer:

    def __init__(self):
        self.n_train_called = 0
        self.train_called_last_with = None
        self.n_compute_called = 0
        self.compute_called_with = None
        self.tokenizer = "some_tokenizer"

    def train(self, train_dataset):
        self.n_train_called = self.n_train_called + 1
        self.train_called_last_with = train_dataset
        return "some_model"

    def compute_metrics(self, valid_dataset):
        self.n_compute_called = self.n_compute_called + 1
        self.compute_called_with = valid_dataset
        return 0.5, 0.6, 0.7


class MockAutoMLSettings:
    def __init__(self, distributed, label_column_name):
        self.is_gpu = True
        self.dataset_id = "some_dataset_id"
        self.validation_dataset_id = "some_validation_dataset_id"
        self.label_column_name = label_column_name
        self.enable_distributed_dnn_training = distributed


def test_runner():
    automl_settings = {"is_gpu": True,
                       "dataset_id": "some_training_set",
                       "validation_dataset_id": "some_validation_set",
                       "label_column_name": "labels",
                       "enable_distributed_dnn_training": False}

    mock_run = MockRun()
    mocked_trainer = MockTrainer()
    mocked_training_set = MockTrainingSet()

    model_wrapper_init = "azureml.automl.dnn.nlp.classification.multilabel.model_wrapper.ModelWrapper.__init__"
    save_model_path = "azureml.automl.dnn.nlp.classification.io.write.save_utils.save_model_wrapper"
    with patch("azureml.core.run.Run.get_context", return_value=mock_run):
        dataset_loader_patch = "azureml.automl.dnn.nlp.classification.io.read.dataloader.dataset_loader"
        dataset_loader_return = (mocked_training_set, "some_validation_set", 3, "some_vectorizer")
        with patch("azureml.automl.dnn.nlp.common.utils.prepare_run_properties") as mock_prepare_run_properties:
            with patch(dataset_loader_patch, return_value=dataset_loader_return):
                parse_settings_path = "azureml.train.automl.runtime._entrypoints.utils.common.parse_settings"
                with patch(parse_settings_path, return_value=MockAutoMLSettings(False, "labels")):
                    trainer_init = "azureml.automl.dnn.nlp.classification.multilabel.runner.PytorchTrainer"
                    with patch(trainer_init, return_value=mocked_trainer):
                        with patch(model_wrapper_init, return_value=None):
                            with patch("azureml.automl.dnn.nlp.common.utils.prepare_post_run_properties"):
                                with patch(save_model_path):
                                    with patch("azureml.automl.dnn.nlp.common.utils.save_conda_yml"):
                                        runner.run(automl_settings)

    mock_prepare_run_properties.assert_called()

    assert mocked_trainer.train_called_last_with == mocked_training_set
    assert mocked_trainer.compute_called_with == "some_validation_set"

    assert mocked_trainer.n_train_called == 1
    assert mocked_trainer.n_compute_called == 1

    assert mock_run.metrics["accuracy"] == 0.5
    assert mock_run.metrics["f1_score_micro"] == 0.6
    assert mock_run.metrics["f1_score_macro"] == 0.7


def test_runner_without_label_col():
    automl_settings = {"is_gpu": True,
                       "dataset_id": "some_training_set",
                       "validation_dataset_id": "some_validation_set",
                       "label_column_name": None,
                       "enable_distributed_dnn_training": False}

    mock_run = MockRun()
    mocked_trainer = MockTrainer()

    with patch("azureml.core.run.Run.get_context", return_value=mock_run):
        dataset_loader_patch = "azureml.automl.dnn.nlp.classification.io.read.dataloader.dataset_loader"
        dataset_loader_return = ("some_training_set", "some_validation_set", 3, "some_vectorizer")
        with patch("azureml.automl.dnn.nlp.common.utils.prepare_run_properties"):
            with patch(dataset_loader_patch, return_value=dataset_loader_return):
                parse_settings_path = "azureml.train.automl.runtime._entrypoints.utils.common.parse_settings"
                with patch(parse_settings_path, return_value=MockAutoMLSettings(False, None)):
                    trainer_init = "azureml.automl.dnn.nlp.classification.multilabel.runner.PytorchTrainer"
                    with patch(trainer_init, return_value=mocked_trainer):
                        with pytest.raises(BaseException):
                            runner.run(automl_settings)
    # An exception is raised and none of the trainer code gets executed
    assert mocked_trainer.train_called_last_with is None
    assert mocked_trainer.compute_called_with is None
    assert mocked_trainer.n_train_called == 0
    assert mocked_trainer.n_compute_called == 0
    assert mock_run.metrics == {}


@unittest.skipIf(not has_horovod, "Horovod not installed")
@pytest.mark.parametrize('is_main_process, enable_distributed',
                         [pytest.param(True, True),
                          pytest.param(False, True),
                          pytest.param(True, False)])
def test_runner_distributed(is_main_process, enable_distributed):
    automl_settings = {"is_gpu": True,
                       "dataset_id": "some_training_set",
                       "validation_dataset_id": "some_validation_set",
                       "label_column_name": "labels",
                       "enable_distributed_dnn_training": True}

    mock_run = MockRun()
    mocked_pytorch_trainer = MockTrainer()
    mocked_distributed_trainer = MockTrainer()
    mocked_training_set = MockTrainingSet()

    model_wrapper_init = "azureml.automl.dnn.nlp.classification.multilabel.model_wrapper.ModelWrapper.__init__"
    save_model_path = "azureml.automl.dnn.nlp.classification.io.write.save_utils.save_model_wrapper"
    with patch("azureml.core.run.Run.get_context", return_value=mock_run):
        dataset_loader_patch = "azureml.automl.dnn.nlp.classification.io.read.dataloader.dataset_loader"
        dataset_loader_return = (mocked_training_set, "some_validation_set", 3, "some_vectorizer")
        with patch(dataset_loader_patch, return_value=dataset_loader_return):
            parse_settings_path = "azureml.train.automl.runtime._entrypoints.utils.common.parse_settings"
            with patch(parse_settings_path, return_value=MockAutoMLSettings(enable_distributed, "labels")):
                trainer_init = "azureml.automl.dnn.nlp.classification.multilabel.runner.PytorchTrainer"
                distributed_init = "azureml.automl.dnn.nlp.classification.multilabel.runner.HorovodDistributedTrainer"
                with patch("azureml.automl.dnn.nlp.common.utils.is_main_process", return_value=is_main_process):
                    with patch(trainer_init, return_value=mocked_pytorch_trainer):
                        with patch(distributed_init, return_value=mocked_distributed_trainer):
                            with patch(model_wrapper_init, return_value=None):
                                with patch("azureml.automl.dnn.nlp.common.utils.prepare_run_properties"):
                                    with patch("azureml.automl.dnn.nlp.common.utils.prepare_post_run_properties"):
                                        with patch("azureml.automl.dnn.nlp.common.utils.save_conda_yml"):
                                            with patch(save_model_path):
                                                runner.run(automl_settings)

    if enable_distributed:
        assert mocked_pytorch_trainer.n_train_called == 0
        assert mocked_pytorch_trainer.n_compute_called == 0
        assert mocked_distributed_trainer.n_train_called == 1

        if is_main_process:
            assert mocked_distributed_trainer.n_compute_called == 1
        else:
            assert mocked_distributed_trainer.n_compute_called == 0
    else:
        assert mocked_pytorch_trainer.n_train_called == 1
        assert mocked_pytorch_trainer.n_compute_called == 1
        assert mocked_distributed_trainer.n_train_called == 0
        assert mocked_distributed_trainer.n_compute_called == 0
