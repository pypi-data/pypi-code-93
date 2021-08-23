"""Write me."""
import pathlib
import sys


def get_temporary_directory(subdirectory=""):  # PRAGMA: no cover
    if sys.platform in ["win32", "cygwin"]:
        temp_dir = pathlib.Path(f"%userprofile%/AppData/Local/Temp/moped/{subdirectory}")
    else:
        temp_dir = pathlib.Path(f"/tmp/moped/{subdirectory}")
    if not temp_dir.is_dir():
        temp_dir.mkdir(parents=True)
    return temp_dir
