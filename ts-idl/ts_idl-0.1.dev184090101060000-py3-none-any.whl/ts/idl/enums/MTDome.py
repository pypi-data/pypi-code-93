# This file is part of ts_idl.
#
# Developed for Vera Rubin Observatory.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License

__all__ = ["EnabledState", "Louver", "MotionState"]

import enum


class EnabledState(enum.IntEnum):
    """Drive enabled state."""

    DISABLED = 1
    ENABLED = 2
    FAULT = 3


class Louver(enum.IntEnum):
    """Louver name and associated array index."""

    A1 = 0
    B1 = 1
    A2 = 2
    B2 = 3
    B3 = 4
    N1 = 5
    M1 = 6
    N2 = 7
    M2 = 8
    M3 = 9
    C1 = 10
    C2 = 11
    C3 = 12
    L1 = 13
    L2 = 14
    L3 = 15
    E1 = 16
    D2 = 17
    E2 = 18
    D3 = 19
    E3 = 20
    I1 = 21
    H1 = 22
    I2 = 23
    H2 = 24
    I3 = 25
    H3 = 26
    F1 = 27
    G1 = 28
    F2 = 29
    G2 = 30
    F3 = 31
    G3 = 32
    D1 = 33


class MotionState(enum.IntEnum):
    """Motion state."""

    FAULT = 0
    CLOSED = 1
    CRAWLING = 2
    MOVING = 3
    OPEN = 4
    PARKED = 5
    PARKING = 6
    STOPPED = 7
    STOPPING = 8
    STOPPING_BRAKING = 9
    STOPPED_BRAKED = 10
