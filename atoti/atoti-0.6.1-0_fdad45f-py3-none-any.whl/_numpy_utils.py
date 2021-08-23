import tempfile
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from ._file_utils import _make_atoti_tempdir


def numpy_to_temporary_csv(
    array: np.ndarray,  # type: ignore
    *,
    columns: Sequence[str],
    separator: str,
    prefix: Optional[str] = None
) -> Path:
    """Convert a NumPy 2D ndarray to a temporary CSV file.

    Args:
        array: The array to convert.
        columns: The column names for the csv.
        separator: The separator to use.
        prefix: The prefix to give to the randomly generated filename.

    Returns:
        The path to the temporary file.
    """
    tempdir: str = _make_atoti_tempdir()
    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        dir=tempdir,
        suffix=".csv",
        encoding="utf8",
        prefix=prefix,
    ) as file_path:
        header = separator.join(columns)

        np.savetxt(
            file_path, array, fmt="%s", delimiter=separator, header=header, comments=""
        )
        return Path(file_path.name)
