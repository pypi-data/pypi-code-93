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
Functions for plotting control pulses.
"""

from collections import namedtuple
from typing import (
    Any,
    List,
)

import numpy as np
from matplotlib.ticker import ScalarFormatter

from .style import qctrl_style


@qctrl_style()
def plot_controls(
    figure, controls, polar=True, smooth=False, unit_symbol="Hz", two_pi_factor=True
):
    """
    Creates a plot of the specified controls.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        The matplotlib Figure in which the plots should be placed. The dimensions of the Figure
        will be overridden by this method.
    controls : dict
        The dictionary of controls to plot. The keys should be the names of the controls, and the
        values the list of segments representing the pulse of that control. Each such segment must
        be a dictionary with 'value' and 'duration' keys, giving the value (possibly complex, in the
        units specified by `unit_symbol`) and duration (in seconds) of that segment of the pulse.
        For example, the following would be a valid ``controls`` input::

            {
             'Clock': [
                 {'duration': 1.0, 'value': -0.5},
                 {'duration': 1.0, 'value': 0.5},
                 {'duration': 2.0, 'value': -1.5},
             ],
             'Microwave': [
                 {'duration': 0.5, 'value': 0.5 + 1.5j},
                 {'duration': 1.0, 'value': 0.2 - 0.3j},
             ],
            }

    polar : bool, optional
        The mode of the plot when the values appear to be complex numbers.
        Plot magnitude and angle in two figures if set to True, otherwise plot I and Q
        in two figures. Defaults to True.
    smooth : bool, optional
        Whether to plot the controls as samples joined by straight lines, rather than as
        piecewise-constant segments. Defaults to False.
    unit_symbol : str, optional
        The symbol of the unit to which the controls values correspond. Defaults to "Hz".
    two_pi_factor : bool, optional
        Whether the values of the controls should be divided by 2π in the plots.
        Defaults to True.

    Raises
    ------
    ValueError
        If any of the input parameters are invalid.
    """
    plots_data: List[Any] = []
    for name, segments in controls.items():
        durations = []
        values = []
        for segment in segments:
            durations.append(segment["duration"])
            values.append(segment["value"])
        values = np.array(values)
        plots_data = plots_data + _create_plots_data_from_control(
            name, durations, values, polar, unit_symbol, two_pi_factor
        )

    # Get the appropriate scaling for the time axis based on the total durations of all controls.
    time_scaling, time_prefix = _get_units(
        [sum(plot_data.xdata) for plot_data in plots_data]
    )

    axes_list = _create_axes(figure, len(plots_data), width=7.0, height=2.0)

    if smooth:
        for axes, plot_data in zip(axes_list, plots_data):
            # Convert the list of durations into a list of times at the midpoints of each segment,
            # with a leading zero and trailing total time.
            # Length of 'times' is m+2 (m is the number of segments).
            end_points = np.cumsum(plot_data.xdata)
            times = (
                np.concatenate(
                    [
                        [0.0],
                        end_points - np.array(plot_data.xdata) * 0.5,
                        [end_points[-1]],
                    ]
                )
                / time_scaling
            )
            # Pad each values array with leading and trailing zeros, to indicate that the pulse is
            # zero outside the plot domain. Length of 'values' is m+2.
            values = np.pad(plot_data.values, ((1, 1)), "constant")

            axes.plot(times, values, linewidth=2)
            axes.fill(times, values, alpha=0.3)

            axes.axhline(y=0, linewidth=1, zorder=-1)
            axes.set_ylabel(plot_data.ylabel)

    else:
        for axes, plot_data in zip(axes_list, plots_data):
            # Convert the list of durations into times, including a leading zero. Length of 'times'
            # is m+1 (m is the number of segments).
            times = np.insert(np.cumsum(plot_data.xdata), 0, 0.0) / time_scaling
            # Pad each values array with leading and trailing zeros, to indicate that the pulse is
            # zero outside the plot domain. Length of 'values' is m+2.
            values = np.pad(plot_data.values, ((1, 1)), "constant")

            #              *---v2--*
            #              |       |
            #       *--v1--*       |        *-v4-*
            #       |              |        |    |
            #       |              *---v3---*    |
            # --v0--*                            *---v5--
            #       t0     t1      t2       t3   t4
            # To plot a piecewise-constant pulse, we need to sample from the times array at indices
            # [0, 0, 1, 1, ..., m-1, m-1, m, m  ], and from the values arrays at indices
            # [0, 1, 1, 2, ..., m-1, m,   m, m+1].
            time_indices = np.repeat(np.arange(len(times)), 2)
            value_indices = np.repeat(np.arange(len(values)), 2)[1:-1]

            axes.plot(times[time_indices], values[value_indices], linewidth=2)
            axes.fill(times[time_indices], values[value_indices], alpha=0.3)

            axes.axhline(y=0, linewidth=1, zorder=-1)
            for time in times:
                axes.axvline(x=time, linestyle="--", linewidth=1, zorder=-1)

            axes.set_ylabel(plot_data.ylabel)

    axes_list[-1].set_xlabel(f"Time ({time_prefix}s)")


@qctrl_style()
def plot_smooth_controls(
    figure, controls, polar=True, unit_symbol="Hz", two_pi_factor=True
):
    """
    Creates a plot of the specified smooth controls.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        The matplotlib Figure in which the plots should be placed. The dimensions of the Figure
        will be overridden by this method.
    controls : dict
        The dictionary of controls to plot. The keys should be the names of the controls, and the
        values the list of samples representing the pulse of that control. Each such sample must
        be a dictionary with 'value' and 'time' keys, giving the value (possibly complex, in the
        units specified by `unit_symbol`)  and time (in seconds) of that sample of the pulse. The
        times must be in increasing order.
        For example, the following would be a valid ``controls`` input::

            {
             'Clock': [
                 {'time': 0.0, 'value': -0.5},
                 {'time': 1.0, 'value': 0.5},
                 {'time': 3.0, 'value': -1.5},
             ],
             'Microwave': [
                 {'time': 0.5, 'value': 0.5 + 1.5j},
                 {'time': 2.0, 'value': 0.2 - 0.3j},
             ],
            }
    polar : bool, optional
        The mode of the plot when the values appear to be complex numbers.
        Plot magnitude and angle in two figures if set to True, otherwise plot I and Q
        in two figures. Defaults to True.
    unit_symbol : str, optional
        The symbol of the unit to which the controls values correspond. Defaults to "Hz".
    two_pi_factor : bool, optional
        Whether the values of the controls should be divided by 2π in the plots.
        Defaults to True.

    Raises
    ------
    ValueError
        If any of the input parameters are invalid.
    """
    plots_data: List[Any] = []
    for name, samples in controls.items():
        times = []
        values = []
        for sample in samples:
            times.append(sample["time"])
            values.append(sample["value"])
        values = np.array(values)
        plots_data = plots_data + _create_plots_data_from_control(
            name, times, values, polar, unit_symbol, two_pi_factor
        )

    # Get the appropriate scaling for the time axis based on the total durations of all controls.
    time_scaling, time_prefix = _get_units(
        [max(plot_data.xdata) for plot_data in plots_data]
    )

    axes_list = _create_axes(figure, len(plots_data), width=7.0, height=2.0)

    for axes, plot_data in zip(axes_list, plots_data):
        # Pad with leading and trailing zeros, to indicate that the pulse is zero outside the plot
        # domain.
        times = np.pad(plot_data.xdata, ((1, 1)), "edge") / time_scaling
        values = np.pad(plot_data.values, ((1, 1)), "constant")

        axes.plot(times, values, linewidth=2)
        axes.fill(times, values, alpha=0.3)

        axes.axhline(y=0, linewidth=1, zorder=-1)

        axes.set_ylabel(plot_data.ylabel)

    axes_list[-1].set_xlabel(f"Time ({time_prefix}s)")


# Internal named tuple containing data required to draw a single plot. Note that xdata can represent
# either durations (of segments) or times (of samples), depending on whether the plot is for a
# piecewise-constant or smooth pulse.
_PlotData = namedtuple("_PlotData", ["ylabel", "xdata", "values"])


def _get_units(values):
    """
    For the given range of values, calculates the units to be used for plotting.  Specifically,
    returns a tuple (scaling factor, prefix), for example (1000, 'k') or (0.001, 'm'). The values
    should be divided by the first element, and the unit label prepended with the second element.
    If the values are zero the scaling factor is 1.
    """
    prefixes = {
        -24: "y",
        -21: "z",
        -18: "a",
        -15: "f",
        -12: "p",
        -9: "n",
        -6: "\N{MICRO SIGN}",
        -3: "m",
        0: "",
        3: "k",
        6: "M",
        9: "G",
        12: "T",
        15: "P",
        18: "E",
        21: "Z",
        24: "Y",
    }
    # We apply a simple algorithm: get the element with largest magnitude, then map according to
    # [0.001, 1) -> 0.001x/milli,
    # [1, 1000) -> no scaling,
    # [1000, 1e6) -> 1000x/kilo,
    # and so on.
    max_value = max(np.abs(values))
    exponent = float(
        3
        * np.floor_divide(np.log10(max_value, out=np.zeros(1), where=max_value > 0), 3)
    )
    # Clip the scaling to the allowable range.
    exponent_clipped = np.clip(exponent, -24, 24)
    return 10 ** exponent_clipped, prefixes[exponent_clipped]


def _create_plots_data_from_control(
    name, xdata, values, polar, unit_symbol, two_pi_factor
):
    """
    Creates a list of _PlotData objects for the given control data.
    """

    # Scale values (and name) if they're to be divided by 2π
    if two_pi_factor:
        scaled_values = values / (2 * np.pi)
        scaled_name = f"{name}$/2\\pi$"
    else:
        scaled_values = values
        scaled_name = name

    if not np.iscomplexobj(values):
        # Real control.
        prefix_scaling, prefix = _get_units(scaled_values)
        return [
            _PlotData(
                xdata=xdata,
                values=scaled_values / prefix_scaling,
                ylabel=f"{scaled_name}\n({prefix}{unit_symbol})",
            )
        ]

    if polar:
        # Complex control, split into polar coordinates.
        prefix_scaling, prefix = _get_units(scaled_values)
        return [
            _PlotData(
                xdata=xdata,
                values=np.abs(scaled_values) / prefix_scaling,
                ylabel=f"{scaled_name}\nModulus\n({prefix}{unit_symbol})",
            ),
            _PlotData(
                xdata=xdata,
                values=np.angle(values),
                ylabel=f"{name}\nAngle\n(rad)",
            ),
        ]

    # Complex control, split into rectangle coordinates.
    prefix_scaling_x, prefix_x = _get_units(np.real(scaled_values))
    prefix_scaling_y, prefix_y = _get_units(np.imag(scaled_values))
    return [
        _PlotData(
            xdata=xdata,
            values=np.real(scaled_values) / prefix_scaling_x,
            ylabel=f"{scaled_name}\nI\n({prefix_x}{unit_symbol})",
        ),
        _PlotData(
            xdata=xdata,
            values=np.imag(scaled_values) / prefix_scaling_y,
            ylabel=f"{scaled_name}\nQ\n({prefix_y}{unit_symbol})",
        ),
    ]


@qctrl_style()
def plot_sequences(figure, seq):
    """
    Creates plot of dynamical decoupling sequences.

    Parameters
    ----------
    figure: matplotlib.figure.Figure
        The matplotlib Figure in which the plots should be placed. The dimensions of the Figure
        will be overridden by this method.
    seq: dict
        The dictionary of controls to plot. Works the same as the dictionary for
        plot_controls, but takes 'offset' instead of 'duration' and 'rotation'
        instead of 'value'. Rotations can be around any axis in the XY plane.
        Information about this axis is encoded in the complex argument of the
        rotation. For example, a pi X-rotation is represented by the complex
        number 3.14+0.j, whereas a pi Y-rotation is 0.+3.14j. The argument of the
        complex number is plotted separately as the azimuthal angle.
    """
    plots_data: List[Any] = []
    for name, pulses in seq.items():
        offsets = [pulse["offset"] for pulse in pulses]
        rotations = [pulse["rotation"] for pulse in pulses]
        rotations = np.array(rotations)
        plots_data = plots_data + _create_plots_data_from_sequence(
            name, offsets, rotations
        )

    axes_list = _create_axes(figure, len(plots_data), width=9.0, height=2.0)

    for axes, plot_data in zip(axes_list, plots_data):
        # The plot_data.offsets array contains only the points where the
        # dynamical decoupling pulses occur. For plotting purposes, it is
        # necessary to have three points describing each instantaneous pulse:
        # one at zero before the pulse, one with the actual value of the
        # pulse, and a third one at zero just after the pulse. The following
        # function triples the number of points in the time array so that
        # the pulses can be drawn like that.
        times = np.repeat(plot_data.offsets, 3)
        time_scaling, time_prefix = _get_units(times)
        times /= time_scaling

        # Besides three points for each pulse, two extra points have to be
        # added: one before all the pulses and one after all of them.
        # np.pad() adds these points, with the first one located at t=0,
        # and the line after it makes sure that
        # the distance between the last point and the last pulse is the same
        # as the distance between the first point and the first pulse. This
        # gives an overall symmetric look to the plot.
        times = np.pad(times, ((1, 1)), "constant")
        times[-1] = times[-2] + times[1]

        values = np.zeros(3 * len(plot_data.rotations))
        values[1::3] = plot_data.rotations

        values = np.pad(values, ((1, 1)), "constant")

        axes.plot(times, values, linewidth=2)

        axes.axhline(y=0, linewidth=1, zorder=-1)
        for time in plot_data.offsets:
            axes.axvline(x=time, linestyle="--", linewidth=1, zorder=-1)

        axes.set_ylabel(plot_data.label)

    axes_list[-1].set_xlabel("Time ({0}s)".format(time_prefix))


_PlotSeqData = namedtuple("_PlotSeqData", ["label", "offsets", "rotations"])


def _create_plots_data_from_sequence(name, offsets, rotations):
    """
    Creates a list of _PlotSeqData objects for the given dynamical decoupling data.
    """
    if not np.iscomplexobj(rotations):
        return [
            _PlotSeqData(
                offsets=offsets,
                rotations=rotations,
                label="{0}\nrotations\n(rad)".format(name),
            )
        ]
    return [
        _PlotSeqData(
            offsets=offsets,
            rotations=np.abs(rotations),
            label="{0}\nrotations\n(rad)".format(name),
        ),
        _PlotSeqData(
            offsets=offsets,
            rotations=np.angle(rotations),
            label="{0}\nazimuthal angles\n(rad)".format(name),
        ),
    ]


def _create_axes(figure, count, width, height):
    """
    Creates a set of axes with default axis labels and axis formatting.

    The axes are stacked vertically, and share an x axis (automatically labeled with 'Time (s)').

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        The matplotlib Figure in which the axes should be placed. The dimensions of the Figure will
        be overridden by this method.
    count : int
        The number of axes to create.
    width : float
        The width (in inches) for each axes.
    height : float
        The height (in inches) for each axes.

    Returns
    -------
    list
        The list of Axes objects.
    """
    figure.set_figheight(height * count)
    figure.set_figwidth(width)
    figure.subplots_adjust(hspace=0.5)

    axes_list = figure.subplots(
        nrows=count, ncols=1, sharex=True, sharey=False, squeeze=False
    )[:, 0]

    # Set axis formatting.
    for axes in axes_list:
        axes.yaxis.set_major_formatter(ScalarFormatter())
        axes.xaxis.set_major_formatter(ScalarFormatter())

    return axes_list
