import logging
import pandas as pd
import pyarrow.parquet as pq
import fnmatch

from typing import List, Dict, cast
from abc import abstractmethod, ABCMeta
from gordo_dataset.sensor_tag import SensorTag
from gordo_dataset.data_provider.storages import FileSystem
from gordo_dataset.file_system.base import FileInfo
from dataclasses import dataclass
from collections import defaultdict

from .utils import build_dir_path

logger = logging.getLogger(__name__)


class MeasurementNotFoundError(Exception):
    def __init__(self, msg: str, sensor_tags: List[SensorTag]):
        self.sensor_tags = sensor_tags
        super().__init__(msg)


@dataclass(frozen=True)
class Measurement:
    id: int
    tag: SensorTag


class MeasurementMapper(metaclass=ABCMeta):
    """
    Find measurement-ids from the sensor tag name
    """

    @abstractmethod
    def get_measurements(self, sensor_tags: List[SensorTag]) -> List[Measurement]:
        ...


class DirectMeasurementMapper(MeasurementMapper):
    def get_measurements(self, sensor_tags: List[SensorTag]) -> List[Measurement]:
        measurements = []
        for sensor_tag in sensor_tags:
            measurements.append(Measurement(sensor_tag.name, sensor_tag))
        return measurements


class DataLakeMeasurementMapper(MeasurementMapper):
    def __init__(self, storage: FileSystem, base_dir: str):
        self.storage = storage
        self.base_dir = base_dir

    def read_parquet(self, path: str) -> pd.Series:
        with self.storage.open(path, "rb") as f:
            table = pq.read_table(f, columns=["measurementId", "measurementName"])
            df = table.to_pandas()
            df = df.set_index("measurementName")
        return df["measurementId"]

    def find_measurements_in_dir(
        self, dir_path: str, sensor_tags: List[SensorTag]
    ) -> List[Measurement]:
        storage = self.storage
        name_ids: Dict[str, int] = {}
        for file_path, file_info in storage.ls(dir_path):
            file_info = cast(FileInfo, file_info)
            if file_info.isfile() and fnmatch.fnmatch(file_path, "*.parquet"):
                s = self.read_parquet(file_path)
                found_name_ids = {}
                for sensor_tag in sensor_tags:
                    name = sensor_tag.name
                    try:
                        found_name_ids[name] = s.loc[name]
                    except KeyError:
                        pass
                logger.debug(
                    "Read parquet '%s'. Find %d measurements from %d",
                    file_path,
                    len(found_name_ids),
                    len(sensor_tags),
                )
                for name in found_name_ids.keys():
                    if name in name_ids:
                        raise ValueError(
                            "measurementName='%s' duplicate in the file '%s'"
                            % (name, file_path)
                        )
                name_ids.update(found_name_ids)
        measurements = []
        for sensor_tag in sensor_tags:
            name = sensor_tag.name
            if name not in name_ids:
                raise MeasurementNotFoundError(
                    "Unable to find measurement for the tag %s" % (sensor_tag,),
                    [sensor_tag],
                )
            measurements.append(Measurement(name_ids[name], sensor_tag))
        return measurements

    def get_measurements(self, sensor_tags: List[SensorTag]) -> List[Measurement]:
        storage, base_dir = self.storage, self.base_dir
        by_assets = defaultdict(list)
        for sensor_tag in sensor_tags:
            if sensor_tag.asset is None:
                raise ValueError("asset is empty for %s" % (str(sensor_tag),))
            by_assets[sensor_tag.asset].append(sensor_tag)
        measurements: List[Measurement] = []
        for asset, asset_sensor_tags in by_assets.items():
            dir_path = build_dir_path(storage, base_dir, [("asset", asset)])
            if not storage.isdir(dir_path):
                msg = "Unable to find asset '%s' directory '%s'" % (asset, dir_path)
                raise MeasurementNotFoundError(msg, asset_sensor_tags)
            asset_measurements = self.find_measurements_in_dir(
                dir_path, asset_sensor_tags
            )
            measurements.extend(asset_measurements)
        return measurements
