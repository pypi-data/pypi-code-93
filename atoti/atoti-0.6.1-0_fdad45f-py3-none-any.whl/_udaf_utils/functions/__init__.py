"""Implementations of ``ExistingJavaFunction``s to help convert operations to Java code."""

from .arithmetic_functions import (
    ADD_FUNCTION,
    MUL_FUNCTION,
    SUB_FUNCTION,
    TRUEDIV_FUNCTION,
)
from .array_functions import array_mean, array_sum
from .conditional_functions import (
    EQ_FUNCTION,
    GT_FUNCTION,
    GTE_FUNCTION,
    LT_FUNCTION,
    LTE_FUNCTION,
    NEQ_FUNCTION,
)
