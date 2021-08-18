"""
Utility functions for calculating metrics
"""
import pandas as pd


def _add_index_level(inp, level_val, level_name):
    return pd.concat({level_val: inp}, names=[level_name])


def _time_mean(inp, variable=None):
    """
    Take time mean of data

    Parameters
    ----------
    inp : :obj:`scmdata.ScmRun`
        Data of which to take the time mean

    variable : str
        Value of the variable column in the output. If ``None``, the values
        are not altered from those in ``inp``.

    Returns
    -------
    :obj:`pd.Series`
        Time mean of the data
    """
    out = inp.timeseries().mean(axis="columns")
    out.name = "value"
    out = _add_index_level(out, inp["year"].min(), "evaluation_period_start_year")
    out = _add_index_level(out, inp["year"].max(), "evaluation_period_end_year")

    if variable is not None:
        out = _add_index_level(
            out.reset_index("variable", drop=True), variable, "variable"
        )

    return out


def _regression_slope(inp, unit):
    """
    Get regression slope of data

    Parameters
    ----------
    inp : :obj:`scmdata.ScmRun`
        Data of which to take the time mean

    unit : str
        Unit of the regression slope

    Returns
    -------
    :obj:`pd.Series`
        Regression slopes of data
    """
    out = inp.linear_regression_gradient(unit=unit)
    out = out.rename({"gradient": "value"}, axis="columns")

    new_index = list(set(out.columns) - {"value"})
    out = out.set_index(new_index)["value"]
    out = _add_index_level(out, inp["year"].min(), "evaluation_period_start_year")
    out = _add_index_level(out, inp["year"].max(), "evaluation_period_end_year")

    return out
