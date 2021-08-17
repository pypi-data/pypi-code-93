# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 13:45:41 2021

This files include functions to do automatic data preprocessing

@author: yipeng.song@hotmail.com
"""
import os
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from end2endML import utilities

# %% a fun to do data preprocessing
def data_preprocessing(
    data,
    outcome,
    name,
    cat_levels_threshold=15,
    missing_threshold=0.5,
    for_future_test=False,
    verbose=1,
    save_results=True,
):
    """A simple automate data preprocessing step

    Args:
        data (pd.dataframe): Contains both the design matrix and outcome.
        outcome (str): the name of the outcome.
        name (str): The name of the data set for saving the data.
        cat_levels_threshold (int, optional): When the unique values of
            a column is less than this value, will take it as a categorical
            variable. Defaults to 15.
        missing_threshold (float, optional): [0, 1], When the propotation
            of missing values larger than this value, remove the corresponding
            rows and columns. Defaults to 0.5.
        for_future_test (bool, optional): If the saved preprocessing is going
            to be used to preprocess the future test data, it is better set it
            as True. This argument is mainly about how to do one-hot encoding.
            When it is True, the first level will not be dropped and unknown class
            in the test set will be ignored. Default False.
        verbose (int, optional): whether to show log information.
            Defaults to 1. 1: show information; 0: not show information.
        save_results (bool, optional): whether to save the parameters, which
            will be useful to preprocess new data sets. Defaults to True.

    Raises:
        NameError: The outcome is not found in the data.

    Returns:
        X (np.ndarray): Design matrix.
        y (np.ndarray): outcome.
        feature_names (list of str): The names of the feature variables.
        sample_index (list of str): The row index of X and y in original data.
        saved_preprocess_steps (an object of self defined class): the saved
            preprocess steps for the preprocessing of future test set.
    """
    if outcome not in data.columns:
        raise NameError("the outcome is not found in the data")

    # rm the subjects with NAs in the y
    NAs = ["NA", "Null", "NULL", "NAN", "na", "NaN", "nan"]
    y = data.loc[:, outcome]
    na_idx = [ele in NAs for ele in y]
    if np.array(na_idx).sum() > 0:
        y[na_idx] = np.nan
        kept_idx = np.logical_not(pd.isnull(y))
        data = data.loc[kept_idx, :]

    ## identify all the categorical variables
    # change all the features with less than cat_levels_threshould unique
    # values to be categorical
    unique_values = data.apply(lambda x: len(pd.value_counts(x)), axis=0)
    category_cols = unique_values < cat_levels_threshold
    data.loc[:, category_cols] = data.loc[:, category_cols].astype(str)

    ## rm cols contains text data
    # the cols with type object and unique_values >= 15
    data_types = data.dtypes
    potential_text_cols = unique_values >= 15
    text_cols = np.logical_and(data_types == "object", potential_text_cols)
    text_cols_names = data.columns[text_cols].to_list()
    if len(text_cols_names) > 0:
        if verbose == 1:
            print("An example of the dropped text data is: ")
            print(data.sample(5).loc[:, text_cols_names])
        data.drop(text_cols_names, axis=1, inplace=True)

    ## rm the cols and rows contains more than 50% NAs
    # set the infinite elements as nan
    data.replace([np.inf, -np.inf], np.nan, inplace=True)

    # rm the cols and rows with a lot NAs
    data_NAs = pd.isnull(data)
    col_idx = data_NAs.sum(axis=0) < missing_threshold * data.shape[0]
    row_idx = data_NAs.sum(axis=1) < missing_threshold * data.shape[1]
    data = data.loc[row_idx, col_idx]
    if verbose == 1:
        print(
            "{} rows and {} cols are removed due to NAs".format(
                (1 - row_idx).sum(), (1 - col_idx).sum()
            )
        )

    ## split data into X and y
    y = data.loc[:, outcome]
    X = data.drop(outcome, axis=1)

    # remove all the rows with NAs in y
    kept_idx = np.logical_not(pd.isnull(y))
    X = X.loc[kept_idx, :]
    y = y[kept_idx]

    # rm colum with only a single unique value
    unique_values = X.apply(lambda x: len(pd.value_counts(x)), axis=0)
    X = X.loc[:, unique_values > 1]

    ## encoding the categorical variables
    kept_variables = X.columns
    var_dtypes = X.dtypes
    cat_variables = kept_variables[var_dtypes == "object"]
    num_variables = kept_variables[var_dtypes != "object"]

    # replace the missing values in categorical variables to 'missing'
    X_cat = X.loc[:, cat_variables]
    X_cat.fillna("nan", inplace=True)
    X_num = X.loc[:, num_variables]

    # one-hot encoding and record the transformers
    if for_future_test:
        cat_encoder = OneHotEncoder(drop=None, sparse=False, handle_unknown="ignore")
    else:
        cat_encoder = OneHotEncoder(drop="first", sparse=False, handle_unknown="error")
    cat_encoder.fit(X_cat)
    X_cat_dummy = pd.DataFrame(
        data=cat_encoder.transform(X_cat),
        index=X_cat.index,
        columns=cat_encoder.get_feature_names(cat_variables),
    )

    # recombine the cat and num data sets
    X = pd.concat([X_num, X_cat_dummy], axis=1)
    feature_names = X.columns
    sample_index = X.index.to_list()

    # input missing values
    imputer = SimpleImputer(strategy="median")
    imputer.fit(X)
    X = imputer.transform(X)

    # transform y to np array
    if type(y) == pd.core.series.Series:
        y = y.to_numpy()

    # check the document of np.savez_compressed to see how to load the saved data
    if save_results:
        # path to the report
        target_path = os.path.join("./results", name)
        path2data = os.path.join(target_path, "data.npz")
        np.savez_compressed(
            path2data,
            X=X,
            y=y,
            feature_names=feature_names,  # features names
            sample_index=sample_index,  # index of samples
        )

    # save the preprocessing procedure
    saved_preprocess_steps = utilities.SavedPreprocessing(
        kept_variables=kept_variables,
        cat_variables=cat_variables,
        num_variables=num_variables,
        cat_encoder=cat_encoder,
        imputer=imputer,
    )

    return X, y, feature_names, sample_index, saved_preprocess_steps
