"""Contains loaders returning pandas DataFrames."""
import inspect

import pandas as pd

from dbispipeline.base import Loader
from dbispipeline.utils import LOGGER


class DataframeLoader(Loader):
    """A generic one-in-all solution."""

    def __init__(self,
                 df_path,
                 features=None,
                 targets=None,
                 filters=None,
                 **extra_args):
        """
        Loads the data from a file on disk.

        Args:
            df_path: the path to the dataset file. If the filename ends with
                ".pckl", a read_pickle is attempted. If it ends with ".csv",
                a read_csv is attempted. Otherwise, an Error is raised.
            features: Which columns the data part of the result should contain.
                if this argument is falsy, all columns are returned.
            targets: which columns should be returned as target.
                if this argument is falsy, no target columns are returend.
            filters: a list of functions that are called on the resulting
                dataframe before it is split in data and target.
            **extra_args: any extra arguments that are stored in the db-config
                to help identify this generic instance.
        """
        self.features = features
        self.targets = targets or []
        self.df_path = df_path
        self.filters = filters or []
        self.extra_args = extra_args

    def load(self):
        """Loads the data."""
        if self.df_path.endswith('.pckl'):
            df = pd.read_pickle(self.df_path)
        elif self.df_path.endswith('.csv'):
            df = pd.read_csv(self.df_path)
        else:
            raise ValueError('unknown format for dataset: %s' % self.df_path)
        if df.empty:
            raise ValueError('loaded empty dataframe!')

        for f in self.filters:
            filtered_df = f(df)
            if filtered_df.empty:
                LOGGER.info('before filtering: %s', df)
                raise ValueError('dataframe is empty after filtering with: '
                                 f'{inspect.getsource(f)}')
            else:
                df = filtered_df
        if not self.features:
            self.features = df.columns
        return df[self.features], df[self.targets]

    @property
    def configuration(self):
        """Returns a database representation of this loader."""
        return dict(
            features=self.features,
            targets=self.targets,
            df_path=self.df_path,
            extra_args=self.extra_args,
        )
