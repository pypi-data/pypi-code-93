from pyxpad.pyxpad_utils import XPadDataDim, XPadDataItem
from pyxpad import user_functions
import numpy as np
import pytest
import warnings
import re

from Qt.QtWidgets import QInputDialog


def test_xpadfunction(test_data):
    def identity(data):
        return data

    identity_func = user_functions.XPadFunction(identity, name="identity")

    item = XPadDataItem(test_data)
    identity_item = identity_func(item)

    assert np.all(item.data == identity_item.data)
    assert np.all(item.dim == identity_item.dim)
    assert "identity(test data)" in str(identity_item)


@pytest.mark.parametrize(
    "func",
    [
        "sin",
        "cos",
        "tan",
        "exp",
        "exponential",
        "log",
        "nlog",
        "sqrt",
        "absolute",
        "arcsin",
        "arccos",
        "arctan",
    ],
)
def test_basic_arithmetic_functions(test_data, func):
    item = XPadDataItem(test_data)

    func_names = {
        "absolute": "abs",
        "exponential": "exp",
        "nlog": "log",
    }
    func_name = func_names.get(func, func)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        user_func = getattr(user_functions, func)
        func_item = user_func(item)
        np_func = getattr(np, func_name)
        np_data = np_func(test_data["data"])

    assert f"{func_name}(test data)" in str(func_item)
    assert np.allclose(func_item.data, np_data, equal_nan=True)


def test_reciprocal(test_data):
    item = XPadDataItem(test_data)

    reciprocal_item = user_functions.reciprocal(item)
    np_reciprocal = np.reciprocal(test_data["data"])

    assert "recip(test data)" in str(reciprocal_item)
    assert chr(0x207B) + chr(0x00B9) in reciprocal_item.units
    assert np.allclose(reciprocal_item.data, np_reciprocal, equal_nan=True)


def test_normalise(test_data):
    test_data["data"] = 4.0 * np.ones((4))
    test_data["dim"] = [XPadDataDim({"data": np.linspace(0.0, 1.0, 4)})]
    item = XPadDataItem(test_data)

    norm_item = user_functions.normalise(item)
    np_norm = np.ones((4))

    assert "Norm(test data)" in str(norm_item)
    assert np.allclose(norm_item.data, np_norm)


def test_invert(test_data):
    item = XPadDataItem(test_data)

    invert_item = user_functions.invert(item)
    np_invert = -test_data["data"]

    assert "-test data" in str(invert_item)
    assert np.allclose(invert_item.data, np_invert, equal_nan=True)


def test_add_constant(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    constant = 3.14
    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (constant, True))
    result = user_functions.addcon(item)

    assert f"test data + {constant}" in str(result)
    assert np.allclose(result.data, test_data["data"] + constant)


def test_dont_add_constant(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (1.0, False))
    with pytest.raises(RuntimeError):
        user_functions.addcon(item)


def test_sub_constant(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    constant = 99.9
    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (constant, True))
    result = user_functions.subcon(item)

    assert f"test data - {constant}" in str(result)
    assert np.allclose(result.data, test_data["data"] - constant)


def test_dont_sub_constant(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (1.0, False))
    with pytest.raises(RuntimeError):
        user_functions.subcon(item)


def test_mul_constant(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    constant = 6.5
    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (constant, True))
    result = user_functions.mulcon(item)

    assert f"test data * {constant}" in str(result)
    assert np.allclose(result.data, test_data["data"] * constant)


def test_dont_mul_constant(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (1.0, False))
    with pytest.raises(RuntimeError):
        user_functions.mulcon(item)


def test_div_constant(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    constant = 33.3
    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (constant, True))
    result = user_functions.divcon(item)

    assert np.allclose(result.data, test_data["data"] / constant)
    assert f"test data / {constant}" in str(result)


def test_dont_div_constant(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (1.0, False))
    with pytest.raises(RuntimeError):
        user_functions.divcon(item)


def test_pow_constant(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    constant = 2
    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (constant, True))
    result = user_functions.powcon(item)

    assert np.allclose(result.data, test_data["data"] ** constant)
    assert f"(test data)^{constant}" in str(result)


def test_dont_pow_constant(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (1.0, False))
    with pytest.raises(RuntimeError):
        user_functions.powcon(item)


def test_change_units(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    unit_factor = 2.0
    new_unit_name = "new unit"
    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (unit_factor, True))
    monkeypatch.setattr(QInputDialog, "getText", lambda *args: (new_unit_name, True))
    result = user_functions.changeunits(item)

    assert np.allclose(result.data, test_data["data"] * unit_factor)
    assert f"test data({new_unit_name})" in str(result)


def test_statistics(test_data, capsys):
    item = XPadDataItem(test_data)

    user_functions.statistics(item)

    captured = capsys.readouterr()

    assert "Statistics on test data" in captured.out

    mean_line = re.search(r"Mean = (\d\.[\deE-]+)", captured.out)
    assert mean_line is not None
    mean = float(mean_line.group(1))
    assert np.allclose(mean, np.mean(item.data))

    std_line = re.search(r"Standard Deviation = (\d\.[\deE-]+)", captured.out)
    assert std_line is not None
    std = float(std_line.group(1))
    assert np.allclose(std, np.std(item.data))

    assert f"Range = ({np.min(item.data)}) - ({np.max(item.data)})" in captured.out


def test_time_offset(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    offset = 1.1
    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (offset, True))
    result = user_functions.timeOffset(item)

    assert np.allclose(result.dim[0].data, test_data["dim"][0].data + offset)


def test_bad_time_offset(test_data, qtbot, monkeypatch):
    item = XPadDataItem(test_data)

    monkeypatch.setattr(QInputDialog, "getDouble", lambda *args: (None, False))
    with pytest.raises(RuntimeError):
        user_functions.timeOffset(item)


def test_chop(test_data):
    item = XPadDataItem(test_data)

    result = user_functions.chop(item, 1.5, 2.5)

    assert len(result.data) == 1
    assert result.data == test_data["data"][1]


def test_bad_chop(test_data):
    item = XPadDataItem(test_data)

    with pytest.raises(ValueError):
        user_functions.chop(item, 2.5, 1.5)

    with pytest.raises(ValueError):
        user_functions.chop(item, 3.5, 4.5)

    with pytest.raises(ValueError):
        user_functions.chop(item, 0.5, 0.75)

    with pytest.raises(ValueError):
        user_functions.chop(item, 1.5, 1.75)


def test_clip(test_data):
    item = XPadDataItem(test_data)

    result = user_functions.clip(item, 0.0, 5.5)

    assert min(result.data) == 5.0
    assert max(result.data) == 5.0
    assert result.dim[0].data == [2.0]


def test_bad_clip(test_data):
    item = XPadDataItem(test_data)

    with pytest.raises(ValueError):
        user_functions.clip(item, 3.0, 0.0)

    with pytest.raises(ValueError):
        user_functions.clip(item, 3.0, 3.0)
