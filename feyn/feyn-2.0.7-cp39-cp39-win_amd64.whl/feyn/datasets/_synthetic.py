from typing import Tuple
import pandas as pd

def make_classification(
    n_samples:int = 100,
    n_features:int = 20,
    stratify:bool = False,
    **kwargs
)-> Tuple:
    """Uses sklearn.datasets.make_classification to create a classification problem
    and returns train and test DataFrames.
    Keyword arguments are parameters in sklearn.datasets.make_classification and
    sklearn.model_selection.train_test_split.

    Args:
        n_samples (int, optional): The number of samples. Defaults to 100.
        n_features (int, optional): The number of features. Defaults to 20.
        stratify (bool, optional): Stratifies the train, test split by the target variable y. Defaults to False.

    Returns:
        train, test: The training and test set of the classification problem
    """
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split

    cls_kwargs = _determine_classifier_kwargs(**kwargs)
    split_kwargs = _determine_split_kwargs(**kwargs)

    X, y = make_classification(n_samples,n_features,**cls_kwargs)

    data = pd.DataFrame(X, columns=[f'x{i}' for i in range(X.shape[1])])
    data['y'] = y

    if stratify:
        split_kwargs["stratify"] = data["y"]

    train, test = train_test_split(data,**split_kwargs)

    return train, test

def make_regression(
    n_samples:int = 100,
    n_features:int = 20,
    stratify:bool = False,
    **kwargs
)-> Tuple:
    """Uses sklearn.datasets.make_regression to create a regression problem
    and returns train and test DataFrames.
    Keyword arguments are parameters in sklearn.datasets.make_regression and
    sklearn.model_selection.train_test_split.

    Args:
        n_samples (int, optional): The number of samples. Defaults to 100.
        n_features (int, optional): The number of features. Defaults to 20.
        stratify (bool, optional): Stratifies the train, test split by the target variable y. Defaults to False.

    Returns:
        Tuple: [description]
    """
    from sklearn.datasets import make_regression
    from sklearn.model_selection import train_test_split

    reg_kwargs = _determine_reg_kwargs(**kwargs)
    split_kwargs = _determine_split_kwargs(**kwargs)

    X,y = make_regression(n_samples,n_features,**reg_kwargs)

    data = pd.DataFrame(X, columns=[f"x{i}" for i in range(X.shape[1])])
    data["y"] = y

    if stratify:
        split_kwargs["stratify"] = data["y"]

    train, test = train_test_split(data, **split_kwargs)

    return train, test

def _determine_classifier_kwargs(**kwargs):

    cls_kwarg_names = [
        'n_informative',
        'n_redundant',
        'n_repeated',
        'n_classes',
        'n_clusters_per_class',
        'weights',
        'flip_y',
        'class_sep',
        'hypercube',
        'shift',
        'scale',
        'shuffle',
        'random_state'
    ]

    cls_kwargs = {}
    if kwargs:
        cls_kwargs = {key: kwargs[key] for key in kwargs if key in cls_kwarg_names}

    return cls_kwargs

def _determine_split_kwargs(**kwargs):

    split_kwarg_names = [
        'test_size',
        'train_size',
        'random_state',
        'shuffle',
    ]

    split_kwargs = {}
    if kwargs:
        split_kwargs = {key: kwargs[key] for key in kwargs if key in split_kwarg_names}

    return split_kwargs

def _determine_reg_kwargs(**kwargs):

    reg_kwarg_names = [
        "n_informative",
        "n_targets",
        "bias",
        "effective_rank",
        "tail_strength",
        "noise",
        "shuffle",
        "random_state"
    ]

    reg_kwargs = {key: kwargs[key] for key in kwargs if key in reg_kwarg_names}

    return reg_kwargs

