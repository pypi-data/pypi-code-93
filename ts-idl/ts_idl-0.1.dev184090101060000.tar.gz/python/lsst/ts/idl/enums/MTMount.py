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
# the Free Software Foundation either version 3 of the License or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License

__all__ = [
    "AxisMotionState",
    "Commander",
    "DeployableMotionState",
    "ElevationLockingPinMotionState",
    "LimitsMask",
    "PowerState",
    "System",
]

import enum


class AxisMotionState(enum.IntEnum):
    """Motion state of azimuth elevation and camera cable wrap."""

    STOPPING = 0
    STOPPED = 1
    MOVING_POINT_TO_POINT = 2
    JOGGING = 3
    TRACKING = 4
    TRACKING_PAUSED = 5


class Commander(enum.IntEnum):
    """Who commands the low-level controller."""

    NONE = 0
    CSC = 1
    EUI = 2
    HDD = 3


class DeployableMotionState(enum.IntEnum):
    """Motion state of deployable systems.

    These include the deployable platform, mirror covers,
    and mirror cover locks.
    """

    RETRACTED = 0
    DEPLOYED = 1
    RETRACTING = 2
    DEPLOYING = 3
    LOST = 4


class ElevationLockingPinMotionState(enum.IntEnum):
    """Position of elevation locking pin."""

    LOCKED = 0
    TEST = 1
    UNLOCKED = 2
    MOVING = 3
    MISMATCH = 4


class LimitsMask(enum.IntFlag):
    """Bit masks for the various limits.

    * L1 = software limit
    * L2 = direction inhibit
    * L3 = cut power
    """

    L1_MIN = 0x01
    L1_MAX = 0x02
    L2_MIN = 0x03
    L2_MAX = 0x04
    L3_MIN = 0x05
    L3_MAX = 0x06
    ADJUSTABLE_L1_MIN = 0x07
    ADJUSTABLE_L1_MAX = 0x08
    OPERATIONAL_L1_MIN = 0x09
    OPERATIONAL_L1_MAX = 0x10


class PowerState(enum.IntEnum):
    """Power state of a system or motion controller.

    Also used for motion controller state.

    Note that only a few systems (and no motion controllers)
    use TURNING_ON and TURNING_OFF. The oil supply system is one.
    """

    OFF = 0
    ON = 1
    FAULT = 2
    TURNING_ON = 3
    TURNING_OFF = 4
    UNKNOWN = 15


class System(enum.IntEnum):
    AZIMUTH = 0
    ELEVATION = 1
    CAMERA_CABLE_WRAP = 2
    BALANCE = 3
    MIRROR_COVERS = 4
    MIRROR_COVER_LOCKS = 5
    AZIMUTH_CABLE_WRAP = 6
    LOCKING_PINS = 7
    DEPLOYABLE_PLATFORMS = 8
    OIL_SUPPLY_SYSTEM = 9
    AZIMUTH_DRIVES_THERMAL = 10
    ELEVATION_DRIVES_THERMAL = 11
    AZ0101_CABINET_THERMAL = 12
    MODBUS_TEMPERATURE_CONTROLLERS = 13
    MAIN_CABINET = 14
    MAIN_AXES_POWER_SUPPLY = 15
    TOP_END_CHILLER = 16
