# -*- coding: utf-8 -*-
"""
Functions related to figures and plots.

functions:

    * duration_curve - plots a duration curve

"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd


def duration_curve(T, ytitle=None, xtitle=None):
    """
    Plots a duration curve of the data in each of the columns of T.

    Inputs
    ----------
    T : pandas.DataFrame
        Data to plot

    ytitle : str or None
        Title for the y axis (None to ignore)
        Default : None

    xtitle : str or None
        Title for the x axis (None to ignore)
        Default : None

    Outputs
    ----------
    fig : plotly.graph_objects.Figure
        Figure
    """

    fig = go.Figure()

    for col_i in T:
        y_i = T[col_i].sort_values(axis=0, ascending=False, na_position="last")
        fig.add_trace(go.Scattergl(y=y_i, name=col_i, mode="lines"))

    if xtitle is not None:
        fig["layout"]["xaxis"]["title"] = xtitle
    if ytitle is not None:
        fig["layout"]["yaxis"]["title"] = ytitle

    return fig
