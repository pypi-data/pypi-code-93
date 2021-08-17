from unittest.mock import MagicMock

import pandas as pd

from azureml.core import Dataset as AmlDataset
from azureml.data import FileDataset
from azureml.dataprep.native import StreamInfo

try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


class MockExperiment:
    def __init__(self):
        self.workspace = "some_workspace"


class MockRun:
    def __init__(self):
        self.metrics = {}
        self.properties = {}
        self.id = 'mock_run_id'

    @property
    def experiment(self):
        return self

    @property
    def workspace(self):
        return self

    @property
    def parent(self):
        return self

    def log(self, metric_name, metric_val):
        self.metrics[metric_name] = metric_val

    def RaiseError(self):
        raise ValueError()


class MockLabelingRun:
    def __init__(self):
        self.metrics = {}
        self.properties = {'azureml.runsource': 'Labeling'}
        self.id = 'mock_run_id'

    @property
    def experiment(self):
        return self

    @property
    def workspace(self):
        workspace_mock = MockWorkspace()
        return workspace_mock

    @property
    def parent(self):
        return self

    def log(self, metric_name, metric_val):
        self.metrics[metric_name] = metric_val

    def download_file(self, name, output_file_path=None, _validate_checksum=False):
        return None

    def RaiseError(self):
        raise ValueError()


class MockWorkspace:
    def __init__(self):
        self.metrics = {}

    @property
    def datastores(self):
        datastore_mock = MagicMock()
        return {'datastore': datastore_mock, 'ner_data': datastore_mock}


class MockBertClass(torch.nn.Module):
    def __init__(self, num_labels):
        super(MockBertClass, self).__init__()
        self.num_labels = num_labels
        self.l1 = torch.nn.Linear(num_labels, num_labels)
        # number of times forward was called
        self.forward_called = 0
        self.train_called = False
        self.eval_called = False
        return

    def forward(self, ids, attention_mask, token_type_ids):
        self.forward_called = self.forward_called + 1
        return self.l1(torch.randn(ids.shape[0], self.num_labels))

    def train(self, mode=True):
        self.train_called = True
        super().train(mode)

    def eval(self):
        self.eval_called = True
        super().eval()


def file_dataset_mock():
    dataset_mock = MagicMock(FileDataset)
    dataset_mock.download.return_value = MagicMock()
    dataset_mock.to_path.side_effect = [["/train.txt"], ["/dev.txt"]]
    return dataset_mock


def ner_trainer_mock():
    mock_trainer = MagicMock()
    mock_trainer.is_world_process_zero.return_value = True
    mock_trainer_result = MagicMock()
    mock_trainer_result.metrics.return_value = {"result_key": "result_value"}
    mock_trainer.train.return_value = mock_trainer_result
    mock_trainer.evaluate.return_value = {"eval_f1": 0.21, "eval_accuracy": 0.85}
    return mock_trainer


def multiclass_trainer_mock():
    mock_trainer = MagicMock()
    mock_trainer.is_world_process_zero.return_value = True
    mock_trainer_result = MagicMock()
    mock_trainer_result.metrics.return_value = {"result_key": "result_value"}
    mock_trainer.train.return_value = mock_trainer_result
    mock_trainer.evaluate.return_value = {"eval_accuracy": 0.56}
    return mock_trainer


def aml_dataset_mock(input_df):
    dataset_mock = MagicMock(AmlDataset)
    dataset_mock.to_pandas_dataframe.return_value = input_df
    return dataset_mock


def get_labeling_df():
    dataset_df = pd.DataFrame()
    dataset_df['image_url'] = [
        StreamInfo(
            arguments={'datastoreName': 'ner_data'},
            handler='AmlDatastore',
            resource_identifier='sample1.txt'),
        StreamInfo(
            arguments={'datastoreName': 'ner_data'},
            handler='AmlDatastore',
            resource_identifier='sample2.txt')
    ]
    dataset_df['label'] = [
        [
            {'label': 'LOC', 'offsetStart': 20, 'offsetEnd': 25},
            {'label': 'LOC', 'offsetStart': 53, 'offsetEnd': 63},
            {'label': 'PER', 'offsetStart': 85, 'offsetEnd': 94}
        ],
        [
            {'label': 'PER', 'offsetStart': 0, 'offsetEnd': 14}
        ]
    ]
    dataset_df['label_confidence'] = [
        [1.0, 1.0, 1.0],
        [1.0]
    ]

    return dataset_df
