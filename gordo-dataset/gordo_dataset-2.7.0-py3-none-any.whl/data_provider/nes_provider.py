import logging
import timeit
import os

from datetime import datetime
from copy import copy

import pandas as pd
import pyarrow.parquet as pq
from concurrent.futures import ThreadPoolExecutor

from gordo_dataset.file_system import FileSystem
from gordo_dataset.utils import capture_args
from gordo_dataset.sensor_tag import SensorTag

from gordo_dataset.data_provider.base import GordoBaseDataProvider
from gordo_dataset.data_provider.storages import create_storage, DEFAULT_STORAGE_TYPE
from gordo_dataset.data_provider.partition import split_by_partitions, PartitionBy
from gordo_dataset.exceptions import ConfigException
from typing import Union, Dict, Optional, Any, List, Iterable, Tuple, TypeVar, cast


from .measurement_mapper import MeasurementMapper, DataLakeMeasurementMapper
from .nes_lookup import NesLookup, FileLocation

logger = logging.getLogger(__name__)

FileLoadingResult = Tuple[FileLocation, pd.Series]

DEFAULT_GOOD_STATUSES = [192]


T = TypeVar("T")


def infinity_iter(v: T) -> Iterable[T]:
    while True:
        yield v


def get_default_base_dir() -> Optional[str]:
    adl_base_dir = os.environ.get("ADL_BASE_DIR")
    if not adl_base_dir:
        adl_base_dir = "raw/data/bazefield wind/omnia_prevent/"
    return adl_base_dir


class NesDataProvider(GordoBaseDataProvider):
    @staticmethod
    def instantiate_storage(
        storage: Optional[Union[FileSystem, Dict[str, Any]]]
    ) -> FileSystem:
        if isinstance(storage, FileSystem):
            return storage
        else:
            kwargs: Dict[str, Any] = copy(storage) if storage else {}
            storage_type = kwargs.pop("type", DEFAULT_STORAGE_TYPE)
            return create_storage(storage_type, **kwargs)

    @staticmethod
    def create_measurement_mapper(
        storage: FileSystem, base_dir: str
    ) -> MeasurementMapper:
        metatable_dir = storage.join(base_dir, "metatable")
        return DataLakeMeasurementMapper(storage, metatable_dir)

    @staticmethod
    def create_nes_mapper(storage: FileSystem, base_dir: str) -> NesLookup:
        data_dir = storage.join(base_dir, "data")
        return NesLookup(storage, data_dir)

    @capture_args
    def __init__(
        self,
        storage: Optional[Union[FileSystem, Dict[str, Any]]] = None,
        measurement_mapper: Optional[MeasurementMapper] = None,
        base_dir: Optional[str] = None,
        good_statuses: Optional[List[int]] = None,
        threads: int = 10,
    ):
        """
        Parameters
        ----------
        storage: Optional[Union[FileSystem, Dict[str, Any]]] - Storage with NES data
        measurement_mapper: Optional[MeasurementMapper] - The measurement mapper. By default it's ``DataLakeMeasurementMapper``
        base_dir: Optional[str] - Directory where are the data and the metatable
        good_statuses: Optional[List[int]] - Filter out all values which is not in this list
        threads: int - Number of threads in the fetcher thread pool

        """
        if not base_dir:
            base_dir = get_default_base_dir()
        self.storage = self.instantiate_storage(storage)
        if not measurement_mapper:
            measurement_mapper = self.create_measurement_mapper(
                self.storage, cast(str, base_dir)
            )
        self.measurement_mapper = measurement_mapper
        self.lookup = self.create_nes_mapper(self.storage, cast(str, base_dir))
        if not good_statuses:
            good_statuses = DEFAULT_GOOD_STATUSES
        self.good_statuses = good_statuses
        self.threads = threads

    def read_parquet(self, path: str, tag_name: str) -> pd.Series:
        with self.storage.open(path, "rb") as f:
            table = pq.read_table(f, columns=["time", "q", "v"])
            df = table.to_pandas()
            if self.good_statuses:
                df = df[df["q"].isin(self.good_statuses)]
            df["time"] = pd.to_datetime(df["time"], utc=True)
            df["v"] = pd.to_numeric(df["v"])
            df = df.set_index("time")
            df = df.rename(columns={"v": tag_name})
        return df[tag_name]

    def load_location(
        self, file_location: FileLocation, dry_run: bool = False
    ) -> pd.Series:
        measurement = file_location.measurement
        tag = measurement.tag
        path = file_location.path
        logger.info(
            "Downloading measurement: %s for partitions: %s from '%s'",
            measurement,
            file_location.partition,
            path,
        )

        info = self.storage.info(path)
        file_size = info.size / (1024 ** 2)
        logger.debug("File size for file '%s': %.2fMB", path, file_size)

        if dry_run:
            # Dry run only, returning empty frame early
            return pd.Series(name=tag.name)

        before_downloading = timeit.default_timer()
        s = self.read_parquet(path, tag.name)
        time_elapsed = timeit.default_timer() - before_downloading
        logger.debug("Done in %.2f sec %s", time_elapsed, path)
        return s

    def _thread_pool_mapper(
        self, file_location: FileLocation, dry_run: bool
    ) -> FileLoadingResult:
        return file_location, self.load_location(file_location, dry_run)

    def load_files(
        self, file_locations: Iterable[FileLocation], dry_run: bool
    ) -> Iterable[FileLoadingResult]:
        if self.threads > 1:
            dry_run_iter = infinity_iter(dry_run)
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                for result in executor.map(
                    self._thread_pool_mapper, file_locations, dry_run_iter
                ):
                    yield result
        else:
            for file_location in file_locations:
                yield file_location, self.load_location(file_location, dry_run)

    def load_series(
        self,
        train_start_date: datetime,
        train_end_date: datetime,
        tag_list: List[SensorTag],
        dry_run: Optional[bool] = False,
        **kwargs,
    ) -> Iterable[pd.Series]:
        if train_end_date < train_start_date:
            raise ConfigException(
                f"NCS reader called with train_end_date: {train_end_date} before train_start_date: {train_start_date}"
            )
        measurements = self.measurement_mapper.get_measurements(tag_list)
        partitions = split_by_partitions(
            PartitionBy.MONTH, train_start_date, train_end_date
        )
        file_locations = self.lookup.files_lookup(measurements, partitions)
        series: Dict[str, pd.Series] = dict()
        for file_location, s in self.load_files(file_locations, bool(dry_run)):
            name = s.name
            if name not in series:
                series[name] = s
            else:
                try:
                    series[name] = pd.concat([series[name], s])
                except Exception as e:
                    logger.warning(
                        "Not able to concatenate series from the file '%s': %s",
                        file_location.path,
                        e,
                    )
        for s in series.values():
            filtered = s[(s.index >= train_start_date) & (s.index < train_end_date)]
            filtered.sort_index(inplace=True)
            yield filtered
