"""Storage base class and factory."""
import abc
import importlib
import re
import shutil
import typing as t
from datetime import datetime, timezone
from pathlib import Path
from tempfile import gettempdir, mkdtemp

import pydicom
from diskcache import Cache
from fw_file.dicom.utils import get_timestamp
from fw_utils import AnyFile, BinFile, TempFile, parse_url
from memoization import cached
from pydicom.dataset import Dataset

from .fileinfo import FileInfo

DEFAULT_CACHE_SIZE = 1 << 30  # 1GB
SPOOLED_TMP_MAX_SIZE = 1 << 20  # 1MB
# map of url schemes to storage class import paths (and user-registered classes)
STORAGE_CLASSES: t.Dict[str, t.Union[str, t.Type["Storage"]]] = {
    "az": "fw_storage.types.az.AzureBlob",
    "dicom": "fw_storage.types.dicom.DICOM",
    "dicomweb": "fw_storage.types.dicomweb.DICOMweb",
    "fs": "fw_storage.types.fs.FileSystem",
    "gs": "fw_storage.types.gs.GoogleCloudStorage",
    "s3": "fw_storage.types.s3.S3",
}

AnyPath = t.Union[str, FileInfo]


class Storage(abc.ABC):
    """Abstract storage class defining the common interface."""

    # URL regex to parse and capture init args with
    url_re: t.ClassVar[t.Pattern]

    @abc.abstractmethod
    def abspath(self, path: AnyPath) -> str:
        """Return absolute path for a given path."""

    @abc.abstractmethod
    def ls(
        self,
        path: str = "",
        *,
        include: t.Optional[t.List[str]] = None,
        exclude: t.Optional[t.List[str]] = None,
        **kwargs: t.Any,
    ) -> t.Iterator[FileInfo]:
        """Yield items under path that match the include/exclude filters."""

    @abc.abstractmethod
    def stat(self, path: str) -> FileInfo:
        """Return FileInfo for a single file."""

    @abc.abstractmethod
    def get(self, path: AnyPath, **kwargs: t.Any) -> BinFile:
        """Return a file opened for reading in binary mode."""

    @abc.abstractmethod
    def set(self, path: AnyPath, file: t.Union[AnyFile, bytes]) -> None:
        """Write a file at the given path in storage."""

    @abc.abstractmethod
    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Remove file from storage."""

    @staticmethod
    def relpath(path: AnyPath) -> str:
        """Return relative path for a given path/fileinfo."""
        return (path.path if isinstance(path, FileInfo) else path).lstrip("/")

    def check_access(self):
        """Return that storage is accessible."""

    def check_perms(self, write=False):
        """Check that storage is accessible and optionally writable."""
        self.check_access()
        if write:
            self.set("fw-storage-permcheck", b"permcheck")
            self.rm("fw-storage-permcheck")
            self.cleanup()

    def cleanup(self) -> None:
        """Run any cleanup steps for the storage (eg. tempfiles, buffers)."""

    def __enter__(self):
        """Enter storage 'with' context to enable automatic cleanup()."""
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        """Invoke cleanup() when exiting the storage 'with' context."""
        self.cleanup()

    def __del__(self) -> None:
        """Invoke cleanup() when the storage is garbage-collected."""
        self.cleanup()


class CloudStorage(Storage):
    """Base class for Cloud Storages."""

    delete_batch_size: t.ClassVar[int] = 1000

    def __init__(  # pylint: disable=unused-argument
        self,
        *args: t.Any,
        write: bool = False,
        cache_dir: str = None,
        cache_size: int = DEFAULT_CACHE_SIZE,
        **kwargs: t.Any,
    ):
        """Initialize cloud storage, check permission and setup cache."""
        self._cache = None
        self.cache_root = cache_dir or gettempdir()
        self.cache_dir = Path(mkdtemp(prefix="fw-storage-", dir=self.cache_root))
        self.cache_size = int(cache_size)
        self.delete_keys: t.Set[str] = set()
        self.check_perms(write=write)

    @abc.abstractmethod
    def download_file(self, path: str, dst: t.IO[bytes]) -> None:
        """Download file and it opened for reading in binary mode."""

    @abc.abstractmethod
    def upload_file(self, path: str, file: t.Union[str, bytes, t.IO[bytes]]) -> None:
        """Upload file to the given path."""

    @abc.abstractmethod
    def flush_delete(self):
        """Flush pending remove operations."""

    @property
    def cache(self):
        """Get underlying cache object.

        Cache is created on the first access or recreated
        if cleanup was called in the meantime.
        """
        if not self._cache and self.cache_size > 0:
            self._cache = Cache(
                directory=self.cache_dir,
                size_limit=self.cache_size,
                eviction_policy="least-recently-used",
            )
        return self._cache

    def cache_get(self, key: str) -> t.Optional[t.IO[bytes]]:
        """Get item from cache if enabled."""
        if self.cache is not None:
            return t.cast(t.IO[bytes], self.cache.get(key, read=True))
        return None

    def cache_set(self, key: str, file: t.IO[bytes]) -> None:
        """Set cache item if enabled."""
        if self.cache is not None:
            self.cache.set(key, file, read=True)

    def cache_del(self, key: str) -> None:
        """Remove item from cache if enabled."""
        if self.cache is not None:
            self.cache.delete(key)

    def get(  # pylint: disable=arguments-differ
        self, path: AnyPath, cache: bool = True, **_
    ) -> BinFile:
        """Return a file opened for reading in binary mode."""
        abspath = self.abspath(path)
        if cache and (f := self.cache_get(abspath)):
            return BinFile(f, metapath=self.relpath(path))
        file = TempFile()
        self.download_file(abspath, file)
        size = file.tell()
        file.seek(0)
        if cache and size < self.cache_size:
            self.cache_set(abspath, file)
            file.seek(0)
        return BinFile(file, metapath=self.relpath(path))

    def set(self, path: AnyPath, file: t.Union[AnyFile, bytes]) -> None:
        """Write a file at the given path in storage."""
        path = self.abspath(path)
        file = str(file) if isinstance(file, Path) else file
        self.upload_file(path, file)
        self.cache_del(path)

    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Remove file from storage.

        Removing objects is delayed and performed in batches (see 'flush_delete').
        """
        path = path.path if isinstance(path, FileInfo) else path
        if recurse:
            for fileinto in self.ls(path):
                self.delete_keys.add(self.abspath(fileinto.path))
        else:
            self.delete_keys.add(self.abspath(path))
        if len(self.delete_keys) == self.delete_batch_size:
            self.flush_delete()

    def cleanup(self):
        """Flush pending remove operations and clear cache."""
        self._cache = None
        if hasattr(self, "cache_dir"):
            shutil.rmtree(self.cache_dir, ignore_errors=True)
        if hasattr(self, "delete_keys") and self.delete_keys:
            for key in self.delete_keys:
                self.cache_del(key)
            self.flush_delete()


