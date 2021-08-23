import enum


class LaserDetailedState(enum.IntEnum):
    """An enumeration class for handling the TunableLaser's substates.

    These enumerations listed here correspond to the ones found in the
    detailedState enum located in ts_xml under the TunableLaser folder within
    the TunableLaser_Events.xml.

    Attributes
    ----------

    NONPROPAGATING : `int`
        Corresponds to the nonpropgating state.
    PROPAGATINGSTATE : `int`
        Corresponds to the propagating state.

    """

    NONPROPAGATING = 1
    PROPAGATING = 2


class LaserErrorCode(enum.IntEnum):
    """Laser error codes"""

    ASCII_ERROR = 7301
    GENERAL_ERROR = 7302
    TIMEOUT_ERROR = 7303
    HW_CPU_ERROR = 7304
