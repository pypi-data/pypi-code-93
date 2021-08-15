#               Copyright (c) 2021 Zenqi.

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import os
import sys
import pathlib
from typing import List
from typing import Optional


class FileWatcher:
    """
    A simple lightweight FileMonitoring System based on
    `os.getmtime` or `os.get(modified)time`. This class
    cannot be used without the loop.

    Parameters:
    ---
        - path (str):
            The path to be watch. It can be file or directory

        - ignored_dirs (List[str]):
            The list of ignored directory.

    """

    __changes = {}

    added = []
    removed = []
    modified = []

    def __init__(self, path: str, ignored_dirs: Optional[List[str]] = []):

        self.path = path
        self.ignored_dirs = ignored_dirs
        self.__before = self.files_to_timestamp(self.path, self.ignored_dirs)

    @property
    def changes(self):
        return self.__changes

    def files_to_timestamp(self, path: str, ignored_dirs: Optional[List[str]] = []):

        path = pathlib.Path(path).absolute()
        files = []

        for i in ignored_dirs:
            ignored_dirs = [os.path.abspath(i)]

        if path.is_dir():
            for filepath in path.glob("**/*"):
                dirname = os.path.dirname(filepath.absolute())
                if os.path.basename(dirname) not in ignored_dirs:
                    files.append(str(filepath.absolute()))

                if not filepath.exists():
                    pass

        elif path.is_file():
            files.append(str(path.absolute()))

        try:
            file_timestamps = dict([(f, os.path.getmtime(f)) for f in files])
        except FileNotFoundError:
            file_timestamps = dict([(f, os.path.getmtime(f)) for f in files])

        return file_timestamps

    def watch(self):
        after = self.files_to_timestamp(self.path, self.ignored_dirs)
        for f in after.keys():
            if not f in self.__before.keys():
                self.added.append(f)
                self.__changes = {"added": f}

        for f in self.__before.keys():
            if not f in after.keys():
                self.removed.append(f)
                self.__changes = {"removed": f}

        for f in self.__before.keys():
            if not f in self.removed:
                if not os.path.exists(f):
                    self.removed.append(f)
                    self.__changes = {"removed": f}

                if os.path.getmtime(f) != self.__before.get(f):
                    self.modified.append(f)
                    self.__changes = {"modified": f}

        self.__before = after


class PythonWatcher(FileWatcher):
    """
    A Python watcher `:class:` for FileWatcher.
    It will automatically ignore `__pycache__` and only
    watch *.py files.
    """

    def __init__(self, path: str):
        self.path = path
        self.ignored_dirs = ["__pycache__"]
        for file in os.listdir(self.path):
            if os.path.isfile(file):
                if not file.endswith(".py"):
                    self.ignored_dirs.append(file)

        super(PythonWatcher, self).__init__(self.path, self.ignored_dirs)

    def watch(self):
        return super().watch()
