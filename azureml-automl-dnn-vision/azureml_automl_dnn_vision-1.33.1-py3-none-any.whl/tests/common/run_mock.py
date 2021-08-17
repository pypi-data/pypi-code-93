import collections

from azureml.core import Environment
from azureml.automl.dnn.vision.common.utils import _pad
from azureml.automl.dnn.vision.classification.io.read.dataset_wrappers import BaseDatasetWrapper
from azureml.automl.dnn.vision.object_detection.data.datasets import ObjectDetectionDatasetBaseWrapper


class RunMock:

    def __init__(self, exp):
        self.experiment = exp
        self.metrics = {}
        self.properties = {}
        self.id = 'mock_run_id'

    def add_properties(self, properties):
        self.properties.update(properties)

    def log(self, metric_name, metric_val):
        self.metrics[metric_name] = metric_val

    def get_environment(self):
        return Environment('test_env')


class ExperimentMock:

    def __init__(self, ws):
        self.workspace = ws


class WorkspaceMock:

    def __init__(self, datastore):
        self._datastore = datastore

    def get_default_datastore(self):
        return self._datastore


class DatastoreMock:

    def __init__(self, name):
        self.name = name
        self.files = []
        self.dataset_file_content = []

    def reset(self):
        self.files = []
        self.dataset_file_content = []

    def path(self, file_path):
        return file_path

    def upload_files(self, files, relative_root=None, target_path=None, overwrite=False):
        self.files.append((files, relative_root, target_path, overwrite))
        if len(files) == 1:
            with open(files[0], "r") as f:
                self.dataset_file_content = f.readlines()


class DatasetMock:

    def __init__(self, id):
        self.id = id


class LabeledDatasetFactoryMock:

    def __init__(self, dataset_id):
        self.task = ""
        self.path = ""
        self.dataset_id = dataset_id

    def from_json_lines(self, task, path):
        self.task = task
        self.path = path
        return DatasetMock(self.dataset_id)


class DatasetWrapperMock(ObjectDetectionDatasetBaseWrapper):

    def __init__(self, items, num_classes):
        self._items = items
        self._num_classes = num_classes
        self._classes = ["label_{}".format(i) for i in range(self._num_classes)]
        self._label_to_index_map = {i: self._classes[i] for i in range(self._num_classes)}

    def __getitem__(self, index):
        return self._items[index]

    def __len__(self):
        return len(self._items)

    @property
    def num_classes(self):
        return self._num_classes

    def label_to_index_map(self, label):
        return self._label_to_index_map[label]

    def index_to_label(self, index):
        return self._classes[index]

    @property
    def classes(self):
        return self._classes

    def prepare_image_targets_for_eval(self, image_targets, height, width):
        return image_targets


class ClassificationDatasetWrapperMock(BaseDatasetWrapper):
    def __init__(self, items, num_classes):
        self._num_classes = num_classes
        self._priv_labels = ["label_{}".format(i) for i in range(self._num_classes)]
        self._label_freq_dict = collections.defaultdict(int)
        for key in self._priv_labels:
            self._label_freq_dict[key] += 1
        self._items = items
        super().__init__(label_freq_dict=self._label_freq_dict, labels=self._priv_labels)

    def __len__(self):
        return len(self._items)

    def pad(self, padding_factor):
        self._items = _pad(self._items, padding_factor)

    def item_at_index(self, idx):
        return self._items[idx]

    def label_at_index(self, idx):
        return self._priv_labels[idx % self._num_classes]

    @property
    def label_freq_dict(self):
        return self._label_freq_dict
