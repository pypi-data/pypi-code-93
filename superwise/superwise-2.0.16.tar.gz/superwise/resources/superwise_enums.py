from enum import Enum


class DataTypesRoles(Enum):
    """ Enum of Roles"""

    ID = "id"
    TIMESTAMP = "time stamp"
    FEATURE = "feature"
    PREDICTION_PROBABILITY = "prediction probability"
    PREDICTION_VALUE = "prediction value"
    LABEL = "label"
    LABEL_TIMESTAMP = "label time stamp"
    LABEL_WEIGHT = "label weight"
    METADATA = "metadata"


class TaskTypes(Enum):
    """ Enum of DataTypes"""

    BINARY_CLASSIFICATION = "Binary Classification"
    BINARY_ESTIMATION = "Binary Estimation"
    REGRESSION = "Regression"
    MULTICLASS_CLASSIFICATION = "Multiclass Classification"


class FeatureType(Enum):
    """ Enum of FeatureType"""

    NUMERIC = "Numeric"
    BOOLEAN = "Boolean"
    CATEGORICAL = "Categorical"
    TIMESTAMP = "Timestamp"
    UNKNOWN = "Unknown"


class CategoricalSecondaryType(Enum):
    CONSTANT = "Cat_constant"
    DENSE = "Cat_dense"
    SPARSE = "Cat_sparse"


class NumericSecondaryType(Enum):
    NUM_RIGHT_TAIL = "Num_right_tail"
    NUM_LEFT_TAIL = "Num_left_tail"
    NUM_CENTERED = "Num_centered"


class BooleanSecondaryType(Enum):
    FLAG = "Boolean_flag"
    NUMERIC = "Boolean_numeric"
