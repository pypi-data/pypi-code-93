"""Common enum functionality."""

import typing as t
from enum import Enum


class ExtendedEnum(str, Enum):
    """ExtendedEnum.

    Enums with an easy way of querying all members.
    """

    @classmethod
    def set(cls) -> t.Set[str]:
        """set.

        Parameters
        ----------

        Returns
        -------
        t.Set[str]
            A set of all values.

        """
        return {c.value for c in cls}

    @classmethod
    def list(cls) -> t.List[str]:
        """list.

        Parameters
        ----------

        Returns
        -------
        t.List[str]
            A list of all values.

        """
        return [c.value for c in cls]

    @classmethod
    def names(cls) -> t.List[str]:
        """names.

        Parameters
        ----------

        Returns
        -------
        t.List[str]
            A list of all enum names.

        """
        return [c.name for c in cls]
