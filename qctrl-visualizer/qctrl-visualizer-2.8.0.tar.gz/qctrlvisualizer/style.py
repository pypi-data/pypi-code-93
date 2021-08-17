# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""
Functions for handling Q-CTRL styling.
"""

from contextlib import contextmanager
from typing import (
    Any,
    Dict,
)

from cycler import cycler
from matplotlib.style import context

BORDER_COLOR = "#D8E0E9"
TEXT_COLOR = "#6C5C71"


def get_qctrl_style() -> Dict[str, Any]:
    """
    Returns a dictionary representing the Q-CTRL styling in Matplotlib format.

    The returned dictionary is suitable for passing to Matplotlib functions such as
    ``matplotlib.style.use`` or ``matplotlib.style.context``.

    Returns
    -------
    dict
        The dictionary representing the Q-CTRL style.
    """
    style: Dict[str, Any] = {}

    # Used for legend text.
    style["text.color"] = TEXT_COLOR

    style["xtick.color"] = TEXT_COLOR
    style["ytick.color"] = TEXT_COLOR

    style["axes.spines.left"] = True
    style["axes.spines.right"] = True
    style["axes.spines.top"] = True
    style["axes.spines.bottom"] = True
    style["axes.edgecolor"] = BORDER_COLOR

    style["axes.labelsize"] = 11
    style["axes.labelcolor"] = TEXT_COLOR

    style["figure.facecolor"] = "white"

    style["legend.edgecolor"] = BORDER_COLOR

    style["lines.color"] = BORDER_COLOR

    style["axes.prop_cycle"] = cycler(
        color=[
            "#680CE9",
            "#EB6467",
            "#57CDC8",
            "#E583F7",
            "#CECF58",
            "#64A0EB",
            "#E98C55",
            "#EB64B6",
            "#57CD71",
        ]
    )

    return style


@contextmanager
def qctrl_style():
    """
    A ``ContextDecorator`` that enables the Q-CTRL Matplotlib styling.

    The returned object can act as a decorator::

        @qctrl_style()
        def plot(*args):
            # Matplotlib calls made in this function will use Q-CTRL styling.
            pass

    The returned object can also act as a context manager::

        with qctrl_style():
            # Matplotlib calls made in this function will use Q-CTRL styling.
            pass
    """
    with context(get_qctrl_style()) as ctx:
        yield ctx
