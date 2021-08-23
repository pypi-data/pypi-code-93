"""
Functions which can be used to manipulate data items

Available to the user in the command terminal

"""

from Qt.QtWidgets import (
    QDialog,
    QGridLayout,
    QDialogButtonBox,
    QPushButton,
    QInputDialog,
)

import numpy as np
from pyxpad import calculus
from .pyxpad_utils import XPadDataItem, XPadDataDim


def XPadFunction(func, name="f"):
    """
    Turns a NumPy function into a function of data item
    """

    def newfunc(data):
        result = XPadDataItem()
        if data.name != "":
            result.name = f"{name}({data.name})"
        result.source = data.source
        if data.label != "":
            result.label = f"{name}({data.label})"
        result.data = func(data.data)
        result.dim = data.dim
        result.order = data.order
        result.time = data.time
        return result

    return newfunc


sin = XPadFunction(np.sin, "sin")
cos = XPadFunction(np.cos, "cos")
tan = XPadFunction(np.tan, "tan")

arcsin = XPadFunction(np.arcsin, "arcsin")
arccos = XPadFunction(np.arccos, "arccos")
arctan = XPadFunction(np.arctan, "arctan")

exp = XPadFunction(np.exp, "exp")
log = XPadFunction(np.log, "log")

exponential = XPadFunction(np.exp, "exp")
nlog = XPadFunction(np.log, "nlog")

sqrt = XPadFunction(np.sqrt, "sqrt")
absolute = XPadFunction(np.absolute, "abs")


def reciprocal(data):
    """Multiplicative inverse. Modifies units"""
    recip = XPadFunction(np.reciprocal, "recip")
    reciprocal = recip(data)
    reciprocal.units = data.units + chr(0x207B) + chr(0x00B9)
    return reciprocal


def normalise(data):
    point = len(data.data) - 1
    integral = calculus.integrate(data)
    normfac = integral.data[point]
    normdat = np.true_divide(data.data, normfac)
    result = XPadDataItem(integral)
    result.data[:] = normdat[:]
    if data.name != "":
        result.name = "Norm(" + data.name + ")"
    if data.label != "":
        result.label = "Norm(" + data.label + ")"
    result.units = data.units
    return result


def invert(data):
    """Additive inverse"""
    return -data


def addcon(data):
    """Add a constant, taken from user input"""
    parent = QDialog()
    constant, ok = QInputDialog.getDouble(parent, "X+C", "Input constant:")
    if not ok:
        raise RuntimeError("User cancelled input")
    return data + constant


def subcon(data):
    """Subtract a constant, taken from user input"""
    parent = QDialog()
    constant, ok = QInputDialog.getDouble(parent, "X-C", "Input constant:")
    if not ok:
        raise RuntimeError("User cancelled input")
    return data - constant


def mulcon(data):
    """Multiply by a constant, taken from user input"""
    parent = QDialog()
    constant, ok = QInputDialog.getDouble(parent, "X*C", "Input constant:")
    if not ok:
        raise RuntimeError("User cancelled input")
    return data * constant


def divcon(data):
    """Divide by a constant, taken from user input"""
    parent = QDialog()
    constant, ok = QInputDialog.getDouble(parent, "X/C", "Input constant:")
    if not ok:
        raise RuntimeError("User cancelled input")
    return data / constant


def powcon(data):
    """Exponentiate by a constant, taken from user input"""
    result = XPadDataItem(data)
    parent = QDialog()
    constant, ok = QInputDialog.getDouble(parent, "X^C", "Input constant:")
    if not ok:
        raise RuntimeError("User cancelled input")
    result.data = np.power(data.data, constant)
    result.name = f"({data.name})^{constant}"
    result.label = f"({data.label})^{constant}"
    result.units = f"({data.units})^{constant}"
    return result


def inputname():
    parent = QDialog()
    title = "Change Name"
    label = "Enter new name:"
    dialog = QInputDialog.getText(parent, title, label)
    if dialog[1]:
        name = dialog[0]
    return name


