from typing import List, Union, Dict

from .datasets import TimeSeriesDataset, GordoBaseDataProvider, TagList
from .sensor_tag import SensorTag, SensorTagNormalizationError

from .data_provider.nes_provider import NesDataProvider


def nes_normalize_sensor(
    sensor: Union[Dict, str, SensorTag], asset: str = None
) -> SensorTag:
    """
    Normalize sensor tag in regards to NES specific.

    Parameters
    ----------
    sensor: Union[Dict, str, SensorTag]
    asset: str - Is required field for NES

    Returns
    -------
    SensorTag

    """
    if isinstance(sensor, dict):
        if "name" not in sensor:
            raise SensorTagNormalizationError("Tag name is empty")
        if "asset" not in sensor:
            raise SensorTagNormalizationError("asset is empty for '%s'", sensor["name"])
        return SensorTag(sensor["name"], sensor["asset"])
    elif isinstance(sensor, str):
        if not asset:
            raise SensorTagNormalizationError("asset is empty")
        return SensorTag(sensor, asset)
    elif isinstance(sensor, SensorTag):
        return sensor
    raise SensorTagNormalizationError(
        "Sensor %s with type %s cannot be converted to a valid SensorTag"
        % (sensor, type(sensor))
    )


class NesTimeSeriesDataset(TimeSeriesDataset):
    @staticmethod
    def create_default_data_provider() -> GordoBaseDataProvider:
        return NesDataProvider()

    @staticmethod
    def tag_normalizer(
        sensors: TagList,
        asset: str = None,
        default_asset: str = None,
    ) -> List[SensorTag]:
        return [nes_normalize_sensor(sensor, asset) for sensor in sensors]
