#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" versionedmeta.py
A Meta Class that can compare the specified version of the classes.
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

# Downloaded Libraries #
from baseobjects import BaseMeta

# Local Libraries #
from ..version import Version


# Definitions #
# Classes #
class VersionedMeta(BaseMeta):
    """A Meta Class that can compare the specified version of the classes.

    Class Attributes:
        _VERSION_TYPE (:obj:`VersionType`): The type of version this object will be.
        VERSION (:obj:`Version`): The version of this class as a string.
    """
    _VERSION_TYPE = None
    VERSION = None

    # Magic Methods
    # Representation
    def __hash__(self):
        """Overrides hash to make the class hashable.

        Returns:
            The system ID of the class.
        """
        return id(self)

    # Comparison
    def __eq__(cls, other):
        """Expands on equals comparison to include comparing the version.

        Args:
            other (:obj:): The object to compare to this class.

        Returns:
            bool: True if the other object is equivalent to this class, including version.

        Raises:
            TypeError: If 'other' is a type that cannot be compared to.
        """
        if isinstance(other, type(cls)):
            if id(cls) == id(object):
                return True
            elif cls._VERSION_TYPE != other._VERSION_TYPE:
                return False
            other_version = other.VERSION
        elif isinstance(other, Version):
            other_version = other
        else:
            other_version = cls.VERSION.cast(other)

        if isinstance(other_version, type(cls.VERSION)):
            return cls.VERSION == other_version
        else:
            raise TypeError(f"'==' not supported between instances of '{str(cls)}' and '{str(other)}'")

    def __ne__(cls, other):
        """Expands on not equals comparison to include comparing the version.

        Args:
            other (:obj:): The object to compare to this class.

        Returns:
            bool: True if the other object is not equivalent to this class, including version number.

        Raises:
            TypeError: If 'other' is a type that cannot be compared to.
        """
        if isinstance(other, type(cls)):
            if cls._VERSION_TYPE != other._VERSION_TYPE:
                super().__ne__(other)
            other_version = other.VERSION
        elif isinstance(other, Version):
            other_version = other
        else:
            other_version = cls.VERSION.cast(other)

        if isinstance(other_version, type(cls.VERSION)):
            return cls.VERSION != other_version
        else:
            raise TypeError(f"'!=' not supported between instances of '{str(cls)}' and '{str(other)}'")

    def __lt__(cls, other):
        """Creates the less than comparison which compares the version of this class.

        Args:
            other (:obj:): The object to compare to this class.

        Returns:
            bool: True if the this object is less than to the other classes' version.

        Raises:
            TypeError: If 'other' is a type that cannot be compared to.
        """
        if isinstance(other, type(cls)):
            if cls._VERSION_TYPE != other._VERSION_TYPE:
                raise TypeError(f"'<' not supported between instances of '{str(cls)}' and '{str(other)}'")
            other_version = other.VERSION
        elif isinstance(other, Version):
            other_version = other
        else:
            other_version = cls.VERSION.cast(other)

        if isinstance(other_version, type(cls.VERSION)):
            return cls.VERSION < other_version
        else:
            raise TypeError(f"'<' not supported between instances of '{str(cls)}' and '{str(other)}'")

    def __gt__(cls, other):
        """Creates the greater than comparison which compares the version of this class.

        Args:
            other (:obj:): The object to compare to this class.

        Returns:
            bool: True if the this object is greater than to the other classes' version.

        Raises:
            TypeError: If 'other' is a type that cannot be compared to.
        """
        if isinstance(other, type(cls)):
            if cls._VERSION_TYPE != other._VERSION_TYPE:
                raise TypeError(f"'>' not supported between instances of '{str(cls)}' and '{str(other)}'")
            other_version = other.VERSION
        elif isinstance(other, Version):
            other_version = other
        else:
            other_version = cls.VERSION.cast(other)

        if isinstance(other_version, type(cls.VERSION)):
            return cls.VERSION > other_version
        else:
            raise TypeError(f"'>' not supported between instances of '{str(cls)}' and '{str(other)}'")

    def __le__(cls, other):
        """Creates the less than or equal to comparison which compares the version of this class.

        Args:
            other (:obj:): The object to compare to this class.

        Returns:
            bool: True if the this object is less than or equal to the other classes' version.

        Raises:
            TypeError: If 'other' is a type that cannot be compared to.
        """
        if isinstance(other, type(cls)):
            if cls._VERSION_TYPE != other._VERSION_TYPE:
                raise TypeError(f"'<=' not supported between instances of '{str(cls)}' and '{str(other)}'")
            other_version = other.VERSION
        elif isinstance(other, Version):
            other_version = other
        else:
            other_version = cls.VERSION.cast(other)

        if isinstance(other_version, type(cls.VERSION)):
            return cls.VERSION <= other_version
        else:
            raise TypeError(f"'<=' not supported between instances of '{str(cls)}' and '{str(other)}'")

    def __ge__(cls, other):
        """Creates the greater than or equal to comparison which compares the version of this class.

        Args:
            other (:obj:): The object to compare to this class.

        Returns:
            bool: True if the this object is greater than or equal to the other classes' version.

        Raises:
            TypeError: If 'other' is a type that cannot be compared to.
        """
        if isinstance(other, type(cls)):
            if cls._VERSION_TYPE != other._VERSION_TYPE:
                raise TypeError(f"'>=' not supported between instances of '{str(cls)}' and '{str(other)}'")
            other_version = other.VERSION
        elif isinstance(other, Version):
            other_version = other
        else:
            other_version = cls.VERSION.cast(other)

        if isinstance(other_version, type(cls.VERSION)):
            return cls.VERSION <= other_version
        else:
            raise TypeError(f"'>=' not supported between instances of '{str(cls)}' and '{str(other)}'")


