"""File-info module."""
import dataclasses
import typing as t


@dataclasses.dataclass(frozen=True)
class FileInfo:
    """FileInfo dataclass yielded from storage.ls() calls.

    Path is unique and relative to the storage prefix. Slots minimize memory
    usage to allow storing large number of FileInfo instances at once.
    """

    __slots__ = ("path", "size", "created", "modified")

    path: str
    size: int
    created: t.Optional[t.Union[int, float]]
    modified: t.Optional[t.Union[int, float]]
