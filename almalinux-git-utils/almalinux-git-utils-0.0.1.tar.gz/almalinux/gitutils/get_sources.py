"""Downloads sources and blobs from AlmaLinux or CentOS sources cache"""

import argparse
import logging
import os
import shutil
import sys

import requests

from almalinux.gitutils.common import (
    configure_logger, find_metadata_file, get_file_checksum, iter_metadata,
    normalize_path
)
from almalinux.gitutils.errors import ChecksumError, NetworkError


def init_arg_parser() -> argparse.ArgumentParser:
    """
    Initializes a command line arguments parser.

    Returns:
        Command line arguments parser.
    """
    arg_parser = argparse.ArgumentParser(prog='alma_get_sources',
                                         description=__doc__)
    arg_parser.add_argument('-i', '--input-metadata', metavar='INPUT_FILE',
                            help='input metadata file list to download')
    arg_parser.add_argument('--domain-name', default='sources.almalinux.org',
                            help='AlmaLinux sources server domain name. '
                                 'Default is sources.almalinux.org')
    arg_parser.add_argument('-v', '--verbose', action='store_true',
                            help='enable additional debug output')
    return arg_parser


def create_sources_dir(base_dir: str, rel_path: str):
    """
    Creates a sources directory if it doesn't exist.

    Args:
        base_dir: Project's base directory.
        rel_path: Project's source file relative path.
    """
    dir_name, file_name = os.path.split(rel_path)
    dir_path = os.path.join(base_dir, dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def download_alma_blob(file_path: str, checksum: str, domain_name: str):
    """
    Downloads a BLOB from the AlmaLinux Git sources cache.

    Args:
        file_path: Destination file path.
        checksum: File checksum.
        domain_name: AlmaLinux Git source cache domain name.
    """
    url = f'https://{domain_name}/{checksum}'
    with requests.get(url, stream=True) as rqst:
        try:
            rqst.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise NetworkError(str(e))
        with open(file_path, 'wb') as fd:
            shutil.copyfileobj(rqst.raw, fd)


def download_metadata_blobs(metadata_path: str, base_dir: str,
                            domain_name: str):
    """
    Downloads BLOBs listed in a metadata file from AlmaLinux Git sources cache.

    Args:
        metadata_path: Metadata file path.
        base_dir: Package sources base directory.
        domain_name: AlmaLinux Git sources cache domain name.
    """
    for rel_path, checksum, checksum_type in iter_metadata(metadata_path):
        file_path = os.path.join(base_dir, rel_path)
        if os.path.exists(file_path):
            real_checksum = get_file_checksum(file_path, checksum_type)
            if real_checksum != checksum:
                raise ChecksumError(
                    f"{rel_path} already exists but its {checksum_type} "
                    f"checksum {real_checksum} doesn't match expected "
                    f"{checksum}"
                )
            logging.info(f'{rel_path} already exists and its checksum is '
                         f'correct')
            continue
        create_sources_dir(base_dir, rel_path)
        download_alma_blob(file_path, checksum, domain_name)
        real_checksum = get_file_checksum(file_path, checksum_type)
        if real_checksum != checksum:
            raise ChecksumError(
                f"{rel_path} has been downloaded but its {checksum_type} "
                f"checksum {real_checksum} doesn't match expected {checksum}"
            )
        logging.info(f'{rel_path} has been successfully downloaded')


def main():
    arg_parser = init_arg_parser()
    args = arg_parser.parse_args(sys.argv[1:])
    configure_logger(args.verbose)
    base_dir = os.getcwd()
    if args.input_metadata:
        metadata_path = normalize_path(args.input_metadata)
    else:
        metadata_path = find_metadata_file(base_dir)
    try:
        download_metadata_blobs(metadata_path, base_dir, args.domain_name)
    except ChecksumError as e:
        logging.error(e)
        return os.EX_DATAERR
    except NetworkError as e:
        logging.error(e)
        return os.EX_IOERR
