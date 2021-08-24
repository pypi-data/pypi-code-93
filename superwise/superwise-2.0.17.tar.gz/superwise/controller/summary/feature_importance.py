import os
from multiprocessing import cpu_count
from multiprocessing import Pool

import numpy as np
import pandas as pd
import shap
from sklearn import preprocessing
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer

from superwise import logger
from superwise.resources.superwise_enums import CategoricalSecondaryType
from superwise.resources.superwise_enums import FeatureType


class FeatureImportance:
    def __init__(self, entities_df):
        self._entities_df = entities_df
        self.logger = logger

    def _get_feature_mask(self):
        return self._entities_df[self._entities_df["role"] == "feature"]

    def get_numeric_features(self, exclude_metadata=False):
        feature_df = self._get_feature_mask()
        numeric_feature_df = feature_df[feature_df["type"] == FeatureType.NUMERIC.value]
        return numeric_feature_df["name"].tolist()

    def get_categorical_features(self, skip_sparse=True, exclude_metadata=False):
        feature_df = self._get_feature_mask()
        categorical_feature_df = feature_df[feature_df["type"] == FeatureType.CATEGORICAL.value]
        if skip_sparse:
            categorical_feature_df = categorical_feature_df[
                categorical_feature_df["secondary_type"] != CategoricalSecondaryType.SPARSE.value
            ]
        return categorical_feature_df["name"].tolist()

    def get_boolean_features(self, exclude_metadata=False):
        feature_df = self._get_feature_mask()
        boolean_feature_df = feature_df[feature_df["type"] == FeatureType.BOOLEAN.value]
        return boolean_feature_df["name"].tolist()

    def get_sparse_features(self, exclude_metadata=False):
        feature_df = self._get_feature_mask()

        categorical_feature_df = feature_df[feature_df["type"] == FeatureType.CATEGORICAL.value]
        sparse_feature_df = categorical_feature_df[
            categorical_feature_df["secondary_type"] == CategoricalSecondaryType.SPARSE.value
        ]
        return sparse_feature_df["name"].tolist()

    def _parallelize_shap(self, features, explainer, n_cores=cpu_count()):
        logger.debug("Running parallelize shap")
        features_split = np.array_split(features, n_cores)
        pool = Pool(n_cores)
        shap_values = np.concatenate(pool.map(explainer.shap_values, features_split))
        pool.close()
        pool.join()
        return shap_values

    def _create_categorical_embedding(self, srs):
        logger.debug("create categorical embedding for {}".format(srs.name))
        return srs.value_counts(dropna=False).to_dict()

    def _fi_pre_processing(self, baseline_data, version_entities) -> pd.DataFrame:
        logger.debug("pre processing for feature importance")
        features_for_modeling = (
            version_entities.get_boolean_features(exclude_metadata=True)
            + version_entities.get_numeric_features(exclude_metadata=True)
            + version_entities.get_categorical_features(exclude_metadata=True)
        )
        features_df = baseline_data.copy()[features_for_modeling]
        for feature in version_entities.get_categorical_features(exclude_metadata=True):
            logger.debug(f"feature importance pre pre-processing categorical feature {feature}")
            embedding = self._create_categorical_embedding(baseline_data[feature])
            features_df[feature] = pd.to_numeric(features_df[feature].map(embedding)).fillna(0)
        imp_mean = SimpleImputer(missing_values=np.nan, strategy="mean")
        numeric_features = version_entities.get_numeric_features(exclude_metadata=True)
        if len(numeric_features) > 0:
            logger.debug(f"pre-processing {len(numeric_features)} numeric features")
            features_df[numeric_features] = imp_mean.fit_transform(features_df[numeric_features])
        boolean_features = version_entities.get_boolean_features(exclude_metadata=True)
        if len(boolean_features) > 0:
            logger.debug(f"pre-processing {len(boolean_features)} boolean features")
            imp_mode = SimpleImputer(missing_values=np.nan, strategy="most_frequent")
            features_df[boolean_features] = features_df[boolean_features].astype(float)
            features_df[boolean_features] = imp_mode.fit_transform(features_df[boolean_features])
        return features_df

    def get_label_by_role(self, role):
        res = self._entities_df[self._entities_df["role"] == role]
        if len(res):
            return res.iloc[0]["name"]
        return None

    def _calc(self, baseline_data):
        logger.debug("calc feature importance")
        processed_features = self._fi_pre_processing(baseline_data, self)
        reconstruction_model = RandomForestRegressor(max_depth=7, n_estimators=50)
        label_name = None
        if not label_name:
            label_name = self.get_label_by_role("prediction value")
        if not label_name:
            label_name = self.get_label_by_role("label")
        if not label_name:
            raise Exception("no valid label to fit model")

        label = baseline_data[label_name]
        if not pd.api.types.is_numeric_dtype(label):
            le = preprocessing.LabelEncoder()
            le.fit(label)
            label = le.transform(label)
        reconstruction_model.fit(processed_features, label)
        explainer = shap.TreeExplainer(reconstruction_model)
        n_cores = int(os.environ.get("PARALLELIZE_CORES", cpu_count()))
        shap_values = self._parallelize_shap(processed_features, explainer, n_cores=n_cores)
        mean_shap = np.abs(shap_values).mean(axis=0)
        mean_shap = (mean_shap / mean_shap.sum()).round(4) * 100
        importance = dict(zip(processed_features.columns, mean_shap.tolist()))
        return importance

    def compute(self, data):
        if "feature_importance" not in self._entities_df or pd.isnull(self._entities_df["feature_importance"]).all():
            logger.info("Feature importance was NOT provided as part of the version entities. Computing")
            feature_name_to_importance = self._calc(data)
            self._entities_df["feature_importance"] = self._entities_df["name"].map(feature_name_to_importance)
        else:
            logger.info("Feature importance was provided as part of the version entities. Skipping Computation")
        self._entities_df["feature_importance"].fillna(0, inplace=True)
        return self._entities_df
