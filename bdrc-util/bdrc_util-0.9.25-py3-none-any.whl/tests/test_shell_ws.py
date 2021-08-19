import logging
from pathlib import Path

from archive_ops.shell_ws import get_mappings
from archive_ops.Resolvers import Resolvers

#
# In pyCharm, th
#

def one_method(root: str, archive: str, expected_val: str, resolver: Resolvers):
    actual_val: str = get_mappings(root, archive, resolver)

    logging.debug(f" method {resolver}, expected {expected_val}, actual: {actual_val}")

    assert expected_val == actual_val, f'expected: {expected_val} actual: {actual_val} '

def log_level(caplog: object) -> None:
    """
    Set the logging level for a test
    :param caplog:
    :return:
    """
    caplog.set_level(logging.DEBUG)


def test_default_mappings(caplog):
    log_level(caplog)
    my_root: str = "expected_root"
    my_archive: str = "ExpectedArchive49"
    one_method(my_root, my_archive, my_root + "0/" + "49/" + my_archive, Resolvers.DEFAULT)


def test_last2_mappings(caplog):
    log_level(caplog)
    my_root: str = "expected_root"
    my_archive: str = "ExpectedArchive49"
    one_method(my_root, my_archive, my_root + "0/" + "49/" + my_archive, Resolvers.TWO)


def test_S3_mappings(caplog):
    log_level(caplog)
    my_root: str = "expected_root"
    my_archive: str = "ExpectedArchive49"
    one_method(my_root, my_archive, my_root + "/0f/" + my_archive, Resolvers.S3_BUCKET)



def test_null_mappings(caplog):
    log_level(caplog)
    my_root: str = "expected_root"
    my_archive: str = "ExpectedArchive49"

    one_method(my_root, my_archive, Path(my_root ,  my_archive).as_posix(), Resolvers.NULL)


def test_last2_is_default_mappings(caplog):
    log_level(caplog)
    my_root: str = "expected_root"
    my_archive: str = "ExpectedArchive49"
    expected: str = get_mappings(my_root, my_archive, Resolvers.TWO)
    one_method(my_root, my_archive, expected, Resolvers.DEFAULT)
