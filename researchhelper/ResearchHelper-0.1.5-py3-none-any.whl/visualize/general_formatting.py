"""Visualization helper functions and graphing."""

from matplotlib.ticker import AutoMinorLocator, MultipleLocator


def setStandardFrame(
    ax,
    x_major_td=0,
    x_minor_td=0,
    y_major_td=0,
    y_minor_td=0,
    x_lim=0,
    y_lim=0,
    lw=2,
    major_alpha=0.9,
    minor_alpha=0.7,
):
    """Implement helper function to standardize matplotlib graphs.

    Parameters
    ----------
    ax : matplotlib axis object
        Standard matplotlib axis object.
        E.g., as from output of `fig, ax = plt.subplots()`
    x_minor_td : int
        Set grid minor tick distance.
        This is in relation to the major grid. So a value of 2 result in
        there being 1 extra minor gridline halfway the major lines. 3, means
        at one-third, and two-thirds a minor line, etc. Defaults to 0.
    x_major_td : int
        Set grid major tick distance. Sets major
        gridlines on multiples of this value. Defaults to 0.
    y_major_td : int
        Set locators for grid. See x_minor_td.
        Defaults to 0.
    y_minor_td : int
        Set locators for grid. See x_major_td.
        Defaults to 0.
    x_lim : int
        Viewport limit on x-axis. Defaults to 0.
    y_lim : int
        Viewport limit on y-axis. Defaults to 0.
    lw : int
        Line width of the grid. Defaults to 2.
    major_alpha : float
        Set alpha of major gridlines. Defaults to 0.9.
    minor_alpha : float
        Set alpha of minor gridlines. Defaults to 0.7.

    Returns
    -------
    None

    """
    # Remove ticks
    ax.yaxis.set_tick_params(which="both", length=0)
    ax.xaxis.set_tick_params(which="both", length=0)

    # Customize domain limit if wanted
    if x_lim != 0:
        ax.set_x_lim(x_lim)
    if y_lim != 0:
        ax.set_y_lim(y_lim)

    # Customize minor and major ticks if wanted
    # Minor = majorTickDistance/minorTickDistance
    if x_major_td != 0:
        ax.xaxis.set_major_locator(MultipleLocator(x_major_td))
    if x_minor_td != 0:
        ax.xaxis.set_minor_locator(AutoMinorLocator(x_minor_td))
    if y_major_td != 0:
        ax.yaxis.set_major_locator(MultipleLocator(y_major_td))
    if y_minor_td != 0:
        ax.yaxis.set_minor_locator(AutoMinorLocator(y_minor_td))

    # Turn grid on for both major and minor ticks and style minor slightly
    # differently.
    ax.grid(which="major", color="#CCCCCC", linestyle="--", lw=lw, alpha=major_alpha)
    ax.grid(which="minor", color="#CCCCCC", linestyle=":", lw=lw, alpha=minor_alpha)

    # Remove box around figure
    for spine in ("top", "right", "bottom", "left"):
        ax.spines[spine].set_visible(False)


def setLabelsAndTitles(
    ax, title, xlabel, ylabel, tick_size=20, label_size=20, title_size=22
):
    """Set the labels and titles of the graph including it's (tick)sizes.

    Parameters
    ----------
    ax : matplotlib axis object
        Standard matplotlib axis object.
        E.g., as from output of `fig, ax = plt.subplots()`
    title : str
        Set graph title.
    xlabel : str
        Set label for a-axis.
    ylabel : str
        Set label for y-axis.
    tick_size : int
        Set size for the ticks. Defaults to 20.
    label_size : int
        Set size for the axes labels. Defaults to 20.
    title_size : int
        Set size for the graph title. Defaults to 22.

    Returns
    -------
    None

    """
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(tick_size)

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(tick_size)

    ax.set_xlabel(xlabel, fontsize=label_size)
    ax.set_ylabel(ylabel, fontsize=label_size)
    ax.set_title(title, fontsize=title_size)


def setLegend(ax, loc=0, lr_loc=1.05, ud_loc=1, size=16):
    """Set legend for graphs.

    You can set the legend either at a previously specified location
    by setting the loc, or a tuple made from lr_loc and ud_loc.

    Parameters
    ----------
    ax : matplotlib axis object
        Standard matplotlib axis object.
        E.g., as from output of `fig, ax = plt.subplots()`
    loc : int
        The location of the legend.
        The strings 'upper left', 'upper right', 'lower left',
        'lower right' place the legend at the corresponding
        corner of the axes/figure.
        The strings 'upper center', 'lower center', 'center left',
        'center right' place the legend at the center of the
        corresponding edge of the axes/figure.
        The string 'center' places the legend at the center of the
        axes/figure.
        The string 'best' places the legend at the location, among
        the nine locations defined so far, with the minimum
        overlap with other drawn artists. This option can be
        quite slow for plots with large amounts of data; your
        plotting speed may benefit from providing a specific
        location. Defaults to 0.
    lr_loc : float
        Left-right location. Defaults to 1.05.
    ud_loc : int
        Up-down location. Defaults to 1.
    size : int
        Scaling the legend. Defaults to 16.

    Returns
    -------
    None

    """
    if loc == 0:
        ax.legend(bbox_to_anchor=(lr_loc, ud_loc), prop={"size": size})
    else:
        ax.legend(loc=loc, prop={"size": size})
