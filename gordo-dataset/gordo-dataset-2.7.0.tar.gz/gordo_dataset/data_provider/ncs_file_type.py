import logging

from abc import ABCMeta, abstractmethod

from gordo_dataset.file_system import FileSystem, FileInfo
from .file_type import FileType, ParquetFileType, CsvFileType, TimeSeriesColumns
from .partition import Partition, YearPartition, MonthPartition

from typing import Iterable, Optional, List, Tuple, Type, Dict, cast

from ..exceptions import ConfigException


logger = logging.getLogger(__name__)

time_series_columns = TimeSeriesColumns("Time", "Value", "Status")


class NcsFileType(metaclass=ABCMeta):
    """
    Represents logic about finding files of one particular type for ``NcsLookup``
    """

    @property
    @abstractmethod
    def file_type(self) -> FileType:
        ...

    @property
    @abstractmethod
    def partition_type(self) -> Type[Partition]:
        ...

    def check_partition(self, partition: Partition):
        return isinstance(partition, self.partition_type)

    @abstractmethod
    def paths(
        self,
        fs: FileSystem,
        tag_dir: str,
        tag_name: str,
        partitions: Iterable[Partition],
    ) -> Iterable[Tuple[Partition, str]]:
        """
        Possible file paths for this file type. These paths should be relational to the tag directory

        Parameters
        ----------
        fs: FileSystem
        tag_dir: str
        tag_name: str
        partitions: Iterable[Partition]

        Returns
        -------
        Iterable[Tuple[Partition, str]]

        """
        ...


class NcsMonthlyParquetFileType(NcsFileType):
    """
    NCS monthly parquet files finder
    """

    def __init__(self):
        self._file_type = ParquetFileType(time_series_columns)
        self._partition_type = YearPartition

    @property
    def file_type(self) -> FileType:
        return self._file_type

    @property
    def partition_type(self) -> Type[Partition]:
        return MonthPartition

    def paths(
        self,
        fs: FileSystem,
        tag_dir: str,
        tag_name: str,
        partitions: Iterable[Partition],
    ) -> Iterable[Tuple[Partition, str]]:
        file_extension = self._file_type.file_extension
        month_partitions: List[MonthPartition] = []
        for partition in partitions:
            if not self.check_partition(partition):
                raise NotImplementedError()
            month_partitions.append(cast(MonthPartition, partition))
        tag_name_upper = tag_name.upper()
        dirs_by_years: Dict[int, List[Tuple[str, Optional[FileInfo]]]] = {}
        for partition in month_partitions:
            if partition.year not in dirs_by_years:
                dir_path = fs.join(tag_dir, "parquet", str(partition.year))
                try:
                    dirs_by_years[partition.year] = list(fs.ls(dir_path))
                except FileNotFoundError:
                    logger.info("File not found '%s'", dir_path)
                    break
            files_list = dirs_by_years[partition.year]
            for path, file_info in files_list:
                _, file_name = fs.split(path)
                if cast(FileInfo, file_info).isfile():
                    file_name_expected = f"{tag_name_upper}_{partition.year}{partition.month:02d}{file_extension.upper()}"
                    if file_name.upper() == file_name_expected:
                        yield partition, path


class NcsYearlyParquetFileType(NcsFileType):
    """
    NCS yearly parquet files finder
    """

    def __init__(self):
        self._file_type = ParquetFileType(time_series_columns)
        self._partition_type = YearPartition

    @property
    def file_type(self) -> FileType:
        return self._file_type

    @property
    def partition_type(self) -> Type[Partition]:
        return YearPartition

    def paths(
        self,
        fs: FileSystem,
        tag_dir: str,
        tag_name: str,
        partitions: Iterable[Partition],
    ) -> Iterable[Tuple[Partition, str]]:
        file_extension = self._file_type.file_extension
        year_partitions: List[YearPartition] = []
        for partition in partitions:
            if not self.check_partition(partition):
                raise NotImplementedError()
            year_partitions.append(cast(YearPartition, partition))
        tag_name_upper = tag_name.upper()
        for partition in year_partitions:
            dir_path = fs.join(tag_dir, "parquet")
            try:
                files_list = list(fs.ls(dir_path))
            except FileNotFoundError:
                logger.info("File not found '%s'", dir_path)
                break
            for path, file_info in files_list:
                _, file_name = fs.split(path)
                if cast(FileInfo, file_info).isfile():
                    file_name_expected = (
                        f"{tag_name_upper}_{partition.year}{file_extension.upper()}"
                    )
                    if file_name.upper() == file_name_expected:
                        yield partition, path


class NcsCsvFileType(NcsFileType):
    """
    NCS CSV files finder
    """

    def __init__(self):
        header = ["Sensor", "Value", "Time", "Status"]
        self._file_type = CsvFileType(header, time_series_columns)
        self._partition_type = YearPartition

    @property
    def file_type(self) -> FileType:
        return self._file_type

    @property
    def partition_type(self) -> Type[Partition]:
        return self._partition_type

    def paths(
        self,
        fs: FileSystem,
        tag_dir: str,
        tag_name: str,
        partitions: Iterable[Partition],
    ) -> Iterable[Tuple[Partition, str]]:
        # TODO Make this case insensitive for tag_name
        file_extension = self._file_type.file_extension
        for partition in partitions:
            if not self.check_partition(partition):
                raise NotImplementedError()
            path = f"{tag_name}_{partition.year}{file_extension}"
            yield partition, fs.join(tag_dir, path)


ncs_file_types: Dict[str, Type[NcsFileType]] = {
    "parquet": NcsMonthlyParquetFileType,
    "yearly_parquet": NcsYearlyParquetFileType,
    "csv": NcsCsvFileType,
}

DEFAULT_TYPE_NAMES: List[str] = ["parquet", "yearly_parquet", "csv"]


def load_ncs_file_types(
    type_names: Optional[Iterable[str]] = None,
) -> List[NcsFileType]:
    """
    Returns list of ``NcsFileType`` instances from names of those types

    Parameters
    ----------
    type_names: Optional[Iterable[str]]
        List of ``NcsFileType`` names. Only supporting `parquet` and `csv` names values

    Returns
    -------
    List[NcsFileType]

    """
    if type_names is None:
        type_names = DEFAULT_TYPE_NAMES
    result = []
    for type_name in type_names:
        if type_name not in ncs_file_types:
            raise ConfigException("Can not find file type '%s'" % type_name)
        result.append(ncs_file_types[type_name]())
    return result
