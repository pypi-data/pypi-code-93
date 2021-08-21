"""Own functions to process data."""

import numpy as np


def perturb(data, pmean, pstd, prem):
    """Perturb the data."""
    # Perturb data
    data *= np.random.normal(pmean, pstd, data.shape)

    # Choose certain ratio of the data by random to illustrate loss of data
    data *= np.random.choice([np.nan, 1], size=(data.shape), p=[prem, 1 - prem])

    return data


def splitData(data, fraction_train=2 / 3, type_split="time"):
    """Split data into seen (training set) and unseen (test set) data."""
    # Get a list of data indices
    nonnans = np.argwhere(~np.isnan(data))
    index = np.arange(len(nonnans))

    # Copy original data structure to not mutate it
    train = data.copy()
    test = data.copy()

    # Specify which type of split we want
    # Split randomly over all datapoints
    if type_split == "random":
        # Shuffle the data in a random order
        np.random.shuffle(index)

        # Make division of data
        div = int(np.floor(len(index) * fraction_train))
        test_nan = index[:div]
        train_nan = index[div:]

        # Rebuild data into the two sets
        for i in train_nan:
            ti = nonnans[i]
            train[ti[0]][ti[1]] = np.nan
        for i in test_nan:
            ti = nonnans[i]
            test[ti[0]][ti[1]] = np.nan

    # Split over a section in time
    elif type_split == "time":
        # Make division of data
        div = int(np.floor(len(index) * fraction_train))
        test_nan = index[:div]
        train_nan = index[div:]

        # Rebuild data into the two sets
        for i in train_nan:
            ti = nonnans[i]
            train[ti[0]][ti[1]] = np.nan
        for i in test_nan:
            ti = nonnans[i]
            test[ti[0]][ti[1]] = np.nan

    return train, test
