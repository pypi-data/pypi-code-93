from typing import Callable, Dict, Hashable, Iterable, List, Tuple
from copy import deepcopy

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

from fathom_lib.utils import get_function_params
from fathom_lib.transformers.row_sampler import RowModifier


class Sparkify(BaseEstimator, TransformerMixin):
    """
    Class created to modify the Sklearn API into a similar
    one used in Spark for pipelines:
        https://spark.apache.org/docs/latest/ml-pipeline.html
    """

    def __init__(
        self,
        model,
        X_columns: List[str] = None,
        y_columns: List[str] = None,
        additional_columns: List[str] = None,
        data_mapping: Dict = None,
    ):
        self.pandasify_model = model
        self.X_columns = X_columns
        self.y_columns = y_columns
        self.additional_columns = additional_columns
        self.data_mapping = data_mapping

    def __getattr__(self, item):
        return getattr(self.get_final_model(), item)

    def get_model_params(self, deep=True):
        return self.pandasify_model.get_model_params(deep)

    def _create_column_params(self, function, pipeline_data, kwargs):
        column_params = {}
        for param in get_function_params(function):
            if (
                param not in kwargs
                and param != "X"
                and param != "y"
                and (
                    (param in pipeline_data.additional_columns)
                    or ((self.data_mapping != None) and (param in self.data_mapping))
                )
            ):
                column_params[param] = self._get_param_from_pipeline_data(
                    param, pipeline_data
                )

        return column_params

    def _get_param_from_pipeline_data(self, param, pipeline_data):
        if (self.data_mapping != None) and (param in self.data_mapping):
            param_column = pipeline_data.get_additional_column(self.data_mapping[param])
        else:
            param_column = pipeline_data.get_additional_column(param)
        return param_column

    def _get_X_from_pipeline_data(self, pipeline_data):
        if isinstance(self.get_final_model(), RowModifier):
            if self.X_columns == None:
                X_columns = pipeline_data.X_columns
            else:
                X_columns = self.X_columns
            X = pipeline_data.data[
                X_columns + pipeline_data.additional_columns + pipeline_data.y_columns
            ]
        elif self.X_columns == None:
            X = pipeline_data.get_X_data()
        else:
            X = pipeline_data.get_new_X_data(self.X_columns)
        return X

    def _prepare_data(self, pipeline_data, method, params):
        pipeline_data = deepcopy(pipeline_data)
        X = self._get_X_from_pipeline_data(pipeline_data)
        column_params = self._create_column_params(method, pipeline_data, params)
        return pipeline_data, X, column_params

    def _prepare_final_pipeline_data(self, pipeline_data, transformed):
        pipeline_data.data.drop(pipeline_data.X_columns, axis=1, inplace=True)
        pipeline_data.data.reset_index(drop=True, inplace=True)
        transformed.reset_index(drop=True, inplace=True)

        if isinstance(self.get_final_model(), RowModifier):
            # If there are new column names for y_columns or additional_columns
            # then the previous names are restored
            new_columns = {}
            X_columns = []
            for col_name in list(transformed.columns):
                for y_col in pipeline_data.y_columns:
                    if ("(" + y_col + ")") in col_name or y_col == col_name:
                        new_columns[col_name] = y_col
                for add_col in pipeline_data.additional_columns:
                    if ("(" + add_col + ")") in col_name or add_col == col_name:
                        new_columns[col_name] = add_col
                for X_col in pipeline_data.X_columns:
                    if ("(" + X_col + ")") in col_name or X_col == col_name:
                        X_columns.append(col_name)

            # TODO: Maybe also add type reconstruction for all columns
            transformed.rename(columns=new_columns, inplace=True)
            pipeline_data.data = transformed
            pipeline_data.X_columns = X_columns
        else:
            pipeline_data.data = pd.concat([pipeline_data.data, transformed], axis=1)
            pipeline_data.X_columns = list(transformed.columns)

    def fit(self, pipeline_data, **fit_params):
        X = self._get_X_from_pipeline_data(pipeline_data)
        column_params = self._create_column_params(
            self.get_final_model().fit, pipeline_data, fit_params
        )

        if pipeline_data.y_columns == []:  # unsupervised
            return self.pandasify_model.fit(X=X, **column_params, **fit_params)
        else:  # supervised
            y = pipeline_data.get_y_data()
            return self.pandasify_model.fit(X=X, y=y, **column_params, **fit_params)

    def predict(self, pipeline_data, **predict_params) -> pd.DataFrame:
        return self._predict(pipeline_data, method="predict", **predict_params)

    def predict_proba(self, pipeline_data, **predict_proba_params) -> pd.DataFrame:
        return self._predict(
            pipeline_data, method="predict_proba", **predict_proba_params
        )

    def predict_log_proba(
        self, pipeline_data, **predict_log_proba_params
    ) -> pd.DataFrame:
        return self._predict(
            pipeline_data, method="predict_log_proba", **predict_log_proba_params
        )

    def _predict(self, pipeline_data, method, **predict_params) -> pd.DataFrame:
        pipeline_data, X, column_params = self._prepare_data(
            pipeline_data, self.get_final_model().predict, predict_params
        )
        compute_func = getattr(self.pandasify_model, method)
        predictions = compute_func(X, **column_params, **predict_params)
        pipeline_data.data = pd.concat(
            [
                pipeline_data.data.reset_index(drop=True),
                predictions.reset_index(drop=True),
            ],
            axis=1,
        )
        return pipeline_data

    def transform(self, pipeline_data, **transform_params) -> pd.DataFrame:
        pipeline_data, X, column_params = self._prepare_data(
            pipeline_data, self.get_final_model().transform, transform_params
        )
        if "y" in get_function_params(self.get_final_model().transform):
            column_params["y"] = pipeline_data.get_y_data()

        transformed = self.pandasify_model.transform(
            X, **column_params, **transform_params
        )
        self._prepare_final_pipeline_data(pipeline_data, transformed)
        return pipeline_data

    def fit_transform(self, pipeline_data, **fit_transform_params) -> pd.DataFrame:
        pipeline_data, X, column_params = self._prepare_data(
            pipeline_data, self.get_final_model().fit, fit_transform_params
        )
        if pipeline_data.y_columns == []:  # unsupervised
            transformed = self.pandasify_model.fit_transform(
                X=X, **column_params, **fit_transform_params
            )
        else:  # supervised
            y = pipeline_data.get_y_data()
            transformed = self.pandasify_model.fit_transform(
                X=X, y=y, **column_params, **fit_transform_params
            )
        self._prepare_final_pipeline_data(pipeline_data, transformed)
        return pipeline_data

    def get_final_model(self):
        return self.pandasify_model.model

    def _get_model_name(self):
        return self.pandasify_model._get_model_name()
