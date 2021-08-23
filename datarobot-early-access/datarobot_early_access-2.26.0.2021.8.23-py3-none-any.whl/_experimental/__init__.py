# flake8: noqa
# because the unused imports are on purpose

import logging

from .models.custom_training_blueprint import CustomTrainingBlueprint
from .models.custom_training_model import CustomTrainingModel
from .models.enums import UnsupervisedTypeEnum
from .models.idiomatic_project import IdiomaticProject
from .models.model import CombinedModel
from .models.model_package import ModelPackage
from .models.project import Project
from .models.restore_discarded_features import DiscardedFeaturesInfo
from .models.segmentation import Segment, SegmentationTask, SegmentInfo

logger = logging.getLogger(__package__)

experimental_warning = (
    "You have imported from the _experimental directory.\n"
    "This directory is used for unreleased datarobot features.\n"
    "Unless you specifically know better,"
    " you don't have the access to use this functionality in the app, so this code will not work."
)

logger.warning(experimental_warning)


class ClassMappingAggregationSettings(object):
    """ Class mapping aggregation settings.
    For multiclass projects allows fine control over which target values will be
    preserved as classes and which will be aggregated into a single "catch everything else" class.
    All attributes are optional, if not specified - server side defaults will be used.

    Attributes
    ----------
    max_unaggregated_class_values : int, optional
        Maximum amount of unique values allowed before aggregation kicks in.
    min_class_support : int, optional
        Minimum number of instances necessary for each target value in the dataset.
        All values with less instances will be aggregated.
    excluded_from_aggregation : list, optional
        List of target values that should be guaranteed to kept as is,
        regardless of other settings.
    aggregation_class_name : str, optional
        If some of the values will be aggregated - this is the name of the aggregation class
        that will replace them.
    """

    def __init__(
        self,
        max_unaggregated_class_values=None,
        min_class_support=None,
        excluded_from_aggregation=None,
        aggregation_class_name=None,
    ):
        self.max_unaggregated_class_values = max_unaggregated_class_values
        self.min_class_support = min_class_support
        self.excluded_from_aggregation = excluded_from_aggregation
        self.aggregation_class_name = aggregation_class_name

    def collect_payload(self):
        return {key: self.__dict__[key] for key in self.__dict__ if self.__dict__[key] is not None}
