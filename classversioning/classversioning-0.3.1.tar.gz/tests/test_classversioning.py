#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" test_xltekobjects.py
Description:
"""
__author__ = "Anthony Fong"
__copyright__ = "Copyright 2021, Anthony Fong"
__credits__ = ["Anthony Fong"]
__license__ = ""
__version__ = "0.3.1"
__maintainer__ = "Anthony Fong"
__email__ = ""
__status__ = "Prototype"

# Default Libraries #
import datetime
import pathlib

# Downloaded Libraries #
import pytest

# Local Libraries #
from src.classversioning import *


# Definitions #
# Functions #
@pytest.fixture
def tmp_dir(tmpdir):
    """A pytest fixture that turn the tmpdir into a Path object."""
    return pathlib.Path(tmpdir)


# Classes #
class ClassTest:
    """Default class tests that all classes should pass."""
    class_ = None
    timeit_runs = 100
    speed_tolerance = 200

    def get_log_lines(self, tmp_dir, logger_name):
        path = tmp_dir.joinpath(f"{logger_name}.log")
        with path.open() as f_object:
            lines = f_object.readlines()
        return lines


class TestVersionedClass(ClassTest):
    # Example
    # Define Classes with Versions
    class ExampleVersioning(VersionedClass):
        """A Version Class that establishes the type of class versioning the child classes will use."""
        _VERSION_TYPE = VersionType(name="Example", class_=TriNumberVersion)  # Remember if you want to use multiple
        # versioned classes that they should have
        # different names.

        @staticmethod
        def get_version_from_object(obj):
            return obj["version"]

        # Automatic Version Instantiation
        def __new__(cls, *args, **kwargs):
            if cls == TestVersionedClass.ExampleVersioning:
                if args:
                    obj = args[0]
                else:
                    obj = kwargs["obj"]
                class_ = cls.get_version_class(obj)
                return class_(*args, **kwargs)
            else:
                return super(TestVersionedClass.ExampleVersioning, cls).__new__(cls)

    class Example1_0_0(ExampleVersioning):
        """This class is the first of Examples version 1.0.0 which implements some adding"""
        VERSION = TriNumberVersion(1, 0, 0)  # Version can be defined through version object

        def __init__(self, *args, **kwargs):
            self.a = 1
            self.b = 2

        def add(self, x):
            self.a = self.a + x

    class Example1_1_0(Example1_0_0):
        """This class inherits from 1.0.0 but changes how the adding is done"""
        VERSION = "1.1.0"  # Version can be defined through str as long as there is a method to derive the Version

        def add(self, x):
            self.b = self.b + x

    class Example2_0_0(ExampleVersioning):
        """Rather than inherit from previous version, this class reimplements the whole class."""
        VERSION = (2, 0, 0)

        def __init__(self,  *args, **kwargs):
            self.a = 1
            self.c = 3

        def multiply(self, x):
            self.a = self.a * x

    def test_versioning(self):
        # Using Example Classes
        # Data
        dataset1 = {"version": "1.0.0", "number": 1}
        dataset2 = {"version": (1, 2, 0), "number": 2}
        dataset3 = {"version": TriNumberVersion(2, 0, 0, ver_name="Example"), "number": 3}

        datasets = [dataset1, dataset2, dataset3]

        # Example: Getting version
        example1 = self.ExampleVersioning.get_version_class(dataset1["version"])
        example2 = self.ExampleVersioning.get_version_class(dataset2["version"], type_="Example")
        example3 = self.ExampleVersioning.get_version_class(dataset3["version"], exact=True, sort=True)

        # Example: Operating on a list of versioned datasets
        for d in datasets:
            example_class = self.ExampleVersioning.get_version_class(d["version"])  # Get Example class based on version
            example_object = example_class()  # Initiate Example object
            if example_class < "2.0.0":  # If the version is less than 2.0.0, add
                example_object.add(d["number"])
                print(example_object.a)
                print(example_object.b)
            else:
                example_object.multiply(d["number"])
                print(example_object.a)

    def test_auto_versioning(self):
        # Data
        dataset1 = {"version": "1.0.0", "number": 1}
        dataset2 = {"version": (1, 2, 0), "number": 2}
        dataset3 = {"version": TriNumberVersion(2, 0, 0, ver_name="Example"), "number": 3}

        test = self.ExampleVersioning(dataset1)




# Main #
if __name__ == '__main__':
    pytest.main(["-v", "-s"])
