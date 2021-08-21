import numpy as np


def analyze_columns_type(dataframe, target_col, num_ratio_threshold=0.015):
    """
    Example usage:
    num_col, cat_col, bool_col, ord_col = analyze_columns_type(df, target_col)
    """
    df = dataframe.drop(columns=target_col).copy()
    cols = df.columns.values

    cat_col = cols[df.dtypes == object].tolist()
    bool_col = cols[df.dtypes == bool].tolist()
    num_col = cols[df.nunique() / len(df) > num_ratio_threshold].tolist()
    cols = np.array(list(set(cols) - set(cat_col + num_col)))
    df = df[cols]

    bool_col += cols[(df.dropna().nunique() == 2) & (df.dropna() < 2).all()].tolist()
    cols = np.array(list(set(cols) - set(cat_col + num_col + bool_col)))

    ord_col = cols.tolist()
    return num_col, cat_col, bool_col, ord_col
