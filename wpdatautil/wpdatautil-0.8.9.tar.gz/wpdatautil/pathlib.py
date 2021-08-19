"""pathlib utilities."""
import urllib.parse
from pathlib import Path


def ensure_parent_dir(path: Path) -> None:
    """Ensure that the parent directory of the given path exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


def path_to_uri(path: Path) -> str:
    """Return the unquoted URI corresponding to the given path."""
    return urllib.parse.unquote(path.as_uri())  # Note: unquote replaces '%3D' with '=' as is often required.
