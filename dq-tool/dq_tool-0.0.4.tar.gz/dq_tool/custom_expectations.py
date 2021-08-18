"""Classes related to defining custom expectations"""
from great_expectations.dataset.sparkdf_dataset import MetaSparkDFDataset
from .expressions import SparkDFDatasetExpectations


class SparkDecorators(MetaSparkDFDataset):
    """A class that holds decorators for custom expectation methods"""


class BaseSparkExpectations(SparkDFDatasetExpectations):
    """A class to subclass to define your custom expectations as methods"""
