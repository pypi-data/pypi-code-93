"""



"""

# Author: Ben Dudson, Department of Physics, University of York
#         benjamin.dudson@york.ac.uk
#
# This file is part of PyXPad.
#
# PyXPad is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyXPad is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

import os

from .pyxpad_utils import XPadDataItem, XPadDataDim

import importlib
import pathlib
from typing import Optional, Union, List, Tuple

# There are now (at least) three different names for the UDA/IDAM
# python wrappers. Try to import them, starting with the most recent
possible_idam_modules = ["pyuda", "pyidam", "idam"]
has_uda = False
idam = None

for idam_module in possible_idam_modules:
    try:
        idam = importlib.import_module(idam_module)
        has_uda = True
        break
    except ImportError:
        pass

if not has_uda:
    print("Warning: UDA/IDAM library not found. Cannot read data")


class XPadSource:
    def __init__(self):
        self.label = ""
        self.dimensions = {}
        self.varNames = []
        self.variables = {}

        self.parent = None

        self.config = {
            "Host": "mast.fusion.org.uk",
            "Port": 56565,
            "verbose": True,
            "debug": False,
        }

    @staticmethod
    def from_tree(path, parent=None):

        self = XPadSource()
        # Convert path to string, strip NULL chars
        path = pathlib.Path(path)

        self.label = os.path.basename(os.path.normpath(path))
        self.parent = parent

        # Define configuration dictionary
        if parent is not None:
            self.config = parent.config

        if os.path.isdir(path):
            return XPadSource.from_directory(self, path, parent)
        return XPadSource.from_IDL_file(self, path, parent)

    @staticmethod
    def from_directory(self, path: pathlib.Path, parent=None) -> "XPadSource":

        # List directory
        ls = os.listdir(path)

        # Check if a name is supplied
        if "title" in ls:
            # Read file to get the label
            with open(path / "title", "r") as f:
                self.label = f.readline().strip()

        # Create a child for each subdirectory which isn't hidden
        self.children = [
            XPadSource.from_tree(path / name, parent=self)
            for name in ls
            if os.path.isdir(path / name) and name[0] != "."
        ]

        # Find items
        for name in ls:
            if (path / name).is_file and (pathlib.Path(name).suffix == ".item"):
                self.children.append(XPadSource.from_tree(path / name, parent=self))
        return self

    @staticmethod
    def from_IDL_file(self, path: pathlib.Path, parent=None) -> "XPadSource":
        # Given an item file to read
        with open(path, "r") as f:
            self.label = f.readline().strip()  # First line is the label
            nitems = int((f.readline().split("$", 1))[0].strip())  # Number of items
            for i in range(nitems):
                line = f.readline()
                # Split at '$'
                s = line.split("$", 1)
                name = s[0].strip()
                if len(name) == 0:
                    continue
                desc = s[1].strip()
                item = XPadDataItem()
                item.name = name
                item.label = item.desc = desc
                item.source = path
                self.variables[name] = item
                self.varNames.append(name)

        if parent is not None:
            parent.addVariables(self.variables)
        return self

    @staticmethod
    def from_signals(shot: Union[int, str]):
        new_source = XPadSource()
        if shot == "":
            shot = new_source.last_shot_number
        new_source.label = str(shot)
        new_source.source = str(shot)
        names, descriptions = new_source._available_signals_and_descriptions(shot)
        for name, description in zip(names, descriptions):
            item = XPadDataItem()
            item.name = name
            item.label = item.desc = description
            item.source = shot
            new_source.variables[name] = item
            new_source.varNames.append(name)
        return new_source

    def addVariables(self, vardict):
        """Add to dictionary of variables and list of names"""
        for name, var in vardict.items():
            self.variables[name] = var
            self.varNames.append(name)

        if self.parent is not None:
            self.parent.addVariables(vardict)  # Variables go from children up to parent

    @property
    def client(self):
        """Start client if not already started"""
        if not has_uda:
            raise ImportError("No IDAM library available")
        # Start client
        if not hasattr(self, "_client"):
            # Set configuration
            idam.Client.server = self.config["Host"]
            idam.Client.port = self.config["Port"]
            self._client = idam.Client()
        return self._client

    def read(self, name, shot):
        """Read data from UDA/IDAM"""
        try:
            if isinstance(name, unicode):
                name = name.encode("utf-8")
        except NameError:
            pass
        name = str(name).strip()
        shot = str(shot).strip()

        # Read data
        data = self.client.get(name, shot)

        if hasattr(data, "dims") and not hasattr(data, "dim"):
            data.dim = data.dims

        # Give data a name
        try:
            data.name = name
            data.source = "Shot " + shot
        except AttributeError:
            # Probably IDAM has set something to be read-only property
            pass

        return XPadDataItem(data)

    def _available_signals_and_descriptions(
        self, shot: Optional[Union[int, str]] = None
    ) -> List[Tuple[str, str]]:
        if shot is None or shot == "":
            shot = self.last_shot_number
        signals = self.client.get(
            "meta::list(context=data, cast=column)", str(shot).strip()
        )
        return (signals["data"].signal_name, signals["data"].description)

    def available_signals(self, shot: Optional[Union[int, str]] = None) -> List[str]:
        """Get list of signals available for given shot"""
        return self._available_signals_and_descriptions(shot)[0]

    @property
    def last_shot_number(self):
        data_item = self.client.get("lastshot", "")
        return data_item.children[0].lastshot

    def size(self, name):
        pass

    def __getstate__(self):
        # We need to remove the IDAM client in order to pickle
        # instances of this class
        if hasattr(self, "client"):
            state = self.__dict__.copy()
            del state["client"]
            return state
        else:
            return self.__dict__
