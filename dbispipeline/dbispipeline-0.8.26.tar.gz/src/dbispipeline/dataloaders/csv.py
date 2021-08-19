"""Module containing csv dataloaders."""
from pandas import read_csv

from ..base import Loader
from ..base import TrainTestLoader
from ..base import TrainValidateTestLoader


class CsvLoader(Loader):
    """Loads a csv file."""

    def __init__(self, path, labels=None, **kwargs):
        """
        Creates a new instance.

        Args:
            path: the path to csv file (see pandas read_csv docs).
            labels: columns used as labels.
            kwargs: arguments that are passed to the pandas read_csv.
        """
        self.path = path
        self.labels = labels
        self.kwargs = kwargs

    def load(self):
        """
        Returns a tuple containing data and labels.

        Both are list-like if the labels argument is set. Ohterwise, the
        labels are None.
        """
        df = read_csv(filepath_or_buffer=self.path, **self.kwargs)

        if self.labels:
            return df.drop(columns=self.labels).values, df[self.labels].values

        else:
            return df.values, None

    @property
    def configuration(self):
        """Returns a dict-like representation of the configuration."""
        return {
            'path': self.path,
            'labels': self.labels,
            **self.kwargs,
        }


class CsvTrainTestLoader(TrainTestLoader):
    """Loader for train and test spilt csv."""

    def __init__(self, train_path, test_path, **kwargs):
        """
        Creates a new instance.

        Args:
            train_path: the path to train csv (see pandas read_csv docs).
            test_path: the path to test csv (see pandas read_csv docs).
            kwargs: arguments that are passed to the CsvLoader.
        """
        self.train_path = train_path
        self.test_path = test_path
        self.kwargs = kwargs

    def load_train(self):
        """Loads the data contained in the train csv file."""
        return CsvLoader(path=self.train_path, **self.kwargs).load()

    def load_test(self):
        """Loads the data contained in the test csv file."""
        return CsvLoader(path=self.test_path, **self.kwargs).load()

    @property
    def configuration(self):
        """Returns a dict-like representation of the configuration."""
        return {
            'train_path': self.train_path,
            'test_path': self.test_path,
            **self.kwargs,
        }


class CsvTrainValidateTestLoader(TrainValidateTestLoader, CsvTrainTestLoader):
    """Loader for train and test spilt csv."""

    def __init__(self, train_path, validate_path, test_path, **kwargs):
        """
        Creates a new instance.

        Args:
            train_path: the path to train csv (see pandas read_csv docs).
            validate_path: the path to validate csv (see pandas read_csv docs).
            test_path: the path to test csv (see pandas read_csv docs).
            kwargs: arguments that are passed to the CsvLoader.
        """
        self.train_path = train_path
        self.validate_path = validate_path
        self.test_path = test_path
        self.kwargs = kwargs

    def load_validate(self):
        """Loads the data contained in the validate csv file."""
        return CsvLoader(path=self.validate_path, **self.kwargs).load()

    @property
    def configuration(self):
        """Returns a dict-like representation of the configuration."""
        return {
            'train_path': self.train_path,
            'validate_path': self.validate_path,
            'test_path': self.test_path,
            **self.kwargs,
        }
