"""AlmaLinux Git server utilities common functions"""

import hashlib
import logging
import os
import re
from typing import Iterator, Tuple

__all__ = ['configure_logger', 'detect_checksum_type', 'find_metadata_file',
           'get_file_checksum', 'iter_metadata', 'normalize_path']


def configure_logger(verbose: bool) -> logging.Logger:
    """
    Configures a console logger.

    Args:
        verbose: Show DEBUG messages if True, show INFO and higher otherwise.

    Returns:
        Configured logger.
    """
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler()
    handler.setLevel(level)
    log_format = "%(levelname)-8s: %(message)s"
    formatter = logging.Formatter(log_format, '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def detect_checksum_type(checksum: str) -> str:
    """
    Detects checksum by its length.

    Args:
        checksum: Checksum.

    Returns:
        Checksum type.
    """
    hash_types = {32: 'md5', 40: 'sha1', 64: 'sha256', 128: 'sha512'}
    hash_type = hash_types.get(len(checksum))
    if not hash_type:
        raise ValueError(f'unknown checksum type {checksum}')
    return hash_type


def find_metadata_file(path: str) -> str:
    """
    Finds a sources metadata file in the specified directory.

    Args:
        path: Directory to search in.

    Returns:
        Sources metadata file path.
    """
    files = [f for f in os.listdir(path) if re.match(r'^\.\S*?\.metadata$', f)]
    if not files:
        raise Exception('metadata file is not found')
    elif len(files) > 1:
        raise Exception('multiple metadata files found. Please specify one to '
                        'use')
    return os.path.join(path, files[0])


def get_file_checksum(file_path: str, checksum_type: str = 'sha1',
                      buff_size: int = 1048576) -> str:
    """
    Calculates a file checksum.

    Args:
        file_path: File path.
        checksum_type: Checksum type.
        buff_size: Number of bytes to read at once.

    Returns:
        File checksum.
    """
    hasher = hashlib.new(checksum_type)
    with open(file_path, 'rb') as fd:
        buff = fd.read(buff_size)
        while len(buff):
            hasher.update(buff)
            buff = fd.read(buff_size)
    return hasher.hexdigest()


def iter_metadata(metadata_path: str) -> Iterator[Tuple[str, str, str]]:
    """
    Iterates over records in a CentOS git repository-compatible metadata file.

    Args:
        metadata_path: Metadata file path.

    Returns:
        Iterator over files and their checksums.
    """
    with open(metadata_path, 'r') as fd:
        for line in fd:
            checksum, file_path = line.split()
            checksum_type = detect_checksum_type(checksum)
            yield file_path, checksum, checksum_type


def normalize_path(path: str) -> str:
    """
    Returns an absolute path with all variables expanded.

    Args:
        path: Path to normalize.

    Returns:
        Normalized path.
    """
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))
