"""Base classes for the dbispipeline."""
from abc import ABC
from abc import abstractmethod


class Loader(ABC):
    """Abstract base class of a dataloader."""

    @abstractmethod
    def load(self):
        """Returns the data loaded by the dataloader."""
        pass

    @property
    @abstractmethod
    def configuration(self):
        """Returns a dict-like representation of the configuration."""
        pass

    @property
    def run_count(self):
        """Returns how many configurations this dataloader will produce."""
        return 1

    @property
    def is_multiloader(self):
        """Returns if this dataloader will produce multiple configurations."""
        return self.run_count > 1


class TrainTestLoader(Loader):
    """Abstract dataloader with explicit train and test data."""

    @abstractmethod
    def load_train(self):
        """Returns the train data."""
        pass

    @abstractmethod
    def load_test(self):
        """Returns the test data."""
        pass

    def load(self):
        """Returns the data as a train, test tuple."""
        return self.load_train(), self.load_test()


class TrainValidateTestLoader(TrainTestLoader):
    """Abstract dataloader with explicit train, validation and test data."""

    @abstractmethod
    def load_validate(self):
        """Returns the validation data."""
        pass

    def load(self):
        """Returns the data as a train, validation, test tuple."""
        return self.load_train(), self.load_validate(), self.load_test()


class Evaluator(ABC):
    """Abstract base class of an evaluator."""

    @abstractmethod
    def evaluate(self, model, data):
        """
        Evaluates the pipeline based on the given dataset.

        Args:
            model: the model given in the pipeline.
            data: the data used for evaluation/training.

        Returns: An dict result.
        """
        pass

    @property
    @abstractmethod
    def configuration(self):
        """Returns a dict-like representation of this loader.

        This is for storing its state in the database.
        """
        pass

    def _check_loader_methods(self, loader, methods=None):

        if type(methods) == str:
            methods = [methods]

        for method in methods:
            m = getattr(loader, method, None)
            if not callable(m):
                raise ValueError(
                    f'The dataloader {loader} does not implement'
                    'the required method {m}. Required methods are: '
                    '{methods}')


class StorageHandler(ABC):
    """Abstract base class of a storage handler."""

    @abstractmethod
    def handle_result(self, result):
        """
        Handles the result of an evaluator.

        Args:
            result: passed from an evaluator.
        """
        pass
