import logging

import fnmatch

from gordo_dataset.file_system import FileSystem

from dataclasses import dataclass
from gordo_dataset.data_provider.partition import Partition, MonthPartition
from gordo_dataset.file_system.base import FileInfo
from typing import List, Iterable, Tuple, cast

from .measurement_mapper import Measurement
from .utils import build_dir_path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FileLocation:
    measurement: Measurement
    partition: Partition
    path: str


class NesLookup:
    def __init__(self, storage: FileSystem, base_dir: str):
        """
        Parameters
        ----------
        storage: FileSystem - The file system to find partitions files
        base_dir: str
        """
        self.storage = storage
        self.base_dir = base_dir

    def files_lookup(
        self, measurements: Iterable[Measurement], partitions: Iterable[Partition]
    ) -> Iterable[FileLocation]:
        """
        Finding partitions files in the directory
        """
        storage = self.storage
        collected_partitions: List[MonthPartition] = []
        for partition in partitions:
            if not isinstance(partition, MonthPartition):
                raise ValueError("NesLooks does not support partition %s" % partition)
            collected_partitions.append(partition)
        for measurement in measurements:
            tag = measurement.tag
            for partition in collected_partitions:
                field_values: List[Tuple[str, str]] = [
                    ("asset", tag.asset),
                    ("measurementId", str(measurement.id)),
                    ("year", str(partition.year)),
                    ("month", str(partition.month)),
                ]
                dir_path = build_dir_path(self.storage, self.base_dir, field_values)
                logger.debug(
                    "Processing measurement %s, partition %s, in path '%s'",
                    measurement,
                    partition,
                    dir_path,
                )
                if not storage.isdir(dir_path):
                    logger.warning("Unable to find directory '%s'", dir_path)
                    continue
                found_one = False
                for file_name, file_info in storage.ls(dir_path):
                    file_info = cast(FileInfo, file_info)
                    if file_info.isfile() and fnmatch.fnmatch(file_name, "*.parquet"):
                        found_one = True
                        file_location = FileLocation(measurement, partition, file_name)
                        yield file_location
                if not found_one:
                    logger.warning("Directory '%s is empty", dir_path)
