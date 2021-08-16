"""
Dipl log parser tests
"""
from unittest.mock import patch
import sys
from archive_ops.DipLog import DipLogParser
import pytest

# For when you need sys.argv
# try:
#     # python 3.4+ should use builtin unittest.mock not mock package
#     from unittest.mock import patch
# except ImportError:
#     from mock import patch
#
# def test_parse_args():
#     testargs = ["prog", "-f", "/home/fenton/project/setup.py"]
#     with patch.object(sys, 'argv', testargs):

def test_when_src_arg_uses_positional_as_dest():
    """
    Happy Path - all is given
    :return:
    """

    # Arrange
    expected_source_path: str = "expectedSourcePath"
    expected_dest_path: str = "expectedDestPath"
    testargs = ["prog", "-i", "6666-666-666-4242", "-a", "DRS", "-b", "2021-08-01 00:00:00", "-w", "WDipLogArgTest", "-s", expected_source_path,expected_dest_path]
    with patch.object(sys, 'argv', testargs):
        # Act
        dlp = DipLogParser("","")
        # Assert
        assert dlp.parsedArgs.dip_source_path == expected_source_path
        assert dlp.parsedArgs.dip_dest_path == expected_dest_path


def test_when_dest_arg_uses_positional_as_src():
    """
    Happy Path - all is given
    :return:
    """

    # Arrange
    expected_source_path: str = "expectedSourcePath"
    expected_dest_path: str = "expectedDestPath"
    testargs = ["prog", "-i", "6666-666-666-4242",  "-t", expected_dest_path, expected_source_path]
    with patch.object(sys, 'argv', testargs):
        # Act
        dlp = DipLogParser("","")
        # Assert
        assert dlp.parsedArgs.dip_source_path == expected_source_path
        assert dlp.parsedArgs.dip_dest_path == expected_dest_path

def test_when_both_flag_args_source_positional_overridden():
    """
    Happy Path - all is given
    :return:
    """

    # Arrange
    expected_source_path: str = "expectedSourcePath"
    expected_overridden_source_path = "expected_overriden_source"
    expected_dest_path: str = "expectedDestPath"
    testargs = ["prog", "-i", "6666-666-666-4242",  "-t", expected_dest_path, "-s", expected_source_path, expected_overridden_source_path ]
    with patch.object(sys, 'argv', testargs):
        # Act
        dlp = DipLogParser("","")
        # Assert
        
        assert dlp.parsedArgs.source_path == expected_overridden_source_path
        assert dlp.parsedArgs.dip_source_path == expected_source_path
        assert dlp.parsedArgs.dip_dest_path == expected_dest_path

def test_when_both_flag_args_both_positionals_overridden():
    """
    Happy Path - all is given
    :return:
    """

    expected_source_path: str = "expectedSourcePath"
    expected_overridden_source_path = "expected_overridden_source"
    expected_dest_path: str = "expectedDestPath"
    expected_overridden_dest_path = "expected_overridden_dest"
    testargs = ["prog", "-i", "6666-666-666-4242",  "-t", expected_dest_path, "-s", expected_source_path, expected_overridden_source_path, expected_overridden_dest_path ]
    with patch.object(sys, 'argv', testargs):
        # Act
        dlp = DipLogParser("","")
        # Assert

        assert dlp.parsedArgs.source_path == expected_overridden_source_path
        assert dlp.parsedArgs.dip_source_path == expected_source_path
        assert dlp.parsedArgs.dest_path == expected_overridden_dest_path
        assert dlp.parsedArgs.dip_dest_path == expected_dest_path