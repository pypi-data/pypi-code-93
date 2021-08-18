from typing import Optional

import attr
import pendulum

from tecton_proto.data.feature_package_pb2 import FeaturePackage
from tecton_spark import feature_package_utils
from tecton_spark import time_utils


@attr.s(auto_attribs=True)
class MaterializationContext(object):
    """MaterializationContext class.

    This class contains information about the time ranges used by a Transformation to compute feature values.

    :param feature_data_start_time: (Optional[pendulum.DateTime): The start of the materialization schedule interval.
    :param feature_data_end_time: (Optional[pendulum.DateTime): The end of the materialization schedule interval.
    :param raw_data_start_time: (Optional[pendulum.DateTime): The start of the data
        interval. This data interval is the same as the schedule interval,
        unless `data_lookback` is set in the MaterializationConfig, then
        the interval length is `data_lookback`.
    :param raw_data_end_time: (Optional[pendulum.DateTime): The end of the data interval (same as `feature_data_end_time`).
    """

    feature_data_start_time: Optional[pendulum.DateTime] = None
    feature_data_end_time: Optional[pendulum.DateTime] = None
    raw_data_start_time: Optional[pendulum.DateTime] = None
    raw_data_end_time: Optional[pendulum.DateTime] = None

    @classmethod
    def build(cls, raw_data_time_limits: pendulum.Period, feature_package: FeaturePackage):
        batch_schedule = time_utils.proto_to_duration(
            feature_package_utils.get_batch_materialization_schedule(feature_package)
        )
        return MaterializationContext(
            feature_data_start_time=raw_data_time_limits.end - batch_schedule,
            feature_data_end_time=raw_data_time_limits.end,
            raw_data_start_time=raw_data_time_limits.start,
            raw_data_end_time=raw_data_time_limits.end,
        )

    @classmethod
    def default(cls):
        dummy_time = pendulum.now("UTC")
        return MaterializationContext(dummy_time, dummy_time, dummy_time, dummy_time)
