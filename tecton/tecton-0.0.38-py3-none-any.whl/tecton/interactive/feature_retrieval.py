from datetime import datetime
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Union

import numpy as np
import pandas as pd
import pendulum
import pyspark
from pyspark.sql import DataFrame as pysparkDF
from pyspark.sql import functions

from tecton._internals import data_frame_helper
from tecton._internals import errors as internal_errors
from tecton._internals.feature_packages import aggregations
from tecton._internals.utils import infer_timestamp
from tecton._internals.utils import is_materializable_workspace
from tecton.interactive.data_frame import DataFrame
from tecton.interactive.data_frame import FeatureVector
from tecton.interactive.feature_package import FeaturePackage
from tecton.interactive.feature_service import FeatureService
from tecton.interactive.feature_set_config import FeatureSetConfig
from tecton.interactive.feature_view import FeatureView
from tecton.tecton_context import TectonContext
from tecton.tecton_errors import TectonValidationError
from tecton_spark.feature_package_view import FeaturePackageOrView
from tecton_spark.feature_package_view import FPBackedFeaturePackageOrView
from tecton_spark.feature_package_view import FVBackedFeaturePackageOrView
from tecton_spark.materialization_params import MaterializationParams


def get_online_features(
    features: Union[FeatureService, Sequence[FeaturePackage]],
    join_keys: Optional[Mapping[str, Union[int, np.int_, str, bytes]]] = None,
    include_join_keys_in_response: bool = False,
    request_data: Optional[Mapping[str, Union[int, np.int_, str, bytes, float]]] = None,
) -> FeatureVector:
    if isinstance(features, FeatureService):
        return features.get_feature_vector(
            join_keys=join_keys,
            include_join_keys_in_response=include_join_keys_in_response,
            request_context_map=request_data,
        )
    elif isinstance(features, list):
        features_vector = FeatureVector([], [], [])
        for fp in features:
            features_vector._update(
                fp.get_feature_vector(
                    join_keys=join_keys,
                    include_join_keys_in_response=include_join_keys_in_response,
                    request_context_map=request_data,
                )
            )
        return features_vector
    else:
        raise TectonValidationError(f"Unexpected data type for features: {type(features)}")


def get_historical_features(
    features: Union[Sequence[FeaturePackage], Sequence[FeatureView], FeatureService],
    spine: Union[pysparkDF, pd.DataFrame],
    from_source: bool = False,
    save: bool = None,
    save_as: str = None,
    timestamp_key: Optional[str] = None,
) -> DataFrame:

    if not timestamp_key:
        timestamp_key = infer_timestamp(spine)

    if isinstance(features, FeatureService):
        return features.get_feature_dataframe(
            spine=spine, timestamp_key=timestamp_key, use_materialized_data=not from_source, save=save, save_as=save_as
        )
    elif isinstance(features, list):
        for feature in features:
            if not (isinstance(feature, FeaturePackage) or isinstance(feature, FeatureView)):
                raise TectonValidationError(
                    "The `features` parameter can only be " "a FeatureService, or a List of FeatureViews"
                )

        feature_set_config = FeatureSetConfig()
        for feature in features:
            if isinstance(feature, FeaturePackage):
                fpov = FPBackedFeaturePackageOrView(feature._proto)
            else:
                fpov = FVBackedFeaturePackageOrView(feature._proto)
            feature_set_config._add(fpov)
        return feature_set_config.get_feature_dataframe(spine, timestamp_key, use_materialized_data=not from_source)
    else:
        raise TectonValidationError(
            "The `features` parameter can only be " "a FeatureService, or a List of FeatureViews"
        )


