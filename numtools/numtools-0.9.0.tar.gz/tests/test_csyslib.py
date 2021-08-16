#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `csyslib.csys.RCSys` package."""

import pytest

import numpy as np
from numtools.csyslib import RCSys, Register


def test_offseted_RCSys():
    """
    Create a coordinates system, then a second one referrencing the first
    one, then export a node from the latest to the ground and check new coordinates
    """
    # build an intermediate CSys based on three points (defined in 0)
    rc = RCSys(
        points=(
            [-5.2, -4.3, 1.8],  # A (origin)
            [7.5, -2, 3.37],  # B (on Z-axis)
            [1.2, 1.56, -9.6],
        )
    )  # C (point in XZ plane)
    # build another CSys referrencing `rc`
    rc2 = RCSys(
        points=(
            [1.0, 1.0, -1.0],  # A (origin)
            [2.0, -2.3, -1.0],  # B (on Z-axis)
            [4.0, 8.0, -2.0],
        ),
        reference=rc,
    )  # C (point in XZ plane)
    # create a point in rc2
    p = np.array([0.73, -0.45, 1.2])
    p_in_rc0 = rc2.export_vertices(p)
    assert np.allclose(p_in_rc0, np.array([-6.66358316, -3.83264776, -0.18678528]))


def test_offseted_RCSys_using_Register():
    """
    Create a coordinates system, then a second one referrencing the first
    one, then export a node from the lates to the ground and check new coordinates
    """
    reg = Register(minid=3)
    # build an intermediate CSys based on three points (defined in 0)
    rc1 = reg.new(
        points=(
            [-5.2, -4.3, 1.8],  # A (origin)
            [7.5, -2, 3.37],  # B (on Z-axis)
            [1.2, 1.56, -9.6],
        )
    )  # C (point in XZ plane)
    assert rc1.id == 3
    # build another CSys referrencing `rc`
    rc2 = reg.new(
        points=(
            [1.0, 1.0, -1.0],  # A (origin)
            [2.0, -2.3, -1.0],  # B (on Z-axis)
            [4.0, 8.0, -2.0],
        ),
        reference_id=rc1.id,
    )  # C (point in XZ plane)
    assert rc2.id == 4
    # create a point in rc2
    p = np.array([0.73, -0.45, 1.2])
    p_in_rc0 = reg[4].export_vertices(p)
    assert np.allclose(p_in_rc0, np.array([-6.66358316, -3.83264776, -0.18678528]))
    # test dependancies are handled
    assert reg.deps(4) == [3]
    # test stacked points
    points = np.array([[0.73, -0.45, 1.2], [1, 2, 3], [-4, 5, 6.3]])
    pnts_in_rc0 = reg[4].export_vertices(points)
    expected = np.array(
        [
            [-6.663583, -3.832648, -0.186785],
            [-3.997904, -4.330918, -1.587242],
            [0.61787, -8.818401, 0.269404],
        ]
    )
    assert np.allclose(pnts_in_rc0, expected)
