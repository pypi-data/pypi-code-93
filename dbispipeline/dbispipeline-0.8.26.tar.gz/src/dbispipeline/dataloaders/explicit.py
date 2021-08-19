"""Loaders that provide explicit splits for train/testing."""

from abc import abstractmethod
import os
import random
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from dbispipeline.base import Loader


def _load_df(path: str) -> pd.DataFrame:
    df = pd.read_csv(os.path.join(path, 'dataset.csv'))
    unnamed_columns = [c for c in df.columns if c.startswith('Unnamed')]
    if unnamed_columns:
        df = df.drop(columns=unnamed_columns)
    df['text_raw'] = [os.path.join(path, x) for x in df.text_raw]
    df['stanza'] = [os.path.join(path, x) for x in df.stanza]
    return df


def _attach(df: pd.DataFrame, y: np.array) -> Tuple[pd.DataFrame, str]:
    df = df.copy()
    # attach the column to the dataframe for grouping
    key_i = 0
    key = f'y_{key_i}'
    while key in df.columns:
        key_i += 1
        key = f'y_{key_i}'
    df[key] = y
    return df, key


def _limit(
        dataset_part: Tuple[pd.DataFrame, np.array],
        remaining_targets: List[str],
        max_docs_per_target: Optional[int],
) -> Tuple[pd.DataFrame, np.array]:
    df, key = _attach(dataset_part[0], dataset_part[1])
    sub_df = df[df[key].isin(remaining_targets)]
    if max_docs_per_target:
        sub_df = sub_df.groupby(key).sample(max_docs_per_target)
    return sub_df.drop(columns=key), sub_df[key].values


class CrossValidatedSplitLoader(Loader):
    """
    Base class for all loaders that don't have an explicit train/test split.

    A Stratified K-Fold is used to split the data, and the resulting splits are
    used for the explicit splits which can be used by the grid search 'cv'
    parameter.
    """

    def __init__(self, n_splits: int = 5, max_targets: int = None,
                 max_docs_per_target: int = None):
        """
        Initialize the loader.

        Args:
            n_splits: number of splits to be using for this CV-loader.
            max_targets: Maximum number of labels to be used. If this value is
                provided, a subset of all possible targets is used for both
                training and testing.
            max_docs_per_target: Maximum number of documents used for training
                each target. Does not influence testing data. Optional.
        """
        self.n_splits = n_splits
        self.max_targets = max_targets
        self.max_docs_per_target = max_docs_per_target

    def load(self) -> Tuple[pd.DataFrame, np.array, List[np.array]]:
        """
        Loads the data and the splits.

        This method gets all data from the abstract method `get_all_data`, and
        applies the stratified cv splitting as well as the optional limiting of
        targets or documents per target.

        Returns:
            A tuple of x, y, splits. The splits are something that can be
            passed to the GridSearchCV object as the 'cv' parameter.
        """
        x, y = self.get_all_data()
        x, key = _attach(x, y)
        all_targets = x[key].unique()

        if self.max_targets:
            selected_targets = random.sample(all_targets.tolist(),
                                             self.max_targets)
            # only take those rows with the selected targets
            x = x[x[key].isin(selected_targets)]
            x = x.reset_index(drop=True)

        all_splits = StratifiedKFold(n_splits=self.n_splits).split(
            # the first argument (X) is not used in a stratified k-fold split.
            np.zeros(x.shape[0]),
            x[key],
        )
        if not self.max_docs_per_target:
            splits = list(all_splits)
        else:
            splits = []
            for train_idx, test_idx in all_splits:
                df_train = pd.DataFrame(
                    dict(idx=train_idx, y=x[key][train_idx]))
                df_train = df_train.groupby('y').sample(
                    self.max_docs_per_target)
                splits.append((df_train.idx.values, test_idx))
        return x.drop(columns=[key]), x[key].values, splits

    @abstractmethod
    def get_all_data(self) -> pd.DataFrame:
        """
        Retrieves the entire data from which the splits are taken.

        Returns:
            A tuple of x, y, splits. The splits are something that can be
            passed to the GridSearchCV object as the 'cv' parameter.
        """
        pass

    @property
    def configuration(self) -> dict:
        """Returns the database representation of this loader."""
        return {
            'n_splits': self.n_splits,
            'max_targets': self.max_targets,
            'max_docs_per_target': self.max_docs_per_target,
        }


class TrainTestSplitLoader(Loader):
    """Base class for all Loaders that have an explicit Train/Test split."""

    def __init__(self, max_targets: int = None,
                 max_docs_per_target: int = None):
        """
        Initialize the loader.

        Args:
            max_targets: Maximum number of labels to be used. If this value is
                provided, a subset of all possible targets is used for both
                training and testing.
            max_docs_per_target: Maximum number of documents used for training
                each target. Does not influence testing data. Optional.
        """
        self.max_targets = max_targets
        self.max_docs_per_target = max_docs_per_target

    def load(self) -> Tuple[pd.DataFrame, np.array, List[np.array]]:
        """
        Loads the data and the splits.

        This method gets all data from the abstract method `get_train_data` and
        `get_test_data`, and then calculates the appropriate split indices
        while considering the optional limiting of any targets or documents per
        target.

        Returns:
            A tuple of x, y, splits. The splits are something that can be
            passed to the GridSearchCV object as the 'cv' parameter.
        """
        train, test = self.get_train_data(), self.get_test_data()
        all_targets = set(train[1])
        if self.max_targets:
            selected_targets = random.sample(all_targets, self.max_targets)
        else:
            selected_targets = list(all_targets)
        train = _limit(train, selected_targets, self.max_docs_per_target)
        test = _limit(test, selected_targets, None)  # don't limit test data
        train_idx = list(range(train[0].shape[0]))
        test_idx = list(
            range(train[0].shape[0], train[0].shape[0] + test[0].shape[0]))
        splits = [(train_idx, test_idx)]
        df = pd.concat([train[0], test[0]])
        y = np.concatenate([train[1], test[1]])
        return df, y, splits

    @abstractmethod
    def get_train_data(self) -> Tuple[pd.DataFrame, np.array]:
        """
        Retrieves the training data from the subclass.

        Returns:
            A tuple of training data in form of [DataFrame, np.Array]
        """
        pass

    @abstractmethod
    def get_test_data(self) -> Tuple[pd.DataFrame, np.array]:
        """
        Retrieves the testing data from the subclass.

        Returns:
            A tuple of training data in form of [DataFrame, np.Array]
        """
        pass

    @property
    def configuration(self) -> dict:
        """Returns the database representation of this loader."""
        return {
            'max_targets': self.max_targets,
            'max_docs_per_target': self.max_docs_per_target,
        }
