import pandas as pd


def get_ele_use(epi: pd.Series, freq="H", negative_trend_check=True):
    if not isinstance(epi, pd.Series):
        raise TypeError("INPUT EPI NOT pandas.Series TYPE!")
    if not isinstance(epi.index, pd.DatetimeIndex):
        raise TypeError("INPUT EPI INDEX NOT datetime TYPE!")
    epi_dif = epi.sort_index().diff().fillna(0)
    if negative_trend_check:
        if (epi_dif < 0).any():
            raise ValueError("EPI DATA HAS NEGATIVE TREND!")
    epi.sort_index(inplace=True)
    epi_mark = epi.resample(freq).first().interpolate("linear").append(epi.iloc[[-1]])
    ele = -epi_mark.diff(periods=-1).dropna()
    return ele

