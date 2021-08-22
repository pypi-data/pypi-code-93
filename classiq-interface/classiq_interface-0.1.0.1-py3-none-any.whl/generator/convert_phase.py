from math import pi

_DEG_TO_RAD_RATIO = pi / 180


def phase_to_rad(deg: int) -> float:
    phase_in_rad = round(deg * _DEG_TO_RAD_RATIO, 4)
    return phase_in_rad


def to_canonical_phase(phase: float) -> float:
    return phase % (2 * pi)


def rad_to_deg(phase: float) -> int:
    return int(round(to_canonical_phase(phase) * (180 / pi)))
