# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Union

import numpy as np
import pandas as pd
from scipy import sparse

from azureml.automl.runtime._data_definition.exceptions import DataShapeException, InvalidDimensionException

from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes


class MaterializedTabularData:
    """
    An in-memory representation of the Dataset required for machine learning experiments.
    Guarantees that:
        - X, y have non-null values
        - X, y, weights have the right data types
        - y and weights are single dimensional
        - X, y and weights all have the same number of samples
    """
    # A reference code for errors originating from this class.
    _REFERENCE_CODE = ReferenceCodes._MATERIALIZED_TABULAR_DATA_GENERIC

    def __init__(self, X: Union[pd.DataFrame, sparse.spmatrix], y: np.ndarray, weights: Optional[np.ndarray] = None):
        """
        Initialize the materialized data.

        :param X: The features (or columns) to train the model on.
        :param y: The target column (e.g., labels) to predict.
        :param weights: An optional column representing the weight to be assigned to each sample in X.
        """
        self.X = X
        self.y = y
        self.weights = weights

        self._validate()

    def _validate(self) -> None:
        """Does some sanity checks on X, y and weights."""
        self._check_x()
        self._check_y()
        self._check_weights()

    def _check_x(self) -> None:
        """
        Checks that:
            - X is non-null
            - X is 2-dimensional
            - X is of expected types (converts to a pandas DataFrame if the input was a numpy array)
        :return: None
        :raises: InvalidValueException, InvalidTypeException
        """
        Contract.assert_value(self.X, "X", reference_code=MaterializedTabularData._REFERENCE_CODE)
        self._try_coerce_x_to_pandas()
        Contract.assert_type(self.X, "X", expected_types=(pd.DataFrame, sparse.spmatrix),
                             reference_code=MaterializedTabularData._REFERENCE_CODE)

        if self.X.ndim > 2:
            raise InvalidDimensionException(
                "Expected 'X' to be a two dimensional array, but has {} dimensions.".format(self.X.ndim),
                target="X",
            )

    def _try_coerce_x_to_pandas(self) -> None:
        # There are still cases (tests only) today where-in we may be passing a numpy array to this class
        # Try to coerce a numpy array to a pandas DataFrame in those cases
        try:
            if isinstance(self.X, np.ndarray):
                self.X = pd.DataFrame(self.X).infer_objects()
        except Exception:
            # If we couldn't convert, ignore the error. We'll later fail with a better exception for an invalid type
            pass

    def _check_y(self) -> None:
        """
        Checks that 'y' is:
            - non-null
            - of the right type
            - has the same number of samples as 'X'
            - is a one-dimensional array
        :return: None
        :raises: InvalidValueException, InvalidTypeException, DataShapeException, InvalidDimensionException
        """
        Contract.assert_value(self.y, "y", reference_code=MaterializedTabularData._REFERENCE_CODE)

        # If input was provided as a pandas DataFrame (with single column) or Series, try to coerce into a numpy array
        if isinstance(self.y, (pd.DataFrame, pd.Series)):
            self.y = self._try_convert_series_to_numpy_array(self.y)

        Contract.assert_type(self.y, "y", expected_types=np.ndarray,
                             reference_code=MaterializedTabularData._REFERENCE_CODE)

        # this will handle following cases by ravelling (= reshaping)
        # [[2],[3],[4]] - this will pass the condition and ravel and convert it to [2,3,4]
        # [[2,9],[3],[4]] - this will not pass condition and hence wont ravel
        if self.y.ndim == 2 and self.y.shape[1] == 1:
            self.y = self.y.ravel()

        if self.y.ndim > 1:
            raise InvalidDimensionException(
                "Expected 'y' to be single dimensional numpy array, but has {} dimensions.".format(self.y.ndim),
                target="y",
            )

        if self.X.shape[0] != len(self.y):
            raise DataShapeException(
                "X({}) and y({}) have different number of samples.".format(self.X.shape[0], len(self.y)), target="X, y"
            )

    def _check_weights(self) -> None:
        """
        Checks that 'weights' is:
            - of the right type
            - has the same number of samples as 'X'
            - is a one-dimensional array
        :return: None
        :raises: InvalidValueException, InvalidTypeException, DataShapeException, InvalidDimensionException
        """
        if self.weights is None:
            return

        # If input was provided as a pandas DataFrame (with single column) or Series, try to coerce into a numpy array
        if isinstance(self.weights, (pd.DataFrame, pd.Series)):
            self.weights = self._try_convert_series_to_numpy_array(self.weights)

        Contract.assert_type(self.weights, "weights", expected_types=np.ndarray,
                             reference_code=MaterializedTabularData._REFERENCE_CODE)

        if self.weights.ndim > 1:
            raise InvalidDimensionException(
                "Expected weights to be single dimensional numpy array, but has {} dimensions.".format(
                    self.weights.ndim
                ),
                target="weights",
            )

        if self.X.shape[0] != len(self.weights):
            raise DataShapeException(
                "X{} and weights{} have different number of samples.".format(self.X.shape[0], len(self.weights)),
                target="X, weights",
            )

    def _try_convert_series_to_numpy_array(
            self, single_dimensional_data: Union[pd.DataFrame, pd.Series]
    ) -> Union[pd.DataFrame, pd.Series, np.ndarray]:
        """Try to convert a pandas DataFrame/Series to a numpy array."""
        result = single_dimensional_data

        if isinstance(single_dimensional_data, pd.Series):
            result = single_dimensional_data.to_numpy()
        elif isinstance(single_dimensional_data, pd.DataFrame):
            if single_dimensional_data.shape[1] == 1:
                # Extract the only a column from the DataFrame
                result = single_dimensional_data[0].to_numpy()
            elif single_dimensional_data.empty:
                # An empty column
                return single_dimensional_data.to_numpy()

        # default case to return the same data as input, as single_dimensional_data may not really be 1-d, or a pandas
        # input format
        return result
