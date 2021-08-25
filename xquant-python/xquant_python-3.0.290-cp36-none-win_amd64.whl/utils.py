from os.path import join, isfile, getsize, basename, isdir, realpath, expandvars, expanduser
from os import listdir, remove, makedirs, chmod
from shutil import copy
from .tools import price_util, time_util


def expand_path(path: str) -> str:
    """Performs full path expansion"""
    return realpath(expandvars(expanduser(path)))


def create_dir_if_not_exist(dir_name: str) -> None:
    """Creates given directory with all parents if it is not exist."""
    if not isdir(dir_name):
        makedirs(dir_name, mode=0o700, exist_ok=True)


def remove_file_if_exist(file_name: str) -> None:
    """Removes existing file"""
    if isfile(file_name):
        remove(file_name)


def copy_all_files(source: str, destination: str) -> None:
    """Copies all files from source directory to destination."""
    for file_name in listdir(source):
        from_path = join(source, file_name)
        to_path = join(destination, file_name)

        if isfile(from_path):
            copy(from_path, to_path)


def get_file_name_from_url(url: str) -> str:
    """
    Extracts file name from URL.
    """
    parts = url.split('/')
    result = parts[-1]
    pos = result.find('?')

    if pos != -1:
        result = result[:pos]

    return result