def get_features(
    feature_package_or_view: FeaturePackageOrView,
    entities: Union[pyspark.sql.dataframe.DataFrame, pd.DataFrame, None] = None,
    start_time: Optional[pendulum.DateTime] = None,
    end_time: Optional[pendulum.DateTime] = None,
    from_source: bool = False,
) -> DataFrame:
    if feature_package_or_view.is_online:
        raise internal_errors.FP_NOT_SUPPORTED_GET_FEATURE_DF

    if from_source and feature_package_or_view.is_push:
        raise TectonValidationError("FeatureTables are not compatible with from_source=True")

    if not from_source and not is_materializable_workspace(feature_package_or_view.workspace):
        raise internal_errors.FD_GET_MATERIALIZED_FEATURES_FROM_NONMATERIALIZABLE_WORKSPACE(
            feature_package_or_view.name, feature_package_or_view.workspace
        )

    if not from_source and not feature_package_or_view.writes_to_offline_store:
        raise internal_errors.FD_GET_FEATURES_FROM_DISABLED_MATERIALIZATION(
            feature_package_or_view.name, feature_package_or_view.workspace
        )

    if start_time is not None and isinstance(start_time, datetime):
        start_time = pendulum.instance(start_time)
    if end_time is not None and isinstance(end_time, datetime):
        end_time = pendulum.instance(end_time)

    if feature_package_or_view.is_temporal_aggregate or feature_package_or_view.is_temporal:
        params = MaterializationParams.from_package_or_view(feature_package_or_view)
        assert params is not None, "Materialization params cannot be None"
        _start = start_time or params.from_timestamp
        _end = end_time or params.most_recent_anchor(pendulum.now("UTC"))
        time_range = pendulum.Period(_start, _end)
    else:
        _start = start_time or pendulum.datetime(1970, 1, 1)
        _end = end_time or pendulum.now("UTC")
        time_range = pendulum.Period(_start, _end)

    tc = TectonContext.get_instance()
    spark = tc._spark

    # Validate that entities only contains Join Key Columns.
    if entities is not None:
        assert set(entities.columns).issubset(
            set(feature_package_or_view.join_keys)
        ), f"Entities should only contain columns that can be used as Join Keys: {feature_package_or_view.join_keys}"

        if isinstance(entities, pd.DataFrame):
            entities = spark.createDataFrame(entities)

    if from_source:
        raw_data_limits = aggregations._get_raw_data_time_limits(feature_package_or_view, _start, _end)
        tc._register_temp_views_for_feature_package_or_view(
            feature_package_or_view=feature_package_or_view,
            register_stream=False,
            raw_data_time_limits=raw_data_limits,
        )

    try:
        if feature_package_or_view.is_temporal or feature_package_or_view.is_push:
            df = aggregations.get_all_temporal_push_features(
                spark, feature_package_or_view, entities, not from_source, time_range
            )
        else:
            df = data_frame_helper._get_feature_dataframe_with_limits(
                feature_package_or_view,
                spine=None,
                spine_time_limits=time_range,
                use_materialized_data=not from_source,
                spine_time_key=None,
                validate_time_key=False,
            ).to_spark()
            if entities is not None:
                df = df.join(functions.broadcast(entities.distinct()), entities.columns, how="right")
            columns = (
                feature_package_or_view.join_keys
                + feature_package_or_view.features
                + [feature_package_or_view.timestamp_key]
            )
            df = df.select(*columns)
    except pyspark.sql.utils.AnalysisException as e:
        if "Unable to infer schema for Parquet" in e.desc or "doesn't exist" in e.desc:
            if feature_package_or_view.is_push:
                return DataFrame._create(tc._spark.createDataFrame([], feature_package_or_view.view_schema.to_spark()))
            else:
                raise internal_errors.FP_NO_MATERIALIZED_DATA(feature_package_or_view.name)
        raise
    # for FVs, raw data filtering should produce data already in the time range for adhoc
    # if FV output is outside feature time range given raw data, we do not want to filter it so the time validation
    # in materialization_plan._possibly_apply_feature_time_limits can fail the query. If we filter here, the UDF
    # may be executed after the filter step, when we want it to catch all features generated outside the time range
    # in ad hoc. It's not 100% but for this it may be good enough
    should_filter_by_time = not from_source or not feature_package_or_view.is_feature_view
    if should_filter_by_time:
        if _start:
            df = df.filter(df[feature_package_or_view.timestamp_key] > _start)
        if _end:
            df = df.filter(df[feature_package_or_view.timestamp_key] < _end)

    return DataFrame._create(df)
