#!/usr/bin/env python
# pylint: disable=no-value-for-parameter
# -*- coding: utf-8 -*-
"""path_tools.py

Concentrate path and file manipulaiton tools.  Any
OpenTEA class needing these tools should inherit it.

Created Nov 2016 by COOP team
"""

from __future__ import absolute_import

import os
import shutil
import logging
import errno
import glob

from os.path import (abspath, basename, isabs, isfile, normpath,
                     realpath, isdir, join, relpath, samefile)

__all__ = ["PathTools"]


class PathTools:
    """Concentrate path manipulation tools"""
    def __init__(self, base_dir=None, **kwargs):
        self.base_dir = os.getcwd() if base_dir is None else base_dir
        self.rel_dir = self.base_dir
        self.log = logging.getLogger(__name__)
        self.log.debug("Instance of PathTools created")
        self.log.debug("    base_dir: " + self.base_dir)
        self.log.debug("    rel_dir : " + self.rel_dir)
        self.__dict__.update(**kwargs)

    def abspath(self, *args):
        """Get path as clean absolute

        If args starts with absolute path, just abspath it.  Else, consider
        from self.base_dir, then abspath.  Note: os.path.abspath also performs
        normpath, which "cleans" any ../ and such.
        """
        interpret_path_from = (join(*args) if isabs(args[0]) else
                               join(self.base_dir, *args))
        return normpath(realpath(abspath(interpret_path_from)))

    def relpath(self, *args):
        """Get path as clean relative from base_dir"""
        return './' + normpath(relpath(realpath(self.abspath(*args)),
                                       self.rel_dir))

    def _file_checks(self, src, dest):
        """Generic checks before moving or copying src to dest

        - If dest is a folder, src file name is kept. Otherwise, given file
          name is used.
        - If source and dest are the same file, no error is raised but a
          warning is printed.

        Return go_code (True: continue. False: skip) and destination
        """
        dest = self.abspath(dest)
        if isdir(dest):
            dest = join(dest, basename(src))

        if isfile(src) and isfile(dest) and samefile(src, dest):
            # shutil.copy doesn't like same files
            self.log.warning(
                "No copy for the same file: {0} and {1}".format(src, dest))
            return False, dest

        return True, dest

    def copy_file(self, src, dest):
        """Copy file src to dest"""
        copy_is_ok, dest = self._file_checks(src, dest)
        if copy_is_ok:
            self.log.debug("Copying {0} to {1}".format(src, dest))
            shutil.copy(src, dest)
        return dest

    def move_file(self, src, dest):
        """Move file src to dest"""
        move_is_ok, dest = self._file_checks(src, dest)
        if move_is_ok:
            self.log.debug("Moving {0} to {1}".format(src, dest))
            if isfile(dest):
                os.remove(dest)
            shutil.move(src, dest)
        return dest

    def copy_dir(self, src, dest):
        """Copy dir src to dest
        - If dest ends with /, src dir is copied in dest dir.  Otherwise, src
          dir is copied *as* dest dir.  This mirrors the `cp` command behavior.
        - If dest is a regular file, raise an error.
        - If source and dest are the same dir, no error is raised but a warning
          is printed.
        """
        if dest[-1] == '/':
            dest = join(dest, basename(src))

        dest = self.abspath(dest)
        if isfile(dest):
            self.log.error("Trying to create/populate directory {0}, but it "
                           "is already a regular file".format(dest))
            raise OSError(errno.EEXIST)

        # shutil.copy doesn't like same files
        if isdir(src) and isdir(dest) and samefile(src, dest):
            self.log.warning("No copy for the same file: {0} and {1}".
                             format(src, dest))
            return

        if not isdir(dest):
            os.mkdir(dest)

        self.log.debug("Copying {0} to {1}".format(src, dest))
        for path in os.listdir(src):
            if isdir(path):
                self.copy_dir(join(src, path), join(dest, path))
            else:
                self.copy_file(join(src, path), dest)

    def ensure_dir(self, directory):
        """Ensure that directory exists"""
        new_dir = self.abspath(directory)
        self.log.debug("Ensuring existence of " + new_dir)
        if not isdir(new_dir):
            os.mkdir(new_dir)
        return new_dir

    def get_file_list(self, path, filter_search="", output="listonly"):
        """ return the list of files in a path (compulsory)
        matching a filter string (facultative).
        output (facultative) can be : - listonly : a list of the files
                                      - relative : a list relative pathes
                                      - absolute : a list of absolute path
        """
        lresult = []
        glob_arg = os.path.join(path, filter_search)
        list_dir = glob.glob(glob_arg)

        if output == "relative":
            for file_name in list_dir:
                lresult.append(os.path.relpath(file_name))
        if output == "listonly":
            for file_name in list_dir:
                lresult.append(os.path.relpath(file_name, path))
        if output == "absolute":
            lresult = list_dir

        lresult = sorted(lresult)
        self.log.debug("Looking for files " + filter_search + "in " + path)
        self.log.debug(".. List of files :" + str(lresult))

        return lresult