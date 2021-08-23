from pyxpad.pyxpad_utils import XPadDataDim, XPadDataItem
import numpy as np
import pytest


def test_default_init():
    item = XPadDataItem()
    assert item is not None


def test_init_from_dict(test_data):
    item = XPadDataItem(test_data)

    assert np.all(item.data == test_data["data"])
    assert item.name == test_data["name"]
    assert np.all(item.dim == test_data["dim"])

    assert str(test_data["dim"][0]) in str(item)


def test_init_no_dims(test_data):
    # Removing the dimensions should still let us construct an XPadDataItem
    test_data.pop("dim")
    item = XPadDataItem(test_data)

    assert np.all(item.data == test_data["data"])
    assert item.name == test_data["name"]
    assert np.all(item.dim == XPadDataItem().dim)


def test_init_from_other(test_data):
    # Easy way to create an other object that doesn't have all the fields
    item1 = XPadDataItem(test_data)
    del item1.errl
    del item1.order
    del item1.time

    item2 = XPadDataItem(item1)

    assert np.all(item2.data == test_data["data"])
    assert item2.name == test_data["name"]
    assert np.all(item2.dim == test_data["dim"])

    assert str(test_data["dim"][0]) in str(item2)


def test_init_from_float():
    item = XPadDataItem(0.5)

    assert item.name == "0.5"
    assert item.data == 0.5


def test_repr():
    item = XPadDataItem()
    assert "XPadDataItem" in repr(item)


def test_add(test_data):
    item1 = XPadDataItem(test_data)
    item2 = XPadDataItem(test_data)

    item3 = item1 + item2

    assert np.all(item3.data == test_data["data"] * 2)
    assert "test data + test data" in str(item3)
    assert np.all(item3.errl == np.hypot(test_data["errl"], test_data["errl"]))
    assert np.all(item3.errh == np.hypot(test_data["errh"], test_data["errh"]))


def test_bad_add(test_data):
    item1 = XPadDataItem(test_data)
    item2 = XPadDataItem(test_data)
    item2.dim = [XPadDataDim()]

    # This won't work due to different dimensions
    with pytest.raises(ValueError):
        item3 = item1 + item2


def test_inplace_add(test_data):
    item1 = XPadDataItem(test_data)
    item2 = XPadDataItem(test_data)

    item1 += item2

    assert np.all(item1.data == test_data["data"] * 2)
    assert "test data + test data" in str(item1)
    assert np.all(item1.errl == np.hypot(test_data["errl"], test_data["errl"]))
    assert np.all(item1.errh == np.hypot(test_data["errh"], test_data["errh"]))


def test_right_add(test_data):
    item1 = XPadDataItem(test_data)

    item2 = 1.0 + item1

    assert np.all(item2.data == test_data["data"] + 1.0)
    assert "test data + 1." in str(item2)


def test_subtract(test_data):
    item1 = XPadDataItem(test_data)
    item2 = XPadDataItem(test_data)

    item3 = item1 - item2

    assert np.all(item3.data == np.zeros(len(test_data["data"])))
    assert "test data - test data" in str(item3)
    assert np.all(item3.errl == np.hypot(test_data["errl"], test_data["errh"]))
    assert np.all(item3.errh == np.hypot(test_data["errh"], test_data["errl"]))


def test_bad_subtract(test_data):
    item1 = XPadDataItem(test_data)
    item2 = XPadDataItem(test_data)
    item2.dim = [XPadDataDim()]

    # This won't work due to different dimensions
    with pytest.raises(ValueError):
        item3 = item1 - item2


def test_inplace_subtract(test_data):
    item1 = XPadDataItem(test_data)
    item2 = XPadDataItem(test_data)

    item1 -= item2

    assert np.all(item1.data == np.zeros(len(test_data["data"])))
    assert "test data - test data" in str(item1)
    assert np.all(item1.errl == np.hypot(test_data["errl"], test_data["errh"]))
    assert np.all(item1.errh == np.hypot(test_data["errh"], test_data["errl"]))


def test_right_subtract(test_data):
    item1 = XPadDataItem(test_data)

    item2 = 2.2 - item1

    assert np.all(item2.data == 2.2 - test_data["data"])
    assert "2.2 - test data" in str(item2)


