# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains dataloader functions for the classification tasks."""

import logging
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from torch.utils.data import Dataset as PyTorchDataset
from typing import Any, List, Tuple, Union, Optional

from azureml.automl.dnn.nlp.classification.common.constants import DatasetLiterals
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import (
    PyTorchDatasetWrapper,
    PyTorchMulticlassDatasetWrapper
)
from azureml.core import Dataset as AmlDataset
from azureml.core.workspace import Workspace


_logger = logging.getLogger(__name__)


def get_vectorizer(train_df: pd.DataFrame, val_df: Union[pd.DataFrame, None],
                   label_column_name: str) -> CountVectorizer:
    """Obtain labels vectorizer

    :param train_df: Training DataFrame
    :param val_df: Validation DataFrame
    :param label_column_name: Name/title of the label column
    :return: vectorizer
    """
    # Combine both dataframes if val_df exists
    if val_df is not None:
        combined_df = pd.concat([train_df, val_df])
    else:
        combined_df = train_df

    # Get combined label column
    combined_label_col = np.array(combined_df[label_column_name].astype(str))

    # TODO: CountVectorizer could run into memory issues for large datasets
    vectorizer = CountVectorizer(token_pattern=r"(?u)\b\w+\b", lowercase=False)
    vectorizer.fit(combined_label_col)

    return vectorizer


def concat_text_columns(df: pd.DataFrame, label_column_name: str) -> pd.DataFrame:
    """Concatenating text (feature) columns present in the dataframe.

    :param df: Dataframe with all columns
    :param label_column_name: Name/title of the label column
    :return: Combined text columns Dataframe
    """
    df_copy = df.copy()
    # Obtain the list of all columns
    df_columns = df_copy.columns

    if label_column_name in df_columns:
        df_copy.drop(columns=label_column_name, inplace=True)

    text_columns = df_copy.columns

    text_df = pd.DataFrame()
    text_df[DatasetLiterals.TEXT_COLUMN] = df_copy[text_columns[0]].map(str)

    # Iterate through other text columns and concatenate them
    for column_name in text_columns[1:]:
        text_df[DatasetLiterals.TEXT_COLUMN] += ". " + df_copy[column_name].map(str)

    return text_df


def _concat_text_and_preserve_label(df: pd.DataFrame, label_column_name: str) -> pd.DataFrame:
    """Concatenates all of the text columns, while keeping the label column intact

    :param df: Dataframe to be converted into required format
    :param label_column_name: Name/title of the label column
    :return: Dataframe in required format
    """
    text_df = concat_text_columns(df, label_column_name)
    if label_column_name not in df.columns:
        return text_df

    labels_df = df[label_column_name].astype(str)
    # Create final dataframe by concatenating text with label dataframe
    final_df = pd.concat([text_df, labels_df], join='outer', axis=1)
    return final_df


def multiclass_dataset_loader(train_df: pd.DataFrame,
                              validation_df: pd.DataFrame,
                              dataset_language: str,
                              label_column_name: str) -> Tuple[PyTorchDataset,
                                                               PyTorchDataset,
                                                               List[Any]]:
    """To get the training_set, validation_set and label_list for multiclass scenario

    :param train_df: Dataframe with training data
    :param validation_df: Dataframe with validation data
    :param dataset_language: language code of dataset
    :param label_column_name: Name/title of the label column
    :return: training dataset, validation dataset, label list
    """
    train_dataframe = _concat_text_and_preserve_label(train_df, label_column_name)
    # Let's sort it for determinism
    label_list = sorted(pd.unique(train_dataframe[label_column_name]))
    validation_set = None
    if validation_df is not None:
        validation_dataframe = _concat_text_and_preserve_label(validation_df, label_column_name)
        label_list_val = pd.unique(validation_dataframe[label_column_name])
        label_list = sorted(set(label_list) | set(label_list_val))
        validation_set = PyTorchMulticlassDatasetWrapper(validation_dataframe, label_list,
                                                         dataset_language, label_column_name)
    training_set = PyTorchMulticlassDatasetWrapper(train_dataframe, label_list,
                                                   dataset_language, label_column_name)
    return training_set, validation_set, label_list


def multilabel_dataset_loader(train_df: pd.DataFrame,
                              validation_df: pd.DataFrame,
                              label_column_name: str) -> Tuple[PyTorchDataset,
                                                               PyTorchDataset,
                                                               int]:
    """To get the training_set, validation_set and num_label_columns for multilabel scenario

    :param train_df: Dataframe with training data
    :param validation_df: Dataframe with validation data
    :param label_column_name: Name/title of the label column
    :return: training dataset, validation dataset, label list
    """
    # Fit a vectorizer on the label column so that we can transform labels column
    vectorizer = get_vectorizer(train_df, validation_df, label_column_name)
    # For multi-label training, label_info refers to num of label columns
    label_info = len(vectorizer.get_feature_names())

    # Convert dataset into the format ingestible be model
    _logger.info("TRAIN Dataset: {}".format(train_df.shape))
    training_set = PyTorchDatasetWrapper(train_df, label_column_name=label_column_name, vectorizer=vectorizer)
    validation_set = None
    if validation_df is not None:
        _logger.info("VALIDATION Dataset: {}".format(validation_df.shape))
        validation_set = PyTorchDatasetWrapper(validation_df,
                                               label_column_name=label_column_name,
                                               vectorizer=vectorizer)
    return training_set, validation_set, label_info, vectorizer


def dataset_loader(dataset_id: str,
                   validation_dataset_id: Union[str, None],
                   label_column_name: str,
                   workspace: Workspace,
                   dataset_language: Optional[str] = 'eng',
                   is_multiclass_training: bool = False) -> Tuple[PyTorchDataset,
                                                                  PyTorchDataset,
                                                                  Union[int, List[Any]]]:
    """To get the training_set, validation_set and label_info for multiclass or multilabel scenarios
    label_info is leveraged by both multi-class and multi-label scenarios, but refers
    to different things for either case. Read comments above to understand.

    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param validation_dataset_id: Unique identifier to fetch validation dataset from datastore
    :param label_column_name: Name/title of the label column
    :param workspace: workspace where dataset is stored in blob
    :param dataset_language: language code of dataset
    :return: training dataset, validation dataset, label info
    """
    # Get Training Dataset object and convert to pandas df
    train_ds = AmlDataset.get_by_id(workspace, dataset_id)
    _logger.info("Type of Dataset is: {}".format(type(train_ds)))
    train_df = train_ds.to_pandas_dataframe()

    # If validation dataset exists, get Validation Dataset object and convert to pandas df
    if validation_dataset_id is not None:
        validation_ds = AmlDataset.get_by_id(workspace, validation_dataset_id)
        _logger.info("Type of Validation Dataset is: {}".format(type(validation_ds)))
        validation_df = validation_ds.to_pandas_dataframe()
    else:
        validation_df = None

    if is_multiclass_training:
        return multiclass_dataset_loader(train_df, validation_df,
                                         dataset_language, label_column_name)
    return multilabel_dataset_loader(train_df, validation_df, label_column_name)
