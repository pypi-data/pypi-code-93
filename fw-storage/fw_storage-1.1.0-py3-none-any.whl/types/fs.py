"""Local storage module."""
import functools
import os
import re
import shutil
import typing as t
from pathlib import Path

from fw_utils import AnyFile, BinFile

from .. import FileNotFound, PermError, Storage
from ..fileinfo import FileInfo
from ..filters import DirFilter, Filters, create_filter
from ..storage import AnyPath

__all__ = ["FileSystem"]

CHUNKSIZE = 8 << 20
FILTER_FACTORY = {"dir": DirFilter}


def translate_error(func):
    """Raise storage errors from built-in filesystem errors."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as exc:
            msg = re.sub(r"\[.*\]\s*(.*)", r"\1", str(exc))
            raise FileNotFound(msg) from exc
        except PermissionError as exc:
            msg = re.sub(r"\[.*\]\s*(.*)", r"\1", str(exc))
            raise PermError(msg) from exc

    return wrapper


class FileSystem(Storage):
    """Storage class for locally mounted filesystems."""

    url_re = re.compile(r"fs://(?P<path>[^?]*)(\?(?P<query>[^#]+))?")

    def __init__(
        self,
        path: t.Union[str, Path] = "",
        uid: t.Optional[int] = None,
        gid: t.Optional[int] = None,
        write: bool = False,
    ) -> None:
        """Init FileSystem storage from a path (default: cwd)."""
        path = Path(path) if path else Path.cwd()
        self.prefix = path.expanduser().resolve()
        self.gid = int(gid) if gid else None
        self.uid = int(uid) if uid else None
        self.check_perms(write=write)

    def abspath(self, path: AnyPath) -> str:
        """Return absolute path for a given path."""
        return str(self.prefix / self.relpath(path))

    def check_access(self):
        """Check that root folder exists."""
        if not self.prefix.exists():
            raise FileNotFound(f"Root dir not found: {self.prefix!r}")

    @translate_error
    def ls(  # pylint: disable=arguments-differ
        self,
        path: str = "",
        *,
        include: Filters = None,
        exclude: Filters = None,
        followlinks: bool = False,
        **_,
    ) -> t.Iterator[FileInfo]:
        """Yield each item under prefix matching the include/exclude filters."""
        # pylint: disable=too-many-locals
        # TODO consider adding in some retries/tolerance for network mounts
        start = (self.prefix / path).resolve()
        filt = create_filter(include=include, exclude=exclude, factory=FILTER_FACTORY)
        rel_dirs: t.List[str] = []
        rel_files: t.List[str] = []

        for root, dirs, files in os.walk(start, followlinks=followlinks):

            def rel(name: str) -> str:
                """Return path relative to prefix for given file/dir-name."""
                # pylint: disable=cell-var-from-loop
                return re.sub(fr"^{self.prefix}", "", f"{root}/{name}").strip("/")

            # remove first dir from dirs buffer since it's the current root dir
            if rel_dirs:
                # make sure that this invariant is true
                assert rel_dirs.pop(0) == rel("")
            # sort the dirs to enforce deterministic walk order
            # apply the dir filters to efficiently prune the walk tree
            dirs.sort()
            dirs[:] = [d for d in dirs if filt.match(rel(d), keys=["dir"])]
            # apply the path filters before using os.stat for efficiency
            files = [rel(f) for f in files if filt.match(rel(f), keys=["path"])]
            # keep relative dir and file pathes in a buffer to help
            # interleaving the dirs and files to have total ordering
            rel_dirs.extend([rel(d) for d in dirs])
            rel_dirs.sort()
            rel_files.extend(files)
            rel_files.sort()

            while rel_files:
                if rel_dirs and rel_dirs[0] < rel_files[0]:
                    # stop yield if the next dir is before
                    # the current file in sort order
                    break

                # yield the matching files from this dir
                info = self.stat(rel_files.pop(0))
                if filt.match(info):
                    yield info

    @translate_error
    def stat(self, path: str) -> FileInfo:
        """Return FileInfo using os.stat for a single file."""
        stat = (self.prefix / path).stat()
        return FileInfo(
            path=path,
            size=stat.st_size,
            created=stat.st_ctime,
            modified=stat.st_mtime,
        )

    @translate_error
    def get(self, path: AnyPath, **_) -> BinFile:
        """Open file for reading in binary mode."""
        return BinFile(self.abspath(path), metapath=self.relpath(path))

    @translate_error
    def set(self, path: AnyPath, file: t.Union[AnyFile, bytes]) -> None:
        """Write file to the given storage path."""
        path_ = Path(self.abspath(path))
        path_.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(file, bytes):
            path_.write_bytes(file)
        else:
            with BinFile(file) as r_file, BinFile(path_, mode="wb") as w_file:
                while data := r_file.read(CHUNKSIZE):
                    w_file.write(data)
        if self.gid or self.uid:
            path_parts = path_.relative_to(self.prefix).parts
            for i in range(len(path_parts)):
                rel_p = "/".join(path_parts[: i + 1])
                shutil.chown(self.prefix / rel_p, user=self.uid, group=self.gid)

    @translate_error
    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Remove a file at the given path."""
        path_ = Path(self.abspath(path))
        if path_.is_dir():
            if not recurse:
                raise ValueError("Cannot remove dir (use recurse=True)")
            shutil.rmtree(path_)
        else:
            path_.unlink()

    def __repr__(self) -> str:
        """Return string representation of the storage."""
        return f"{type(self).__name__}('{self.prefix}')"
