#!/usr/bin/env python3

from traceback import print_exc
from argparse import ArgumentParser
from dvk_archive.test.file.file_tests import test_all as file_test
from dvk_archive.test.error_finding.error_finding_tests import test_all as error_test
from dvk_archive.test.processing.processing_tests import test_all as pro_test
from dvk_archive.test.web.web_tests import test_all as web_test

def test_all():
    """
    Runs all unit tests for the dvk_archive program.
    """
    try:
        pro_test()
        file_test()
        error_test()
        web_test()
        print("\033[32mAll dvk_archive tests passed.\033[0m")
    except AssertionError:
        print("\033[31mCheck failed:\033[0m")
        print_exc()

def test_error_finding():
    """
    Runs unit tests related to finding errors in DVK files.
    """
    try:
        error_test()
        print("\033[32mAll error finding tests passed.\033[0m")
    except AssertionError:
        print("\033[31mCheck failed:\033[0m")
        print_exc()

def test_file():
    """
    Runs unit tests related to file input and output.
    """
    try:
        file_test()
        print("\033[32mAll file tests passed.\033[0m")
    except AssertionError:
        print("\033[31mCheck failed:\033[0m")
        print_exc()

def test_processing():
    """
    Runs unit tests related to internal processing.
    """
    try:
        pro_test()
        print("\033[32mAll processing tests passed.\033[0m")
    except AssertionError:
        print("\033[31mCheck failed:\033[0m")
        print_exc()

def test_web():
    """
    Runs unit tests related to web processes.
    """
    try:
        web_test()
        print("\033[32mAll web tests passed.\033[0m")
    except AssertionError:
        print("\033[31mCheck failed:\033[0m")
        print_exc()

def main():
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f",
        "--file",
        help="Runs tests for file handling modules.",
        action="store_true")
    group.add_argument(
        "-e",
        "--error",
        help="Runs tests for error finding modules.",
        action="store_true")
    group.add_argument(
        "-p",
        "--processing",
        help="Runs test for internal processing modules",
        action="store_true")
    group.add_argument(
        "-w",
        "--web",
        help="Runs test for web processes",
        action="store_true")
    args = parser.parse_args()
    if args.file:
        test_file()
    elif args.error:
        test_error_finding()
    elif args.processing:
        test_processing()
    elif args.web:
        test_web()
    else:
        test_all()

if __name__ == "__main__":
    main()
