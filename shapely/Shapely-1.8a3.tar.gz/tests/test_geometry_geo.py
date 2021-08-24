"""Tests of shape and mapping"""

import pytest

from shapely.errors import ShapelyDeprecationWarning
from shapely.geometry import MultiPolygon, Point, mapping, shape


def test_multipolygon():
    """A two-polygon multipolygon round trips correctly"""
    geom = MultiPolygon([Point(-1, -1).buffer(0.5), Point(1, 1).buffer(0.5)])
    with pytest.warns(ShapelyDeprecationWarning):
        assert len(geom) == 2
    geoj = mapping(geom)
    assert len(geoj['coordinates']) == 2
    geom2 = shape(geoj)
    with pytest.warns(ShapelyDeprecationWarning):
        assert len(geom2) == 2
