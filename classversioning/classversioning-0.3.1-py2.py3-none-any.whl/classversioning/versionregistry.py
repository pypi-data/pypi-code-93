#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" versionregistry.py
VersionRegistry creates registries of the Versions which keep track of several versioning schemas. For example, there
could be two different file types that both use TriNumberVersions, this registry keeps the class versions from these
different files separate from each other.
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
import bisect
from collections import UserDict

# Downloaded Libraries #

# Local Libraries #
from .version import VersionType


# Definitions #
# Classes #
class VersionRegistry(UserDict):
    """A dictionary like class that holds versioned objects.

    The keys distinguish different types of objects from one another, so their version are not mixed together. The items
    are lists containing the versioned objects in order by version.
    """

    # Instance Methods
    def get_version(self, type_, key, exact=False):
        """Gets an object from the registry base on the type and version of object.

        Args:
            type_ (str): The type of versioned object to get.
            key (str, list, tuple, :obj:`Version`): The key to search for the versioned object with.
            exact (bool, optional): Determines whether the exact version is need or return the closest version.
        Returns
            obj: The versioned object.

        Raises
            ValueError: If there is no closest version.
        """
        if isinstance(type_, VersionType):
            type_ = type_.name

        versions = self.data[type_]["list"]
        if isinstance(key, str) or isinstance(key, list) or isinstance(key, tuple):
            version_class = self.data[type_]["type"].class_
            key = version_class.cast(key)

        if exact:
            index = versions.index(key)
        else:
            index = bisect.bisect(versions, key)

        if index < 0:
            raise ValueError(f"Version needs to be greater than {str(versions[0])}, {str(key)} is not.")
        else:
            return versions[index-1]

    def get_version_type(self, name):
        """Gets the type object being used as a key.

        Args:
            name (str): The name of the type object.

        Returns:
            :obj:`VersionType`: The type object requested.
        """
        return self.data[name]["type"]

    def add_item(self, item, type_=None):
        """Adds a versioned item into the registry.

        Args
            type_ (str): The type of versioned object to add.
            item (:obj:`Version`): The versioned object to add.
        """
        if isinstance(type_, str):
            name = type_
            type_ = self.data[name]["type"]
        else:
            if type_ is None:
                type_ = item.version_type
            name = type_.name

        if name in self.data:
            bisect.insort(self.data[name]["list"], item)
        else:
            self.data[name] = {"type": type_, "list": [item]}

    def sort(self, type_=None, **kwargs):
        """Sorts the registry.

        Args:
            type_ (str, optional): The type of versioned object to add.
            **kwargs: Args that are passed to the list sort function.
        """
        if type_ is None:
            for versions in self.data.values():
                versions["list"].sort(**kwargs)
        else:
            if isinstance(type_, VersionType):
                type_ = type_.name
            self.data[type_]["list"].sort(**kwargs)
