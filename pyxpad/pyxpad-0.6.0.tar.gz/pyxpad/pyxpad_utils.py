#
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

from numpy import sqrt, abs, all
from typing import Any


def get_attr_or_item(other: Any, name: str):
    """Wrap both getattr and __getitem__, but raise AttributeError on failure"""
    try:
        return getattr(other, name)
    except AttributeError:
        try:
            return other[name]
        except (TypeError, KeyError):
            raise AttributeError


class XPadDataDim:
    """
    Dimension of a data item

    name     Short name (e.g. "t")
    label    Short axis label (e.g. "Time (sec)")
    units    (e.g. "s")
    data     Axis values (NumPy array)
    errl     Low-side error (may be None)
    errh     High-side error (may be None)
    """

    def __init__(self, other=None):  # Constructor
        # Instance Variables
        self.name = ""
        self.label = ""
        self.units = ""
        self.data = None
        self.errl = None
        self.errh = None

        if other is not None:
            # List of variables to copy
            varlist = ["name", "label", "units", "data", "errl", "errh"]
            for name in varlist:
                # Check if other has this property
                try:
                    setattr(self, name, get_attr_or_item(other, name))
                except AttributeError:
                    pass

            if self.name == "":
                self.name = self.label

    def __str__(self):
        return self.name

    def __repr__(self):
        return (
            f"XPadDataDim({{'name':'{self.name}', 'label':'{self.label}', "
            f"'units':'{self.units}', 'data': {self.data}, "
            f"'errl': {self.errl}, 'errh': {self.errh}}})"
        )

    def __eq__(self, other):
        return (
            (self.name == other.name)
            and (self.units == other.units)
            and all(self.data == other.data)
        )


