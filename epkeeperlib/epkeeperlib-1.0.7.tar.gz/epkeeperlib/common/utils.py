import os

import pandas as pd


def divide(x, y, r=None, percent=None):
    """
    :param x: 被除数
    :param y: 除数
    :param r: default None, 保留小数位
    :param percent: default None, 百分比类型，可选：ratio（占比）、compare（增减百分比）
    """
    if not percent:
        if y == 0:
            return 0
        else:
            if r:
                if not isinstance(r, int):
                    raise TypeError("r MUST BE INTEGER!")
                if r < 0:
                    raise ValueError("r MUST BE NON-NEGATIVE!")
                elif r == 0:
                    return round(x / y)
                else:
                    return round(x / y, r)
            else:
                return x / y
    elif percent == "ratio":
        if y == 0:
            return "0.00%"
        else:
            return "{:.2%}".format(x / y)
    elif percent == "compare":
        if y == 0:
            return "-"
        else:
            return "{:.2%}".format(x / y - 1)
    else:
        raise ValueError("INVALID percent VALUE!")


def print_df(df: pd.DataFrame):
    print("\t", "\t".join(df.columns.astype(str)))
    for idx, row in df.iterrows():
        print(idx, "\t", "\t".join(row.astype(str).values))


def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
