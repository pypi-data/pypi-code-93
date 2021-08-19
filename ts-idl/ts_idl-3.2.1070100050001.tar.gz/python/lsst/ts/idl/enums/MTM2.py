__all__ = ["InclinationTelemetrySource"]

import enum


class InclinationTelemetrySource(enum.IntEnum):
    ONBOARD = 1
    MTMOUNT = 2
