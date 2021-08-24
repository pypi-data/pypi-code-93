import pandas as pd


def subset(df, **levels):
    """easily subset a dataframe"""
    levelnames = df.index.names
    unknown = set(levels.keys()) - set(levelnames)
    if unknown:
        levels = {k: v for k, v in levels.items() if k in levelnames}
    # validate levels
    filters = []
    for levelname in levelnames:
        if levelname not in levels or levels[levelname] is None:
            filter = slice(None)
        else:
            filter = levels[levelname]
            if isinstance(filter, str):
                filters.append([filter])
                continue
            try:
                filter = list(filter)
            except TypeError:
                filter = [filter]
        filters.append(filter)
    return df.loc[tuple(filters), :]
