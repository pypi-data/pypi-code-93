"""Unit tests for class `Detector`."""

#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from copy import deepcopy

import pytest

from pyxel.detectors import (
    CCD,
    CMOS,
    CCDCharacteristics,
    CCDGeometry,
    Characteristics,
    CMOSCharacteristics,
    CMOSGeometry,
    Detector,
    Environment,
    Material,
)

# from pyxel.data_structure.photon import Photon


@pytest.mark.parametrize(
    "cls, geometry, environment, characteristics, material",
    [
        # (Geometry(), Environment(), Characteristics(), Material()),
        # (Geometry(), Environment(), CCDCharacteristics(), Material()),
        # (Geometry(), Environment(), CMOSCharacteristics(), Material()),
        (CCD, CCDGeometry(), Environment(), Characteristics(), Material()),
        (CCD, CCDGeometry(), Environment(), CCDCharacteristics(), Material()),
        (CCD, CCDGeometry(), Environment(), CMOSCharacteristics(), Material()),
        (CMOS, CMOSGeometry(), Environment(), Characteristics(), Material()),
        (CMOS, CMOSGeometry(), Environment(), CCDCharacteristics(), Material()),
        (CMOS, CMOSGeometry(), Environment(), CMOSCharacteristics(), Material()),
    ],
)
def test_init(cls, geometry, environment, characteristics, material):
    """Test Detector.__init__ with valid entries."""

    # Create a `Detector`
    obj = cls(
        geometry=geometry,
        environment=environment,
        characteristics=characteristics,
        material=material,
    )

    # Test getters
    assert obj.geometry is geometry
    assert obj.environment is environment
    assert obj.characteristics is characteristics
    assert obj.material is material

    assert obj.charge is not None
    assert obj.pixel is not None
    assert obj.signal is not None
    assert obj.image is not None

    with pytest.raises(
        RuntimeError,
        match=r"Photon array is not initialized ! Please use a 'Photon Generation' model",
    ):
        _ = obj.photon


#
# @pytest.mark.parametrize("obj, other_obj", [
#     (Detector(Geometry(), Material(), Environment(), Characteristics()),        # TODO
#      Detector(Geometry(), Material(), Environment(), Characteristics())),
#     (Detector(CCDGeometry(), Material(), Environment(), Characteristics()),
#      Detector(CCDGeometry(), Material(), Environment(), Characteristics())),
#     (Detector(CMOSGeometry(), Material(), Environment(), Characteristics()),
#      Detector(CMOSGeometry(), Material(), Environment(), Characteristics())),
#
#     (Detector(Geometry(), Material(), Environment(), CCDCharacteristics()),
#      Detector(Geometry(), Material(), Environment(), CCDCharacteristics())),        # TODO
#     (Detector(CCDGeometry(), Material(), Environment(), CCDCharacteristics()),
#      Detector(CCDGeometry(), Material(), Environment(), CCDCharacteristics())),
#     (Detector(CMOSGeometry(), Material(), Environment(), CCDCharacteristics()),
#      Detector(CMOSGeometry(), Material(), Environment(), CCDCharacteristics())),
#
#     (Detector(Geometry(), Material(), Environment(), CMOSCharacteristics()),               # TODO
#      Detector(Geometry(), Material(), Environment(), CMOSCharacteristics())),
#     (Detector(CCDGeometry(), Material(), Environment(), CMOSCharacteristics()),
#      Detector(CCDGeometry(), Material(), Environment(), CMOSCharacteristics())),
#     (Detector(CMOSGeometry(), Material(), Environment(), CMOSCharacteristics()),
#      Detector(CMOSGeometry(), Material(), Environment(), CMOSCharacteristics())),
# ])
# def test_eq(obj, other_obj):
#     """Test Detector.__eq__."""
#     assert isinstance(obj, Detector)


@pytest.mark.parametrize(
    "obj", [CCD(CCDGeometry(), Material(), Environment(), CCDCharacteristics())]
)
def test_copy(obj):
    """Test Detector.copy."""
    assert isinstance(obj, Detector)
    id_obj = id(obj)
    new_obj = deepcopy(obj)
    assert id_obj == id(obj)
    assert new_obj is not obj
