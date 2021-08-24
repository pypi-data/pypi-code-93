import logging
import os

import numpy as np
import pandas as pd
import scipy.stats

from superwise.resources.superwise_enums import BooleanSecondaryType
from superwise.resources.superwise_enums import CategoricalSecondaryType
from superwise.resources.superwise_enums import DataTypesRoles
from superwise.resources.superwise_enums import FeatureType
from superwise.resources.superwise_enums import NumericSecondaryType
from superwise.resources.superwise_enums import TaskTypes

logger = logging.getLogger(__name__)


def compute_secondary_numeric(skewness):
    if skewness > 2:
        return NumericSecondaryType.NUM_RIGHT_TAIL.value
    if skewness > -2:
        return NumericSecondaryType.NUM_CENTERED.value
    return NumericSecondaryType.NUM_LEFT_TAIL.value


def compute_secondary_categorical(row):
    if row["num_unique"] == 1:
        return CategoricalSecondaryType.CONSTANT.value
    if row["num_unique"] < 250:
        return CategoricalSecondaryType.DENSE.value
    return CategoricalSecondaryType.SPARSE.value


def compute_secondary_boolean(row):
    if pd.api.types.is_numeric_dtype(row["pandas_type"]):
        return BooleanSecondaryType.NUMERIC.value
    else:
        return BooleanSecondaryType.FLAG.value


class EntitiesValidationError(RuntimeError):
    def __init__(self, reason):
        super(EntitiesValidationError, self).__init__(reason)
        self.reason = reason


