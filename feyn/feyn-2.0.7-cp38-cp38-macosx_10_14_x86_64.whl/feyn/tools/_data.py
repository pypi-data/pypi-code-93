"""Helper functions that may make it easier to interact with feyn."""
import numpy as np
import feyn
from typing import List, Iterable

def split(data: Iterable, ratio:List[float]=[1,1], random_state:int = None) -> List[Iterable]:
    """
    Split datasets into random subsets

    This function is used to split a dataset into random subsets - typically training and test data.

    The input dataset should be either a pandas DataFrames or a dictionary of numpy arrays. The ratio parameter controls how the data is split, and how many subsets it is split into.

    Example: Split data in the ratio 2:1 into train and test data
    >>> train, test = feyn.tools.split(data, [2,1])

    Example: Split data in to train, test and validation data. 80% training data and 10% validation and holdout data each
    >>> train, validation, holdout = feyn.tools.split(data, [.8, .1, .1])


    Arguments:
        data -- The data to split (DataFrame or dict of numpy arrays).
        ratio -- the size ratio of the resulting subsets
        random_state -- the random state of the split (integer)

    Returns:
        list of subsets -- Subsets of the dataset (same type as the input dataset).
    """

    columns = list(data.keys())
    sz = len(data[columns[0]])

    rng = np.random.default_rng(seed=random_state)
    permutation = rng.permutation(sz)
    segment_sizes = np.ceil((np.array(ratio)/sum(ratio) * sz)).astype(int)

    segment_indices = []

    start_ix = 0
    for segment_size in segment_sizes:
        end_ix = start_ix+segment_size
        segment_indices.append(permutation[start_ix:end_ix])
        start_ix = end_ix

    result = []
    for indices in segment_indices:
        if type(data).__name__ == "DataFrame":
            result.append(data.iloc[indices])
        else:
            result.append({col: coldata[indices] for col, coldata in data.items()})

    return result


def select_features(df: Iterable, target:str, n:int = 25):
    res = {}
    # Compute mutual information
    for f in df.columns:
        if f == target:
            continue
        v = df[[f,target]].values.T
        mi = feyn.metrics.calculate_mi(v, float_bins=5)
        res[f]=mi
    
    # Sort by mutual information
    res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1], reverse=True)}
    
    return list(res)[:n]+[target]
