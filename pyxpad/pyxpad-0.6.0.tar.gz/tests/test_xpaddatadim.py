from pyxpad.pyxpad_utils import XPadDataDim


def test_default_init():
    dim = XPadDataDim()
    assert dim is not None


def test_default_equality():
    dim1 = XPadDataDim()
    dim2 = XPadDataDim()
    assert dim1 == dim2


def test_str():
    dim1 = XPadDataDim()
    dim1.name = "Test dim"

    assert str(dim1) == "Test dim"


def test_construct_from_complete_other():
    class Other:
        pass

    other = Other()
    other.name = "other"
    other.label = "something else"
    other.units = "m"
    other.data = [1, 2, 3]
    other.errl = [0.1, 0.2, 0.3]
    other.errh = [1.1, 2.2, 3.3]

    dim1 = XPadDataDim(other)

    assert dim1.name == "other"
    assert dim1.label == "something else"
    assert dim1.units == "m"
    assert dim1.data == [1, 2, 3]
    assert dim1.errl == [0.1, 0.2, 0.3]
    assert dim1.errh == [1.1, 2.2, 3.3]
    assert dim1 == other


def test_construct_from_incomplete_other():
    class Other:
        pass

    other = Other()
    other.label = "other"
    other.units = "m"
    other.data = [1, 2, 3]

    dim1 = XPadDataDim(other)

    assert dim1.name == "other"
    assert dim1.label == "other"
    assert dim1.units == "m"
    assert dim1.data == [1, 2, 3]
    assert dim1.errl == None
    assert dim1.errh == None

    dim2 = XPadDataDim(other)
    assert dim1 == dim2


def test_repr():
    class Other:
        pass

    other = Other()
    other.name = "other"
    other.units = "m"
    other.data = [1, 2, 3]

    dim1 = XPadDataDim(other)

    assert dim1.name == "other"
    assert dim1.label == ""
    assert dim1.units == "m"
    assert dim1.data == [1, 2, 3]
    assert dim1.errl == None
    assert dim1.errh == None

    dim2 = eval(repr(dim1))
    assert dim1 == dim2
