import pandas as pd


def features(frame: pd.DataFrame, feature: str) -> ():
    """
    return a set of calculations
    :param frame: source
    :param feature: name of column in df
    :return: tuple of max min mean std
    """
    return frame[feature].max(), frame[feature].min(), frame[feature].mean(), frame[feature].std()


def features_dict(frame: pd.DataFrame, feature: str) -> {}:
    """
    return a set of calculations
    :param frame: source
    :param feature: name of column in df
    :return: tuple of max min mean std
    """
    return {'feature': feature, 'sum': frame[feature].sum(), 'max': frame[feature].max(), 'min': frame[feature].min(),
            'mean': frame[feature].mean(), 'std': frame[feature].std()}


def bucket_analysis(df: pd.DataFrame, features: ()) -> pd.DataFrame:
    """
    Analyze selected columns in a data frame Some basic data analysis
    :param df: Data Frame of algorithm features must contain columns count,size,file_count
    :type df: pandas.DataFrame
    :param features: list of columns to return sum, max, min, mean, stddev
    :return: Data Frame with the analysis features
    """

    feature_dict = [features_dict(df, x) for x in features]
    return pd.DataFrame(feature_dict)
    # format_str: str =\
    #     "Feature: {feature:<15}\tMax {_max:>20,.8}\tMin:{_min:>20,.8}\tmean:{_mean:>20,.8}\tstddev:{_std:>20,.8}"
    # _feature: str
    # for _feature in ('count', 'size', 'file_count'):
    #     _max, _min, mean, std = features(df, _feature)
    #     print(format_str.format(feature=_feature, _max=float(_max), _min=float(_min), _mean=mean, _std=std))


if __name__ == '__main__':
    data_frame = pd.read_csv(r'bucket_dist.csv')
    hoops = bucket_analysis(pd.read_csv(r'bucket_dist.csv'))
    print(hoops)
