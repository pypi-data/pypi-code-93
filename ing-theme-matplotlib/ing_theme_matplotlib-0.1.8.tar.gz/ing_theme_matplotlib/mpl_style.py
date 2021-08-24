"""
This module contains the ``mpl_style`` function which applies the ing ``matplotlib`` theme

Some of the tick properties cannot be set using ``plt.style.use``,
so we have to set them in code.

We want the user to be able to apply the full style, including styling the
minor ticks, using only a _single_ function call. To make this possible we need
to monkey patch as we first need to apply the style using ``plt.style.use``,
then create a figure (using either ``plt.figure`` or ``plt.Figure`` or
``plt.subplots``), and _then_ get from this figure the axes to style the ticks.
"""
import matplotlib.pyplot as plt
import matplotlib.axes
from os.path import join, dirname, realpath
import os

STYLE_DIR = realpath(join(dirname(__file__), "styles"))
LOGOS_DIR = realpath(join(dirname(__file__), "logos"))
COMMON_STYLE = "common.mplstyle"
DARK_STYLE = "dark.mplstyle"
LIGHT_STYLE = "light.mplstyle"

__all__ = ["mpl_style"]


def mpl_style(dark: bool = True, minor_ticks: bool = True):
    """ Sets the matplotlib style
    Args:
        dark: Use the dark or light style (default: True)
        minor_ticks: Style the minor ticks (requires monkey patching)(default: True)
    """
    plt.style.use(
        join(STYLE_DIR, style)
        for style in [COMMON_STYLE, DARK_STYLE if dark else LIGHT_STYLE]
    )
    color = "FFFFFF" if dark else "000000"

    if minor_ticks:
        plt.subplots = _monkey_patch_subplot(color, plt.subplots)
        plt.Figure_ING = _monkey_patch_figure(color, plt.Figure)


def _style_ticks(axis, color):
    """ Enable minor ticks, and color major + minor ticks"""
    axis.minorticks_on()
    ticks = (
        axis.get_xticklines()
        + axis.xaxis.get_minorticklines()
        + axis.get_yticklines()
        + axis.yaxis.get_minorticklines()
    )

    for tick in ticks:
        tick.set_color("#" + color + "3D")


def _monkey_patch_figure(color, mat_Figure):
    """ Style a figure's current axis tick marks, just after the figure is
    created. """

    def _patch(*args, **kwargs):
        fig = mat_Figure(*args, **kwargs)
        _style_ticks(fig.gca(), color)
        return fig

    return _patch


def _monkey_patch_subplot(color, mat_subplot):
    """ Style all axes of a figure containing subplots, just after the
    figure is created. """

    def _patch(*args, **kwargs):
        fig, axes = mat_subplot(*args, **kwargs)
        axes_list = [axes] if isinstance(axes, matplotlib.axes.Axes) else axes
        for ax in axes_list:
            if isinstance(ax, matplotlib.axes.Axes):
                _style_ticks(ax, color)
            else:
                for each in ax:
                    _style_ticks(each, color)
        return fig, axes

    return _patch


def add_logo(bottom_right = 'ing_logo', bottom_left = None):
    """ Adds a logo to the plot. Logos can be placed at the bottom right and the bottom left. 
    Args:
        bottom_right: The default ING logo is used at the bottom right of the graph. 
                       To use other images at this position, the path where the image is located should be given such as 'logos/any_other_logo.png'.
        bottom_left: Default shows nothing. To use any image, the path the where the image is located should be given such as 'logos/any_other_logo.png'.
    """

    fig = plt.figure(constrained_layout=True, figsize = (12, 8))
    gs = fig.add_gridspec(8, 5)
    ax = fig.add_subplot(gs[0:7, :])

    ax1 = fig.add_subplot(gs[7:, 0:1])
    if bottom_left == 'ing_logo':
        img = ax1.imshow(plt.imread(os.path.join(LOGOS_DIR, 'ING_Logo.png')))
    elif bottom_left:
        if bottom_left != 'ing_logo':
            img = ax1.imshow(plt.imread(bottom_left))
    ax1.axis('off')

    ax2 = fig.add_subplot(gs[7:, -1:])
    
    if bottom_right == 'ing_logo':
        img2 = ax2.imshow(plt.imread(os.path.join(LOGOS_DIR, 'ING_Logo.png')))
    elif bottom_right:
        if bottom_right != 'ing_logo':
            img2 = ax2.imshow(plt.imread(bottom_right))
    ax2.axis('off')
    
    return fig.get_axes()[0]
