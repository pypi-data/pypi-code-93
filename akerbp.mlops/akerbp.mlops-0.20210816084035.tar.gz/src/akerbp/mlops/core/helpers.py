# helpers.py
import os
from pathlib import Path

from akerbp.mlops.core import logger


logging=logger.get_logger(name='mlops_core')

def get_top_folder(path):
    """
    Get the top folder of a path.

    Input:
        - path: (str or Path) 

    Output:
        - (str or Path, depending on input) top parent folder in path
    """
    if isinstance(path, str):
        return path.split(os.sep)[0]
    elif isinstance(path, Path):
        return path.parents[len(path.parents)-2]


def as_import_path(file_path):
    if file_path:
        if not isinstance(file_path, str):
            file_path=str(file_path)
        return file_path.replace(os.sep,'.').replace('.py','')
    else:
        logging.debug(f"Empty file path -> empty import path returned")
