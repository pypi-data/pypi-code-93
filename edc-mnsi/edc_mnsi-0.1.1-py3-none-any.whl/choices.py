from edc_constants.constants import (
    ABSENT,
    DECREASED,
    NORMAL,
    NOT_APPLICABLE,
    PRESENT,
    REDUCED,
)

from .constants import PRESENT_WITH_REINFORCEMENT

ANKLE_REFLEX_CHOICES = (
    (PRESENT, "Present"),
    (PRESENT_WITH_REINFORCEMENT, "Present/Reinforcement"),
    (ABSENT, "Absent"),
    (NOT_APPLICABLE, "Not applicable"),
)

MONOFILAMENT_CHOICES = (
    (NORMAL, "Normal"),
    (REDUCED, "Reduced"),
    (ABSENT, "Absent"),
    (NOT_APPLICABLE, "Not applicable"),
)

ULCERATION_CHOICES = (
    (ABSENT, "Absent"),
    (PRESENT, "Present"),
    (NOT_APPLICABLE, "Not applicable"),
)

VIBRATION_PERCEPTION_CHOICES = (
    (PRESENT, "Present"),
    (DECREASED, "Decreased"),
    (ABSENT, "Absent"),
    (NOT_APPLICABLE, "Not applicable"),
)
