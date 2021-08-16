#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" version.py
Version is an abstract class which versions of different types can be defined from.
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
from abc import abstractmethod

# Downloaded Libraries #
from baseobjects import BaseObject

# Local Libraries #
from .versiontype import VersionType


# Definitions #
# Classes #
class Version(BaseObject):
    """An abstract class for creating versions which dataclass like classes that stores and handles a versioning.

    Class Attributes:
        default_version_name (str): The name of the version.

    Attributes:
        version_type (:obj:`VersionType`): The type of version object this object is.

    Args:
        obj (:obj:, optional): An object to derive a version from.
        ver_name (str, optional): The name of the version type being used.
        init (bool, optional): Determines if the object should be initialized.
    """
    default_version_name = "default"

    # Class Methods
    @classmethod
    def cast(cls, other, pass_=False):
        """A cast method that optionally returns the original object rather than raise an error

        Args:
            other (:obj:): An object to convert to this type.
            pass_ (bool, optional): True to return original object rather than raise an error.

        Returns:
            obj: The converted object of this type or the original object.
        """
        try:
            other = cls(other)
        except TypeError as e:
            if not pass_:
                raise e

        return other

    @classmethod
    def create_version_type(cls, name=None):
        """Create the version type of this version class.

        Args:
            name (str): The which this type will referred to.

        Returns:
            :obj:`VersionType`: The version type of this version.
        """
        if name is None:
            name = cls.default_version_name
        return VersionType(name, cls)

    # Matic Methods
    # Construction/Destruction
    @abstractmethod
    def __init__(self, obj=None, ver_name=None, init=True, **kwargs):
        self.version_type = None

        if init:
            self.construct(obj=obj, ver_name=ver_name)

    # Representation
    def __hash__(self):
        """Overrides hash to make the object hashable.

        Returns:
            The system ID of the object.
        """
        return id(self)

    # Type Conversion
    @abstractmethod
    def __str__(self):
        """Returns the str representation of the version.

        Returns:
            str: A str with the version numbers in order.
        """
        return super().__str__()

    # Comparison
    @abstractmethod
    def __eq__(self, other):
        """Expands on equals comparison to include comparing the version number.

        Args:
            other (:obj:): The object to compare to this object.

        Returns:
            bool: True if the other object or version number is equivalent.
        """
        return super().__ne__(other)

    @abstractmethod
    def __ne__(self, other):
        """Expands on not equals comparison to include comparing the version number.

        Args:
            other (:obj:): The object to compare to this object.

        Returns:
            bool: True if the other object or version number is not equivalent.
        """
        return super().__ne__(other)

    @abstractmethod
    def __lt__(self, other):
        """Creates the less than comparison for these objects which includes str, list, and tuple.

        Args:
            other (:obj:): The object to compare to this object.

        Returns:
            bool: True if this object is less than to the other objects' version number.

        Raises:
            TypeError: If 'other' is a type that cannot be compared to.
        """
        other = self.cast(other, pass_=True)

        if isinstance(other, Version):
            return self.tuple() < other.tuple()
        else:
            raise TypeError(f"'>' not supported between instances of '{str(self)}' and '{str(other)}'")

    @abstractmethod
    def __gt__(self, other):
        """Creates the greater than comparison for these objects which includes str, list, and tuple.

        Args:
            other (:obj:): The object to compare to this object.

        Returns:
            bool: True if this object is greater than to the other objects' version number.

        Raises:
            TypeError: If 'other' is a type that cannot be compared to.
        """
        other = self.cast(other, pass_=True)

        if isinstance(other, Version):
            return self.tuple() > other.tuple()
        else:
            raise TypeError(f"'>' not supported between instances of '{str(self)}' and '{str(other)}'")

    @abstractmethod
    def __le__(self, other):
        """Creates the less than or equal to comparison for these objects which includes str, list, and tuple.

        Args:
            other (:obj:): The object to compare to this object.

        Returns:
            bool: True if this object is less than or equal to to the other objects' version number.

        Raises:
            TypeError: If 'other' is a type that cannot be compared to.
        """
        other = self.cast(other, pass_=True)

        if isinstance(other, Version):
            return self.tuple() <= other.tuple()
        else:
            raise TypeError(f"'<=' not supported between instances of '{str(self)}' and '{str(other)}'")

    @abstractmethod
    def __ge__(self, other):
        """Creates the greater than or equal to comparison for these objects which includes str, list, and tuple.

        Args:
            other (:obj:): The object to compare to this object.

        Returns:
            bool: True if this object is greater than or equal to to the other objects' version number.

        Raises:
            TypeError: If 'other' is a type that cannot be compared to.
        """
        other = self.cast(other, pass_=True)

        if isinstance(other, Version):
            return self.tuple() >= other.tuple()
        else:
            raise TypeError(f"'>=' not supported between instances of '{str(self)}' and '{str(other)}'")

    # Instance Methods
    # Constructors/Destructors
    @abstractmethod
    def construct(self, obj=None, ver_name=None):
        """Constructs the version object based on inputs

        Args:
            obj (:obj:, optional): An object to derive a version from.
            ver_name (str, optional): The name of the version type being used.
        """
        self.version_type = self.create_version_type(ver_name)

    # Type Conversion
    @abstractmethod
    def list(self):
        """Returns the list representation of the version.

        Returns:
            :obj:`list` of :obj:`str`: The list representation of the version.
        """
        pass

    @abstractmethod
    def tuple(self):
        """Returns the tuple representation of the version.

        Returns:
            :obj:`tuple` of :obj:`str`: The tuple representation of the version.
        """
        pass

    def str(self):
        """Returns the str representation of the version.

        Returns:
            str: A str with the version numbers in order.
        """
        return str(self)

    # Typing
    def set_version_type(self, name):
        """Creates a new VersionType for this object.

        Args:
            name (str): The name of the new VersionType.
        """
        self.version_type = VersionType(name, type(self))
