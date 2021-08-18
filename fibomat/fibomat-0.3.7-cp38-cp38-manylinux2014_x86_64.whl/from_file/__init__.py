"""Module provides support for import of vector graphics."""
from typing import List
import pathlib

from fibomat.shapes import Shape

from fibomat.from_file.dxf import shapes_from_dxf
from fibomat.from_file.svg import shapes_from_svg
from fibomat.utils import PathLike


def shapes_from_file(file_path: PathLike) -> List[Shape]:
    """Parse a vector graphic file and return the contained data mapped to fib-o-mat shape types.

    The file type is determined by the file_path suffix. Currently supported is only dfx-format.

    Args:
        file_path (PathLike): file to be parsed

    Returns:
        List[Shapes]

    Raises:
        RuntimeError: Raised if provided file is not valid.
        RuntimeError: Raised if provided file format is not supported.
    """
    file_path = pathlib.Path(file_path).absolute()

    if not file_path.is_file():
        raise RuntimeError(f'"{file_path}" is not a valid file')

    suffix = file_path.suffix

    if suffix == '.dxf':
        return shapes_from_dxf(file_path)
    elif suffix == '.svg':
        return shapes_from_svg(file_path)

    raise RuntimeError(f'Cannot import file with extension "{suffix}"')
