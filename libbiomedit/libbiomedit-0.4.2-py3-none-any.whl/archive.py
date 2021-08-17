import tarfile
import zipfile
from abc import ABC, abstractmethod
from contextlib import contextmanager
from os import PathLike
from typing import IO, List, Union

from . import unwrap


class ArchiveReaderInterface(ABC):
    @classmethod
    @abstractmethod
    def opener(cls, path: Union[str, PathLike]):
        """Open archive for reading"""

    @staticmethod
    @abstractmethod
    def is_valid_type(path: Union[str, PathLike]) -> bool:
        """Check if an archive file has a valid type"""

    @abstractmethod
    def namelist(self) -> List[str]:
        """Return a list of archive members by name"""

    @abstractmethod
    def extract_member(self, name: str) -> IO[bytes]:
        """Get a member from the archive as a file object"""


class ZipReader(zipfile.ZipFile, ArchiveReaderInterface):
    @classmethod
    def opener(cls, path: Union[str, PathLike]):
        return cls(path)  # pylint: disable=consider-using-with

    @staticmethod
    def is_valid_type(path: Union[str, PathLike]) -> bool:
        """Check if an archive file is a ZIP file"""
        return zipfile.is_zipfile(path)

    def extract_member(self, name: str) -> IO[bytes]:
        """Get a member from the archive as a file object"""
        try:
            return self.open(name)  # pylint: disable=consider-using-with
        except KeyError as e:
            raise KeyError(f"File object {name} not found in {self.filename}") from e


class TarReader(tarfile.TarFile, ArchiveReaderInterface):
    @classmethod
    def opener(cls, path: Union[str, PathLike]):
        # pylint: disable=consider-using-with
        return cls.open(path, format=tarfile.PAX_FORMAT)

    @staticmethod
    def is_valid_type(path: Union[str, PathLike]) -> bool:
        """Check if an archive file is a TAR file"""
        return tarfile.is_tarfile(path)

    def namelist(self) -> List[str]:
        """Return a list of archive members by name"""
        return self.getnames()

    def extract_member(self, name: str) -> IO[bytes]:
        """Get a member from the archive as a file object"""
        try:
            return unwrap(self.extractfile(name))
        except (KeyError, ValueError) as e:
            raise KeyError(f"File object {name} not found in {str(self.name)}") from e


@contextmanager
def archive_reader(path: Union[str, PathLike]):
    if ZipReader.is_valid_type(path):
        with ZipReader.opener(path) as zip_reader:
            yield zip_reader
    elif TarReader.is_valid_type(path):
        with TarReader.opener(path) as tar_reader:
            yield tar_reader
    else:
        raise TypeError(
            f"Input file '{path}' is not a .zip or .tar archive.\n"
            "Only .zip and .tar files can be used as input."
        )
