# Copyright (c) 2015 - Red Hat Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

"""base and meta package layout classes"""


import abc
import os
from abc import ABCMeta, abstractmethod

import six

from pyrpkg.errors import LayoutError

if six.PY2:
    ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})
else:
    ABC = abc.ABC


class MetaLayout(type):
    """
    Layout meta class that keeps track of all layout subclasses.

    Classes are appended in the _layouts property in order of code execution.
    """
    def __init__(cls, name, bases, dct):
        """
        This method registers a subclass in a class property (_layouts)
        so those can be used as valid layout classes.
        """
        if not hasattr(cls, '_layouts'):
            MetaLayout._layouts = []
        if cls not in cls._layouts and cls.__name__ != 'BaseLayout':
            MetaLayout._layouts.append(cls)
        super(MetaLayout, cls).__init__(name, bases, dct)


class ABCMetaLayout(MetaLayout, ABCMeta):
    """
    A mixin metaclass to enable usage of both Metalayout and ABC meta classes as a single metaclass.
    """
    pass


@six.add_metaclass(ABCMetaLayout)
class BaseLayout(ABC):
    """
    The abstract class to be inherited from when implemeting specific layouts.

    Every subclass will be registered in the MetaLayout class.

    Inherited classes will be registered in order or code execution.
    """
    root_dir = None
    sourcedir = None
    specdir = None
    builddir = None
    rpmdir = None
    rpmfilename = None
    srcrpmdir = None
    sources_file_template = None

    @classmethod
    @abstractmethod
    def from_path(cls, path, hint=None):
        """
        Class constructor based on a package path.

        This method's implementation is mandatory and
        should return an instance of the object class.

        It should raise an exception if it can't read the path
        or if the dir path contains an invalid layout.
        """
        if not os.path.exists(path):
            raise LayoutError('package path does not exist')

    def is_retired(self):
        """
        Checks whether package or module is already retired.
        The state is indicated by present of files 'dead.package'
        or 'dead.module'.
        """
        for fname in ['dead.package', 'dead.module']:
            if os.path.exists('%s/%s' % (self.root_dir, fname)):
                return fname
        return None
