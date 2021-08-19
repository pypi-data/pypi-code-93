"""
Defines algorithms to locate any workRID in a complex of:
-   share points, numbered 0..n (the actual file server and client determines the
    full path. The share point returned is a digit, it's up to the file server to
    serve a resource that ends in a digit. (the client has a mount point which can
    be any arbitrary string, as long as it ends in a digit.
    Ex:  Rackstation 5 (TBRCRS5) has share points Archive0 and Archive1
    - MacOS Client mounts these shares as /Volumes/Archive0 and /Volumes/Archive1
    - Linux client can be more flexible, but for scripts sake it should be the same:
        - /mnt/Archive0 mounts /RS5/Archive0
        - /mnt/Archive1 mounts /RS5/Archive1
-   buckets: the location of the work in a set of sub folders of the share point
"""
import os
from hashlib import md5
from pathlib import Path


def build_path(root: str, branch: object,leaf_str: str) -> str:
    """
    Filter to preserve remote URLs in root (e.g. s3://somewhere)
    :param root: parent of branch
    :param branch: intermediate part of resolution
    :param leaf_str: last directory in resolution path
    :return:
    """
    if '://' not in root:
        return str(Path(root, str(branch), leaf_str))
    return root + os.sep + str(Path( str(branch), leaf_str))


def r_divmod_50_b_md5_5(parent: str, archive_name: str) -> ():
    """
    Maps a named work to a
    :return: tuple of strings: 'root'  ( 0 <= root <= 1) bucket ( 0x00 <= bucket  0xFF)
    if 'archive_name' ends in two characters, its root is 0
    'root' is calculated:
        let r = int(md5_hash(archive_name)[:2])
        return ( r - 50 > 0 ) ? 1 : 0
    are returned as a conversion to hex of 'r'
    :param parent: containing path
    :param archive_name: suffix
    """

    # First 2 characters of hex digest
    bucket = md5(str.encode(archive_name)).hexdigest()[:2]
    root: int = 0

    try:
        bucket_int = int(bucket, 16)
        # noinspection PyPep8Naming
        root, mod_dont_care = divmod(bucket_int, 50)
    except ValueError:
        # We just take the default if conversion throws
        bucket_int = 0
        pass

    resolved_root = parent + "{:d}".format(root)
    return build_path(resolved_root, f"{bucket_int:02x}",archive_name)


def r_divmod_50_b_2(parent: str, archive_name: str) -> ():
    """
    Maps a named work to a
    :return: tuple of strings: 'root'  ( 0 <= root <= 1) bucket ( 00 <= bucket  99)
    if 'archive_name' ends in two characters, its root is 0
    'root' is calculated:
        let r = int(archive_name[-2:])
        return ( r - 50 > 0 ) ? 1 : 0
    the last two characters of the work name
    evaluate to between 0 and 99
    :param parent: containing path
    :param archive_name: suffix
    """
    bucket = archive_name[-2:]
    root: int = 0
    try:

        bucket_int = int(bucket)
        root, mod_dont_care = divmod(bucket_int, 50)
    except ValueError:
        # We just take the default if conversion throws
        bucket_int = 0
        pass
    # return "{:d}".format(root), "{:02d}".format(bucket_int)
    resolved_root = parent + "{:d}".format(root)
    return build_path(resolved_root, f"{bucket_int:02d}", archive_name)


def r_null(parent: str, archive_name: str) -> ():
    """
    Null case , to test clients. Returns tuple of empty strings
    :type archive_name: str
    :param parent: containing path
    :param archive_name: work RID to resolve
    :return: Straight concatenation
    """
    return build_path(parent, "", archive_name)


def r_s3(parent: str, archive_name: str) -> ():
    """
    Returns the S3 bucket
    :param parent: containing path
    :param archive_name: work RID to resolve
    :return: S3 Resolution (first 2 digits of hex)
    """
    return build_path(parent, md5(str.encode(archive_name)).hexdigest()[:2],archive_name)