def changename(data):
    result = XPadDataItem(data)
    result.name = "Renamed(" + data.name + ")"
    return result


def changeunits(data):
    result = XPadDataItem(data)
    parent = QDialog()
    title = "Change Units"
    label = "Enter new units:"
    new_unit, ok = QInputDialog.getText(parent, title, label)
    if not ok:
        raise RuntimeError("User cancelled input")
    unit_factor = getUnitFactor()
    if unit_factor and new_unit:
        result.data = np.multiply(data.data, unit_factor)
        result.units = new_unit
        return result


def getUnitFactor():
    parent = QDialog()
    title = "Change Units"
    label = "Enter conversion factor:"
    factor, ok = QInputDialog.getDouble(parent, title, label)
    if not ok:
        raise RuntimeError("User cancelled input")
    return factor


def statistics(data):
    stats = f"""\nStatistics on {data.name}:
    Mean = {np.mean(data.data)}
    Standard Deviation = {np.std(data.data)}
    Range = ({np.min(data.data)}) - ({np.max(data.data)})
    """
    print(stats)


def timeOffset(data):
    result = XPadDataItem(data)
    parent = QDialog()
    offset, ok = QInputDialog.getDouble(parent, "Time Offset", "Input time offest:")
    if not ok:
        raise RuntimeError("User cancelled input")
    result.dim[data.order].data = np.add(result.dim[data.order].data, offset)
    result.name = f"Timoff({result.name}, {offset})"
    result.label = f"Timoff({result.label}, {offset})"
    return result


def chop(item, t_min, t_max):
    """
    >>> from user_functions import *
    >>> a = chop(XMC_OMV_110, 0.274, 0.276)
    >>> a_amp,a_phase = fftp(a)
    >>> b = chop(a_phase, 0.0, 100.0)
    >>> plot(b)
    """
    if len(item.dim) != 1:
        raise ValueError("chop can only operate on 1D traces currently")

    if t_max < t_min or t_max < item.dim[0].data[0] or t_min > item.dim[0].data[-1]:
        raise ValueError("New time-range not defined correctly")

    idx = np.where(np.logical_and(item.dim[0].data >= t_min, item.dim[0].data <= t_max))

    if len(idx[0]) == 0:
        raise ValueError("No data in time-range specified")

    # Calculate the phase
    chopped = XPadDataItem()

    if item.name != "":
        chopped.name = (
            "CHOP( " + item.name + ", " + str(t_min) + ", " + str(t_max) + " )"
        )
    chopped.source = item.source
    if item.label != "":
        chopped.label = (
            "CHOP( " + item.label + ", " + str(t_min) + ", " + str(t_max) + " )"
        )
    chopped.units = item.units

    chopped.data = item.data[idx]

    # Create a dimension
    dim = XPadDataDim()

    dim.name = item.dim[0].name
    dim.label = item.dim[0].label
    dim.units = item.dim[0].units

    dim.data = item.dim[0].data[idx]
    chopped.dim = [dim]

    if chopped.dim[0].units in ["s", "S", "sec", "Sec", "SEC"]:
        chopped.order = 0
        chopped.time = chopped.dim[0].data

    return chopped


def clip(item, valmin, valmax):
    """
    Removes values outside a given range
    """

    if len(item.dim) != 1:
        raise ValueError("Clip can only operate on 1D traces currently")

    if valmax < valmin:
        raise ValueError("Clip range incorrectly defined")

    clipped = XPadDataItem(item)
    data = []
    time = []

    for point in range(len(item.data) - 1):
        if item.data[point] <= valmax and item.data[point] >= valmin:
            data += [item.data[point]]
            time += [item.dim[item.order].data[point]]

    if len(data) == 0:
        raise ValueError("No data in the specified range")

    clipped.data = data
    clipped.dim[clipped.order].data = time
    clipped.time = time
    clipped.name = "CLIP(" + item.name + ", " + str(valmin) + ", " + str(valmax) + ")"
    clipped.label = "CLIP(" + item.label + ", " + str(valmin) + ", " + str(valmax) + ")"

    return clipped
