# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class Dependency(object):
    """This class represents a dependency of a component."""

    def __init__(self, cls):
        """
        Parameters
        ----------
        cls : type
            The class which serves as dependency.
        """
        self._cls = cls

    @property
    def cls(self):
        """
        Retrieve the component (class) which was marked as a dependency.

        Returns
        -------
        dependency_class : type
        """
        return self._cls