class XPadDataItem:
    """
    Data item class for PyXPad. Provides a standard interface
    and numerical operators

    name    The name used to request the data (e.g. "amc_plasma current")
    source  Source of the data as a string (e.g. "15100")
    label   Short description (e.g. "Plasma Current")
    units   Data units (e.g. "kA")
    desc    longer description (if set)
    data    NumPy array of the data
    errl    Low-side error (may be None)
    errh    High-side error (may be None)
    dim     A list of dimensions, each of which contains:
      - label  Short axis label (e.g. "Time (sec)")
      - units  (e.g. "s")
      - data   Axis values (NumPy array)
      - errl   Low-side error (may be None)
      - errh   High-side error (may be None)
    order   Index of time dimension
    time    A shortcut to the time data (dim[order].data). May be None

    """

    def __init__(self, other=None):  # Constructor
        # Instance Variables
        self.name = ""
        self.source = ""
        self.label = ""
        self.units = ""
        self.desc = ""
        self.data = None
        self.errl = None
        self.errh = None
        self.rank = None
        self.dim = [XPadDataDim()]
        self.order = -1
        self.time = None

        if other is None:
            return

        # Can we get either `other.data` or `other["data"]`?
        try:
            has_data = get_attr_or_item(other, "data") is not None
        except AttributeError:
            has_data = False

        # If we can't get a data member, assume it's a numerical type
        if not has_data:
            self.data = other
            self.name = str(other)
            return

        # List of variables to copy
        varlist = [
            "name",
            "source",
            "label",
            "units",
            "desc",
            "data",
            "rank",
            "errl",
            "errh",
            "order",
            "time",
        ]
        # Set any attributes we find on other
        for name in varlist:
            try:
                setattr(self, name, get_attr_or_item(other, name))
            except AttributeError:
                pass

        if self.name == "":
            self.name = self.label

        # Copy any dimensions other may have
        try:
            self.dim = [XPadDataDim(dim) for dim in get_attr_or_item(other, "dim")]
        except AttributeError:
            pass

    # def __coerce__(self, other):
    #    # Convert other to an XPadDataItem and return
    #    item = XPadDataItem

    def __str__(self):
        """
        Returns a summary of the data as a string
        """
        s = self.name + "(" + self.units + ")"

        if len(self.dim) > 0:
            s += " [" + ",".join([str(d) for d in self.dim]) + "]"

        return s

    def __repr__(self):
        return (
            f"XPadDataItem({{'name':'{self.name}', 'source':'{self.source}', "
            f"'label':'{self.label}', 'units':'{self.units}', 'desc':'{self.desc}'}})"
        )

    def __add__(self, other):  # +
        item = XPadDataItem(self)
        item += other
        return item

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):  # +=
        try:
            # Metadata
            self.name += " + " + other.name
            if (self.label != "") and (other.label != ""):
                self.label += " + " + other.label
            else:
                self.label = self.name

            # Dimensions
            if self.dim == other.dim:
                self.dim = other.dim
            else:
                raise ValueError(
                    "Incompatible dims: {} and {}".format(self.dim, other.dim)
                )

            # Low-side error
            if self.errl is not None and other.errl is not None:
                self.errl = sqrt(self.errl ** 2 + other.errl ** 2)
            elif other.errl is not None:
                self.errl = other.errl

            # High-side error
            if self.errh is not None and other.errh is not None:
                self.errh = sqrt(self.errh ** 2 + other.errh ** 2)
            elif other.errh is not None:
                self.errh = other.errh

            # Data
            self.data = self.data + other.data
        except AttributeError:
            # other probably just a numeric type
            self.name += " + " + str(other)
            if self.label != "":
                self.label += " + " + str(other)
            self.data = self.data + other

        return self

    def __sub__(self, other):  # -
        item = XPadDataItem(self)
        item -= other
        return item

    def __rsub__(self, other):  # -
        item = -(self - other)  # Lazy way
        item.name = f"{other} - {self.name}"
        if self.label:
            item.label = f"{other} - {self.label}"
        return item

    def __isub__(self, other):  # -=
        try:
            # Metadata
            self.name += " - " + other.name
            if (self.label != "") and (other.label != ""):
                self.label += " - " + other.label
            else:
                self.label = self.name

            # Dimensions
            if self.dim == other.dim:
                self.dim = other.dim
            else:
                raise ValueError(
                    "Incompatible dims: {} and {}".format(self.dim, other.dim)
                )

            # Low-side error. Note h and l swap for other
            if self.errl is not None and other.errh is not None:
                self.errl = sqrt(self.errl ** 2 + other.errh ** 2)
            elif other.errh is not None:
                self.errl = other.errh

            # High-side error
            if self.errh is not None and other.errl is not None:
                self.errh = sqrt(self.errh ** 2 + other.errl ** 2)
            elif other.errl is not None:
                self.errh = other.errl

            # Data
            self.data = self.data - other.data
        except AttributeError:
            self.name += " - " + str(other)
            if self.label != "":
                self.label += " - " + str(other)
            self.data = self.data - other
        return self

    def __mul__(self, other):  # *
        item = XPadDataItem(self)
        item *= other
        return item

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):  # *=
        try:
            # Metadata
            self.name += " * " + other.name
            if (self.label != "") and (other.label != ""):
                self.label += " * " + other.label
            else:
                self.label = self.name

            # Dimensions
            if self.dim == other.dim:
                self.dim = other.dim
            else:
                raise ValueError(
                    "Incompatible dims: {} and {}".format(self.dim, other.dim)
                )

            # Units
            if self.units == other.units:
                self.units += chr(0x00B2)
            else:
                self.units += other.units

            # Low-side error
            if self.errl is not None and other.errl is not None:
                self.errl = sqrt(
                    (other.data * self.errl) ** 2 + (self.data * other.errl) ** 2
                )
            elif other.errl is not None:
                self.errl = self.data * other.errl
            elif self.errl is not None:
                self.errl = other.data * self.errl

            # High-side error
            if self.errh is not None and other.errh is not None:
                self.errh = sqrt(
                    (other.data * self.errh) ** 2 + (self.data * other.errh) ** 2
                )
            elif other.errh is not None:
                self.errh = self.data * other.errh
            elif self.errh is not None:
                self.errh = other.data * self.errh

            # Data
            self.data = self.data * other.data
        except AttributeError:
            self.name = "( " + self.name + " * " + str(other) + " )"
            if self.label != "":
                self.label = "( " + self.label + " * " + str(other) + " )"
            self.data = self.data * other
            if self.errl is not None:
                self.errl = self.errl * other
            if self.errh is not None:
                self.errh = self.errh * other
        return self

    def __truediv__(self, other):  # /
        item = XPadDataItem(self)
        item /= other
        return item

    def __itruediv__(self, other):  # /=
        try:
            # Metadata
            self.name += " / " + other.name
            if (self.label != "") and (other.label != ""):
                self.label += " / " + other.label
            else:
                self.label = self.name

            # Dimensions
            if self.dim == other.dim:
                self.dim = other.dim
            else:
                raise ValueError(
                    "Incompatible dims: {} and {}".format(self.dim, other.dim)
                )

            # Units
            if self.units == other.units:
                self.units = ""
            elif self.units == "":
                self.units = other.units + chr(0x207B) + chr(0x00B9)
            else:
                self.units += "/" + other.units

            # Low-side error. Note h and l swap for other
            if self.errl is not None and other.errh is not None:
                self.errl = sqrt(
                    (self.errl / other.data) ** 2
                    + (self.data * other.errh / other.data ** 2) ** 2
                )
            elif other.errh is not None:
                self.errl = self.data * other.errh / other.data ** 2
            elif self.errl is not None:
                self.errl = self.errl / other.data

            # High-side error
            if self.errh is not None and other.errl is not None:
                self.errh = sqrt(
                    (self.errh / other.data) ** 2
                    + (self.data * other.errl / other.data ** 2) ** 2
                )
            elif other.errl is not None:
                self.errh = self.data * other.errl / other.data ** 2
            elif self.errh is not None:
                self.errh = self.errh / other.data

            # Data
            self.data = self.data / other.data
        except AttributeError:
            self.name = "( " + self.name + " / " + str(other) + " )"
            if self.label != "":
                self.label = "( " + self.label + " / " + str(other) + " )"
            self.data = self.data / other
            if self.errl is not None:
                self.errl = self.errl / other
            if self.errh is not None:
                self.errh = self.errh / other
        return self

    def __rtruediv__(self, other):  #
        item = XPadDataItem(other)
        # Check to see if the temporary's dimensions are still the default: this
        # implies `other` didn't have any dimensions to copy. We're going to hit
        # an "incompatible dimensions" exception, so let's copy the dimensions
        # from self -- we might not be able to actually do the division if the
        # array sizes won't broadcast, but we will be able to do e.g. 1./self
        if item.dim == XPadDataItem().dim:
            item.dim = self.dim
        item /= self
        return item

    def __neg__(self):  # Unary minus
        item = XPadDataItem(self)
        item.name = "-" + self.name
        if self.label != "":
            item.label = "-" + self.label

        item.data = -self.data
        # Swap high and low errors
        item.errl = self.errh
        item.errh = self.errl

        return item

    def __pos__(self):
        return self

    def __abs__(self):
        item = XPadDataItem(self)
        item.name = f"abs({self.name})"
        if self.label != "":
            item.label = f"abs({self.label})"

        item.data = abs(self.data)
        # High side error is maximum of low and high
        if self.errl is not None and self.errh is not None:
            pass
        if self.errl is not None:
            item.errh = self.errl

        # Low side error is zero
        item.errl = 0.0

        return item


def chop(item):
    """
    Selects a range of indices

    """
    pass