def test_multiply(test_data):
    item1 = XPadDataItem(test_data)
    item2 = XPadDataItem(test_data)

    item3 = item1 * item2

    assert np.all(item3.data == test_data["data"] ** 2)
    assert "test data * test data" in str(item3)
    data_times_errl = test_data["data"] * test_data["errl"]
    data_times_errh = test_data["data"] * test_data["errh"]
    assert np.all(item3.errl == np.hypot(data_times_errl, data_times_errl))
    assert np.all(item3.errh == np.hypot(data_times_errh, data_times_errh))


def test_bad_multiply(test_data):
    item1 = XPadDataItem(test_data)
    item2 = XPadDataItem(test_data)
    item2.dim = [XPadDataDim()]

    # This won't work due to different dimensions
    with pytest.raises(ValueError):
        item3 = item1 * item2


def test_inplace_multiply(test_data):
    item1 = XPadDataItem(test_data)
    item2 = XPadDataItem(test_data)

    item1 *= item2

    assert np.all(item1.data == test_data["data"] ** 2)
    assert "test data * test data" in str(item1)
    data_times_errl = test_data["data"] * test_data["errl"]
    data_times_errh = test_data["data"] * test_data["errh"]
    assert np.all(item1.errl == np.hypot(data_times_errl, data_times_errl))
    assert np.all(item1.errh == np.hypot(data_times_errh, data_times_errh))


def test_right_multiply(test_data):
    item1 = XPadDataItem(test_data)

    item2 = 3.3 * item1

    assert np.all(item2.data == 3.3 * test_data["data"])
    assert "test data * 3.3" in str(item2)


def test_divide(test_data):
    item1 = XPadDataItem(test_data)
    item2 = XPadDataItem(test_data)

    item3 = item1 / item2

    assert np.all(item3.data == np.ones(len(test_data["data"])))
    assert "test data / test data" in str(item3)
    data = test_data["data"]
    errl = test_data["errl"]
    errh = test_data["errh"]
    assert np.all(item3.errl == np.hypot(errl / data, data * errh / data ** 2))
    assert np.all(item3.errh == np.hypot(errh / data, data * errl / data ** 2))


def test_bad_divide(test_data):
    item1 = XPadDataItem(test_data)
    item2 = XPadDataItem(test_data)
    item2.dim = [XPadDataDim()]

    # This won't work due to different dimensions
    with pytest.raises(ValueError):
        item3 = item1 / item2


def test_inplace_divide(test_data):
    item1 = XPadDataItem(test_data)
    item2 = XPadDataItem(test_data)

    item1 /= item2

    assert np.all(item1.data == np.ones(len(test_data["data"])))
    assert "test data / test data" in str(item1)
    data = test_data["data"]
    errl = test_data["errl"]
    errh = test_data["errh"]
    assert np.all(item1.errl == np.hypot(errl / data, data * errh / data ** 2))
    assert np.all(item1.errh == np.hypot(errh / data, data * errl / data ** 2))


def test_right_divide(test_data):
    item1 = XPadDataItem(test_data)

    item2 = 4.4 / item1

    assert np.all(item2.data == 4.4 / test_data["data"])
    assert "4.4 / test data" in str(item2)


def test_unary_negation(test_data):
    item1 = XPadDataItem(test_data)

    item2 = -item1

    assert np.all(item2.data == -test_data["data"])
    assert "-test data" in str(item2)
    assert np.all(item2.errh == test_data["errl"])
    assert np.all(item2.errl == test_data["errh"])


def test_unary_positive(test_data):
    item1 = XPadDataItem(test_data)

    item2 = +item1

    assert np.all(item2.data == test_data["data"])
    assert "test data" in str(item2)
    assert np.all(item2.errl == test_data["errl"])
    assert np.all(item2.errh == test_data["errh"])


def test_absolute(test_data):
    item1 = XPadDataItem(test_data)

    item2 = abs(item1)

    assert np.all(item2.data == abs(test_data["data"]))
    assert "abs(test data)" in str(item2)
    assert np.all(item2.errl == np.zeros(len(test_data["errl"])))
    assert np.all(item2.errh == test_data["errl"])
