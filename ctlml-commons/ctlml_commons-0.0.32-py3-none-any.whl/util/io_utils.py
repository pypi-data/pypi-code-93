import bz2
import csv
import errno
import os
from typing import Any, List


def ensure_exists(file_path: str) -> None:
    path: str = os.path.dirname(file_path)

    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def file_exists(path: str) -> bool:
    return os.path.exists(path)


def file_remove(path: str) -> None:
    os.remove(path)


def write_csv_data(path: str, header: List[str], data: List[Any], update_type: str = "w", as_bz2: bool = False) -> None:
    if as_bz2:
        with bz2.open(filename=path, mode="wt") as f:
            write(obj=f, header=header, data=data)
    else:
        with open(file=path, mode=update_type, newline="\n") as f:
            write(obj=f, header=header, data=data)


def write(obj: Any, header: List[str], data: List[Any]) -> None:
    writer = csv.writer(obj, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    if header and len(header) > 0:
        writer.writerow(header)

    for row in data:
        writer.writerow(row)
