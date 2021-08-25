"""Uploads sources and BLOBs to the AlmaLinux sources cache"""

import argparse
import logging
import os
import sys
from typing import Iterator, List, Optional, Tuple

import boto3
import botocore.exceptions

from almalinux.gitutils.errors import ChecksumError
from almalinux.gitutils.common import (
    configure_logger, find_metadata_file, get_file_checksum, iter_metadata,
    normalize_path
)


def init_arg_parser() -> argparse.ArgumentParser:
    """
    Initializes a command line arguments parser.

    Returns:
        Command line arguments parser.
    """
    arg_parser = argparse.ArgumentParser(
        prog="alma_blob_upload",
        description="Uploads sources and BLOBs to the AlmaLinux sources cache"
    )
    group = arg_parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--file', nargs='+', help='file(s) to upload')
    group.add_argument('-i', '--input-metadata', metavar='INPUT_FILE',
                       help='input metadata file list to upload. Will be '
                            'detected automatically if omitted and no files '
                            'provided')
    arg_parser.add_argument('-b', '--bucket', default="sources.almalinux.org",
                            help='Amazon S3 bucket name. Default is '
                                 'sources.almalinux.org')
    arg_parser.add_argument('-o', '--output-metadata', metavar='OUTPUT_FILE',
                            help='output metadata file path')
    arg_parser.add_argument('-p', '--private', action='store_true',
                            help='set uploaded file mode to private. All '
                                 'uploaded files are public by default')
    arg_parser.add_argument('--domain-name', default='sources.almalinux.org',
                            help='AlmaLinux sources server domain name. '
                                 'Default is sources.almalinux.org')
    arg_parser.add_argument('-v', '--verbose', action='store_true',
                            help='enable additional debug output')
    return arg_parser


def iter_files(files: List[str]) -> Iterator[Tuple[str, str, str]]:
    """
    Iterates over a list of files and calculates checksums for them.

    Args:
        files: List of files.

    Returns:
        Iterator over files and their checksums.
    """
    checksum_type = 'sha1'
    for rel_path in files:
        file_path = normalize_path(rel_path)
        checksum = get_file_checksum(file_path, checksum_type)
        yield rel_path, checksum, checksum_type


def is_file_exist(s3_client, bucket_name: str, checksum: str) -> bool:
    """
    Checks is a file with a given checksum is already uploaded.
    Args:
        s3_client: Amazon S3 client.
        bucket_name: S3 bucket name.
        checksum: File checksum.

    Returns:
        True if a file is already uploaded, False otherwise.
    """
    try:
        s3_client.head_object(Bucket=bucket_name, Key=checksum)
        return True
    except botocore.exceptions.ClientError:
        return False


def upload_file(s3_client, bucket_name: str, file_path: str,
                checksum: str, private: bool):
    """
    Uploads a file to an Amazon S3 bucket.

    Args:
        s3_client: Amazon S3 client.
        bucket_name: S3 bucket name.
        file_path: File path.
        checksum: File checksum.
        private: False if file should be public, True otherwise.
    """
    acl = 'bucket-owner-full-control' if private else 'public-read'
    s3_client.upload_file(file_path, bucket_name, checksum,
                          ExtraArgs={'ACL': acl})


def get_file_iterator(
        files: List[str], metadata_path: Optional[str]
) -> Iterator[Tuple[str, str, str]]:
    """
    Finds a suitable file iterator for given arguments.

    Args:
        files: List of files.
        metadata_path: Metadata file path.

    Returns:
        File iterator.
    """
    if files:
        iterator = iter_files(files)
    else:
        if not metadata_path:
            metadata_path = find_metadata_file(os.getcwd())
        iterator = iter_metadata(metadata_path)
    return iterator


def main():
    arg_parser = init_arg_parser()
    args = arg_parser.parse_args(sys.argv[1:])
    configure_logger(args.verbose)
    s3_client = boto3.client('s3')
    iterator = get_file_iterator(args.file, args.input_metadata)
    out_fd = None
    if args.output_metadata:
        out_fd = open(args.output_metadata, 'w')
    try:
        for rel_path, checksum, checksum_type in iterator:
            file_path = normalize_path(rel_path)
            if not args.file:
                real_checksum = get_file_checksum(file_path, checksum_type)
                if real_checksum != checksum:
                    raise ChecksumError(
                        f"{rel_path} {checksum_type} checksum {real_checksum} "
                        f"doesn't match expected {checksum}"
                    )
            file_url = f'https://{args.domain_name}/{checksum}'
            if not is_file_exist(s3_client, args.bucket, checksum):
                upload_file(s3_client, args.bucket, file_path, checksum,
                            args.private)
                logging.info(f'{rel_path} successfully uploaded: {file_url}')
            else:
                logging.info(f'{rel_path} is already uploaded: {file_url}')
            if out_fd:
                out_fd.write(f'{checksum} {rel_path}\n')
    finally:
        if out_fd:
            out_fd.close()