class EntitiesValidator:
    def __init__(self, task, version_entities_df, data, MAX_DIMENSIONS=None):
        """
            version_entities_df
                name | type | role | is_dimension
            task
                task_type_id
                label -> mapper of external to internal
                prediction -> mapper of external to internal
        """
        self.MAX_DIMENSIONS = MAX_DIMENSIONS or int(os.environ.get("MAX_DIMENSIONS", 10))
        self._version_entities_df = version_entities_df
        self._task = task
        self._data = data

    def _assert_type(self, column, column_description, expected_type):
        column_version_entities = self._version_entities_df[self._version_entities_df["name"] == column].iloc[0]
        if column_version_entities["type"] != expected_type:
            error_msg = (
                f"Column {column} ({column_description}) has type {column_version_entities['type']} "
                f"but type {expected_type} is required"
            )
            raise EntitiesValidationError(error_msg)

    @staticmethod
    def assert_range(data, column, column_description, expected_min, expected_max):
        minimum = data[column["name"]].min()
        maximum = data[column["name"]].max()
        if minimum < expected_min or maximum > expected_max:
            error_msg = (
                f"column={column['name']} ({column_description}) has values ranging from "
                f"{minimum} to {maximum} whereas {expected_min} to {expected_max} is expected"
            )
            raise EntitiesValidationError(error_msg)

    @staticmethod
    def _assert_not_null(data, column, column_description):
        if data[column].isna().any():
            error_msg = "Column {} ({}) has null values".format(column, column_description)
            raise EntitiesValidationError(error_msg)

    @staticmethod
    def _assert_not_empty(data, column, column_description):
        if data[column].isna().all():
            error_msg = f"Column {column} ({column_description}) has all null values"
            raise EntitiesValidationError(error_msg)

    @staticmethod
    def _assert_subset(set_a, set_a_description, set_b, set_b_description):
        """
            asserts a is a subset of b
        """
        diff = set_a - set_b
        if diff:
            error_msg = (
                f"These columns exist in {set_a_description} but are missing from {set_b_description}: "
                f"{','.join(map(str, diff))}"
            )
            raise EntitiesValidationError(error_msg)

    def _is_valid_record_id(self):
        id_column = self._version_entities_df[self._version_entities_df["role"] == "id"]
        if len(id_column) > 1:
            raise Exception("more then one entity with role = id")
        elif len(id_column) == 0:
            raise Exception("Record id col is missing")

        id_column = id_column.iloc[0]["name"]
        if not self._data[id_column].is_unique:
            error_msg = f"Column {id_column} is marked as role ID but has duplicated values"
            raise EntitiesValidationError(error_msg)

    def _is_valid_label_weight(self):
        label_weight_col = self._version_entities_df["role"] == DataTypesRoles.LABEL_WEIGHT.value
        label_weight_size = label_weight_col.sum()
        if label_weight_size > 1:
            raise EntitiesValidationError("more then one ({}) label weight entity".format(label_weight_size))
        elif label_weight_size:
            label_weight_df = self._version_entities_df[label_weight_col].iloc[0]["name"]
            self._assert_type(label_weight_df, "label weight", FeatureType.NUMERIC.value)
            self._data["label_weight"] = self._data["label_weight"].fillna(1).astype(float)
        else:
            self._data["label_weight"] = 1

    def _version_entities_has_not_reserved_names(self):
        reserved_names = ["task_id", "version_id"]
        reserved_words_used = self._version_entities_df[self._version_entities_df["name"].isin(reserved_names)][
            "name"
        ].tolist()
        if reserved_words_used:
            error_msg = f"version_entities contains reserved words {','.join(reserved_words_used)}"
            raise EntitiesValidationError(error_msg)

    def _has_all_required_roles(self):
        existing_role = set(self._version_entities_df["role"].unique())
        required_roles = set([DataTypesRoles.ID.value, DataTypesRoles.TIMESTAMP.value])
        self._assert_subset(required_roles, "required roles", existing_role, "existing roles")

    def _column_names_match_version_entities(self):
        data_feature_names = set(self._data.columns)
        version_entities_feature_names = set(self._version_entities_df["name"].tolist())
        self._assert_subset(data_feature_names, "data", version_entities_feature_names, "version_entities")
        self._assert_subset(version_entities_feature_names, "version_entities", data_feature_names, "data")

    def _is_valid_dimension_ts_count(self):
        df = self._version_entities_df
        cnt = len(df[~df["dimension_start_ts"].isnull()])
        if cnt > self.MAX_DIMENSIONS:
            error_msg = f"Maximum allowed dimensions is {self.MAX_DIMENSIONS}. You requested {cnt}"
            raise EntitiesValidationError(error_msg)

    def _is_valid_dimension(self):
        dimensions = self._version_entities_df[~self._version_entities_df["dimension_start_ts"].isnull()][
            "name"
        ].tolist()
        for dimension in dimensions:
            self._assert_type(dimension, "dimension", FeatureType.CATEGORICAL.value)

    def _is_valid_label(self):
        label_col = self._version_entities_df["role"] == DataTypesRoles.LABEL.value
        if self._task.task_type == TaskTypes.REGRESSION.value:
            invalid_feature_type_col = self._version_entities_df[label_col]["type"] != FeatureType.NUMERIC.value
        else:
            invalid_feature_type_col = (
                self._version_entities_df[label_col]["type"].isin(
                    [FeatureType.CATEGORICAL.value, FeatureType.BOOLEAN.value]
                )
                == False
            )
        if len(self._version_entities_df[label_col][invalid_feature_type_col]) > 0:
            raise Exception("invalid feature type")
        return True

    def _is_valid_prediction_value(self):
        pred_val_col = self._version_entities_df["role"] == DataTypesRoles.PREDICTION_VALUE.value
        if self._task.task_type == TaskTypes.REGRESSION.value:
            invalid_feature_type_col = self._version_entities_df[pred_val_col]["type"] != FeatureType.NUMERIC.value
        else:
            invalid_feature_type_col = (
                self._version_entities_df[pred_val_col]["type"].isin(
                    [FeatureType.CATEGORICAL.value, FeatureType.BOOLEAN.value]
                )
                == False
            )
        if len(self._version_entities_df[pred_val_col][invalid_feature_type_col]) > 0:
            raise Exception("invalid feature type")
        return True

    def _is_valid_prediction_probability(self):
        columns = self._version_entities_df[self._version_entities_df["role"] == "prediction probability"]
        for idx, column in columns.iterrows():
            self._assert_type(column["name"], "prediction probability", FeatureType.NUMERIC.value)
            self._assert_not_null(self._data, column["name"], "prediction_probability")
            self.assert_range(self._data, column, "prediction probability", 0, 1)

    def _is_valid_prediction_ts(self):
        column = self._version_entities_df[self._version_entities_df["role"] == "time stamp"]
        if len(column) > 1:
            raise EntitiesValidationError("more then one entity with role 'time stamp'")
        column = column.iloc[0]
        self._assert_type(column["name"], "prediction time stamp", FeatureType.TIMESTAMP.value)
        self._assert_not_null(self._data, column["name"], "prediction time stamp")

    def _is_valid_label_ts(self):
        column = self._version_entities_df[self._version_entities_df["role"] == "label time stamp"]
        if len(column) > 1:
            raise EntitiesValidationError("only one 'label time stamp' entity allowed")
        elif len(column) == 0:
            return True
        column = column.iloc[0]
        self._assert_type(column["name"], "label time stamp", FeatureType.TIMESTAMP.value)
        self._assert_not_null(self._data, column["name"], "label time stamp")

    def _time_stamp_types_valid(self):
        ts_columns = self._version_entities_df[self._version_entities_df["type"] == FeatureType.TIMESTAMP.value][
            "name"
        ].tolist()
        for ts_column in ts_columns:
            self._assert_not_empty(self._data, ts_column, "time stamp")
            try:
                self._data[ts_column] = pd.to_datetime(self._data[ts_column])
            except Exception:
                error_msg = "Column {} is marked as type Timestamp but is malformed".format(ts_column)
                raise EntitiesValidationError(error_msg)

    def _boolean_types_valid(self):
        boolean_columns = self._version_entities_df[self._version_entities_df["type"] == FeatureType.BOOLEAN.value][
            "name"
        ].tolist()
        for boolean_column in boolean_columns:
            self._assert_not_empty(self._data, boolean_column, "boolean")

            unique_values = set(self._data[boolean_column].dropna().unique())
            if len(unique_values) == 0:
                error_msg = "Boolean column {} is empty".format(boolean_column)
                raise EntitiesValidationError(error_msg)

            if not (
                unique_values <= {True, False}
                or unique_values <= {1, 0}
                or unique_values <= {1.0, 0.0}
                or unique_values <= {"true", "false"}
                or unique_values <= {"1", "0"}
                or unique_values <= {"1.0", "0.0"}
            ):
                error_msg = (
                    "Boolean column must be either a subset of {{True, False}} or {{1, 0}}. "
                    "You provided {} for column {}".format(",".join(map(str, unique_values)), boolean_column)
                )
                raise EntitiesValidationError(error_msg)

            if self._data[boolean_column].dtype == np.dtype(object):
                self._data[boolean_column] = self._data[boolean_column].map(
                    {"true": True, "false": False, "1": True, "0": False, "1.0": True, "0.0": False}
                )
            else:
                self._data[boolean_column] = self._data[boolean_column].astype("boolean")

    def _numeric_types_valid(self):
        numeric_columns = self._version_entities_df[self._version_entities_df["type"] == FeatureType.NUMERIC.value][
            "name"
        ].tolist()
        for numeric_column in numeric_columns:
            self._assert_not_empty(self._data, numeric_column, "numeric")
            try:
                self._data[numeric_column] = pd.to_numeric(self._data[numeric_column])
                if numeric_column not in ["label_weight"]:
                    try:
                        self._data[numeric_column] = self._data[numeric_column].astype("Int64")
                    except TypeError:
                        pass
                    except:
                        pass
            except:
                raise EntitiesValidationError("cast column {}  to numeric failed".format(numeric_column))

    def _categorical_types_valid(self):
        categorical_columns = self._version_entities_df[
            self._version_entities_df["type"] == FeatureType.CATEGORICAL.value
        ]["name"].tolist()
        for categorical_column in categorical_columns:
            self._assert_not_empty(self._data, categorical_column, "categorical")
            self._data[categorical_column] = self._data[categorical_column].astype("category")

    def _build_feature_statistics_df(self, data):
        types = []
        for feature_name in data.columns:
            feature_data = data[feature_name].dropna()
            feature_stat = dict()
            feature_stat["name"] = feature_name
            feature_stat["pandas_type"] = (
                data[feature_name].dtype.type
                if isinstance(data[feature_name].dtype, pd.Int64Dtype)
                else data[feature_name].dtype
            )
            hist = feature_data.value_counts(normalize=True)
            feature_stat["num_unique"] = len(hist)
            feature_stat["% unique"] = len(hist) / len(data)
            feature_stat["% top 5"] = hist.head(5).sum()
            feature_stat["skewness"] = (
                feature_data.skew() if pd.api.types.is_numeric_dtype(feature_stat["pandas_type"]) else np.nan
            )
            types.append(feature_stat)
        types = pd.DataFrame(types)
        types["type"] = types["name"].map(self._version_entities_df.set_index("name")["type"])
        return types

    @staticmethod
    def _infer_secondary_type_row(row):
        if row["type"] == FeatureType.CATEGORICAL.value:
            return compute_secondary_categorical(row)
        if row["type"] == FeatureType.BOOLEAN.value:
            return compute_secondary_boolean(row)
        if row["type"] == FeatureType.NUMERIC.value:
            return compute_secondary_numeric(row["skewness"])
        return np.nan

    def infer_secondary_type(self):
        if (
            "secondary_type" not in self._version_entities_df
            or self._version_entities_df["secondary_type"].isnull().values.all()
        ):
            logger.info("Secondary type was NOT provided as part of the version entities. Computing")
            feature_statistics_df = self._build_feature_statistics_df(self._data)
            feature_statistics_df["secondary_type"] = feature_statistics_df.apply(
                self._infer_secondary_type_row, axis=1
            )
            self._version_entities_df["secondary_type"] = self._version_entities_df["name"].map(
                feature_statistics_df.set_index("name")["secondary_type"]
            )
        elif self._version_entities_df["secondary_type"].isnull().values.any():
            raise EntitiesValidationError("seconday_type supplied for some entities, should be supplied for all or non")

    def prepare(self):
        """
        Validate and prepare the data
        """
        logger.info("start validate and prepare data")
        self._data = self._data.reset_index(drop=True)

        # version_entities attributes
        self._version_entities_has_not_reserved_names()
        self._column_names_match_version_entities()

        logger.info("start validate and prepare dimensions")
        # Dimensions
        self._is_valid_dimension_ts_count()
        self._is_valid_dimension()

        logger.info("start validate and prepare types")
        # Types
        self._boolean_types_valid()
        self._categorical_types_valid()
        self._time_stamp_types_valid()
        self._numeric_types_valid()

        logger.info("start validate and prepare roles")
        # Roles
        self._has_all_required_roles()
        self._is_valid_record_id()
        self._is_valid_prediction_ts()
        self._is_valid_prediction_value()
        self._is_valid_prediction_probability()
        self._is_valid_label()
        self._is_valid_label_ts()
        self._is_valid_label_weight()
        self.infer_secondary_type()
        return self._data
