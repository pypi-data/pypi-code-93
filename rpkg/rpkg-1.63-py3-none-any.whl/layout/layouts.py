# Copyright (c) 2015 - Red Hat Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

"""package layout implementation"""


import os

from pyrpkg.errors import LayoutError

from .base import BaseLayout


class DistGitLayout(BaseLayout):
    """
    This class represents a dist-git package layout.
    """
    def __init__(self, root_dir=None, sources_file_template='sources'):
        """
        Default class constructor to create a new object instance.
        """
        self.root_dir = root_dir
        self.sourcedir = root_dir
        self.specdir = root_dir
        self.builddir = root_dir
        self.rpmdir = root_dir
        self.rpmfilename = '%%{ARCH}/%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm'
        self.srcrpmdir = root_dir
        self.sources_file_template = sources_file_template

    @classmethod
    def from_path(cls, path, hint=None):
        """
        Creates a new object instance from a valid path in the file system.

        Raises exception if path or package structure is invalid.
        """
        super(DistGitLayout, cls).from_path(path, hint)

        if len([f for f in os.listdir(path) if f.endswith('.spec')]) == 0:
            raise LayoutError('spec file not found.')
        if (hint == 'resultsdir'):
            raise LayoutError('resultsdir hint given')
        return cls(root_dir=path)


class DistGitResultsDirLayout(BaseLayout):
    """
    This class represents a dist-git package layout using results directory.
    """
    def __init__(self, root_dir=None, sources_file_template='sources'):
        """
        Default class constructor to create a new object instance.
        """
        results_dir = os.path.join(root_dir, 'results')

        self.root_dir = root_dir
        self.sourcedir = root_dir
        self.specdir = root_dir
        self.builddir = results_dir
        self.rpmdir = results_dir
        self.rpmfilename = '%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm'
        self.srcrpmdir = results_dir
        self.sources_file_template = sources_file_template

    @classmethod
    def from_path(cls, path, hint=None):
        """
        Creates a new object instance from a valid path in the file system.

        Raises exception if path or package structure is invalid.
        """
        super(DistGitResultsDirLayout, cls).from_path(path, hint)

        if len([f for f in os.listdir(path) if f.endswith('.spec')]) == 0:
            raise LayoutError('spec file not found.')
        if (hint != 'resultsdir'):
            raise LayoutError('resultsdir hint not given')
        return cls(root_dir=path)


class SRPMLayout(BaseLayout):
    """
    This class represents an exposed source RPM package layout.
    """
    def __init__(self, root_dir=None, sources_file_template='.{0.repo_name}.metadata'):
        """
        Default class constructor to create a new object instance.
        """
        self.root_dir = root_dir
        self.sourcedir = os.path.join(root_dir, 'SOURCES')
        self.specdir = os.path.join(root_dir, 'SPECS')
        self.builddir = os.path.join(root_dir, 'BUILD')
        self.rpmdir = os.path.join(root_dir, 'RPMS')
        self.rpmfilename = '%%{ARCH}/%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm'
        self.srcrpmdir = os.path.join(root_dir, 'SRPMS')
        self.sources_file_template = sources_file_template

    @classmethod
    def from_path(cls, path, hint=None):
        """
        Creates a new object instance from a valid path in the file system.

        Raises exception if path or package structure is invalid.
        """
        super(SRPMLayout, cls).from_path(path, hint)

        if not os.path.exists(os.path.join(path, 'SPECS')):
            raise LayoutError('SPECS dir not found.')
        if len([f for f in os.listdir(os.path.join(path, 'SPECS')) if f.endswith('.spec')]) == 0:
            raise LayoutError('spec file not found.')
        if len([f for f in os.listdir(path) if f.endswith('.metadata')]) == 0:
            raise LayoutError('metadata file not found.')
        return cls(root_dir=path)


class IncompleteLayout(BaseLayout):
    """
    This layout is possibly missing specfile(s) or some other essentials
    of previous layouts. Must not be retired yet. Just enough layout
    to allow run 'retire' command.
    """
    def __init__(self, root_dir=None, sources_file_template='sources'):
        """
        Default class constructor to create a new object instance.
        """
        self.root_dir = root_dir
        self.sources_file_template = sources_file_template

    @classmethod
    def from_path(cls, path, hint=None):
        """
        Creates a new object instance from a valid path in the file system.

        Raises exception if package is already retired.
        """
        super(IncompleteLayout, cls).from_path(path, hint)

        if cls(root_dir=path).is_retired():
            raise LayoutError('Retired marker found.')
        return cls(root_dir=path)


class RetiredLayout(BaseLayout):
    """
    This class represents situation that package or module is retired.
    Directory contains just a marker.
    """
    def __init__(self, root_dir=None):
        """
        Default class constructor to create a new object instance.
        """
        self.root_dir = root_dir

    @classmethod
    def from_path(cls, path, hint=None):
        """
        Creates a new object instance from a valid path in the file system.

        Raises exception if no marker is found.
        """
        super(RetiredLayout, cls).from_path(path, hint)

        if not cls(root_dir=path).is_retired():
            raise LayoutError('Retired marker not found.')
        return cls(root_dir=path)