class DicomBaseStorage(Storage):
    """Base class for DICOM storages."""

    UID_RE = r"\d+[\.\d+]*"
    PATH_RE_OPTIONAL = fr"^((?P<study>{UID_RE})(/(?P<series>{UID_RE}))?)?$"
    PATH_RE_REQUIRED = fr"(?P<study>{UID_RE})/(?P<series>{UID_RE})"
    PATH_RE_STUDY_REQ = fr"^(?P<study>{UID_RE})(/(?P<series>{UID_RE}))?$"

    @abc.abstractmethod
    def get(self, path: AnyPath, **kwargs: t.Any) -> AnyPath:  # type: ignore
        """Return path to downloaded series."""
        # pylint: disable=arguments-differ

    @abc.abstractmethod
    def set(self, file: AnyPath) -> None:  # type: ignore
        """Write a file at the given path in storage."""
        # pylint: disable=arguments-differ

    @abc.abstractmethod
    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Remove file from storage."""

    @abc.abstractmethod
    def stat(self, path: str) -> FileInfo:
        """Return FileInfo for a single file."""

    def abspath(self, path: AnyPath) -> str:
        """Return absolute path for a given path."""
        return path.path if isinstance(path, FileInfo) else path

    def result_to_fileinfo(self, ds: Dataset) -> FileInfo:
        """Fills the FileInfo from a dict."""
        study_uid = ds.StudyInstanceUID
        series_uid = ds.SeriesInstanceUID
        self.correct_image_count(ds)
        size = ds.get("NumberOfSeriesRelatedInstances", 0)
        dt = get_timestamp(ds, "Series")
        if dt:
            timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
        else:
            timestamp = datetime.utcnow().timestamp()
        return FileInfo(
            path=f"{study_uid}/{series_uid}",
            size=size,
            created=timestamp,
            modified=timestamp,
        )

    def correct_image_count(self, ds: Dataset) -> None:
        """Correct image count of Dataset.

        Only tries to correct if NumberOfSeriesRelatedInstances not present or zero.
        """
        if not ds.get("NumberOfSeriesRelatedInstances"):
            count = self.get_image_count(ds.StudyInstanceUID, ds.SeriesInstanceUID)
            ds.NumberOfSeriesRelatedInstances = count

    @abc.abstractmethod
    def get_image_count(self, study_uid: str, series_uid: str) -> int:
        """Get image count of a series."""

    @staticmethod
    def apply_path_re(
        path_re: str, path: str
    ) -> t.Tuple[t.Optional[str], t.Optional[str]]:
        """Aplly regex on the given path to extract study/series uids."""
        match = re.match(path_re, path)
        if not match:
            raise ValueError(f"Invalid DICOM study/series path: {path}")
        return match.group("study"), match.group("series")

    @staticmethod
    def parse_filters_to_dict(filters: t.List[str]) -> t.Dict[str, str]:
        """Parse list of strings into filter dict."""
        filt_dict = {}
        for filt in filters:
            try:
                key, value = filt.split("=", maxsplit=1)
                filt_dict[key] = value
            except ValueError as exc:
                raise ValueError("Missing filter key or value") from exc
        return filt_dict

    @staticmethod
    def apply_exclude_filters(ds: Dataset, filters: t.Dict[str, str]) -> bool:
        """Apply exclude filters on dataset."""
        for key, value in filters.items():
            field = ds.get(int(DicomBaseStorage.param_to_tag(key), 16))
            if field is None:
                continue
            if field.VR in ("DA", "TM"):
                if "-" in value:
                    minimum, maximum = value.split("-")
                    if minimum and minimum <= field.value:
                        if not maximum:
                            return True
                        if field.value <= maximum:
                            return True
            elif field.VR == "UI":
                if "," in value:
                    if field.value in value.split(","):
                        return True
            if field.value == value:
                return True
        return False

    @staticmethod
    def param_to_tag(param: str) -> str:
        """Get DICOM tag string for query param."""
        if param in pydicom.datadict.keyword_dict:
            tag = f"{pydicom.datadict.tag_for_keyword(param):08x}"
        else:
            tag = param
        pydicom.datadict.keyword_for_tag(tag)
        return tag


class StorageError(Exception):
    """Storage error base class."""

    def __init__(self, message: str, errors: t.Optional[t.List[str]] = None):
        """Initialize exception."""
        super().__init__(message)
        self.errors = errors


class FileNotFound(StorageError):
    """File not found."""


class PermError(StorageError):
    """Permission error."""


def get_storage(storage_url: str, **kwargs) -> Storage:
    """Return storage instance for a storage URL (factory)."""
    parsed = parse_url(storage_url)
    scheme = parsed["scheme"]
    if scheme not in STORAGE_CLASSES:
        raise ValueError(f"Unknown storage URL scheme {scheme}")
    storage_cls = STORAGE_CLASSES[scheme]
    if isinstance(storage_cls, str):
        storage_cls = get_storage_cls(storage_cls)
    storage_kw = parse_url(storage_url, storage_cls.url_re)
    storage_kw.update(kwargs)
    return storage_cls(**storage_kw)  # type: ignore


@cached
def get_storage_cls(storage_cls_path: str) -> t.Type[Storage]:
    """Return the storage class for an import path (late import)."""
    module_path, cls_name = storage_cls_path.rsplit(".", maxsplit=1)
    try:
        module = importlib.import_module(module_path, cls_name)
        storage_cls = getattr(module, cls_name)
    except (ImportError, AttributeError) as exc:
        msg = f"Cannot import storage class {storage_cls_path} ({exc})"
        raise ValueError(msg) from exc
    return storage_cls
