from pyxpad.pyxpad_utils import XPadDataDim, XPadDataItem
from pyxpad import calculus
import numpy as np


def test_integrate(test_data):
    x = np.linspace(0.0, 1.0)
    test_data["dim"] = [XPadDataDim({"data": x})]
    test_data["data"] = x

    item = XPadDataItem(test_data)

    result = calculus.integrate(item)

    assert np.allclose(result.data, 0.5 * (x ** 2))


def test_differentiate(test_data):
    x = np.linspace(0.0, 2.0 * np.pi, 128)
    test_data["dim"] = [XPadDataDim({"data": x})]
    test_data["data"] = np.sin(x)

    item = XPadDataItem(test_data)

    result = calculus.differentiate(item)

    assert np.allclose(result.data[1:-1], np.cos(x[1:-1]), 1e-2)
