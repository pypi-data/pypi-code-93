# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 09:31:38 2021

@author: yipeng.song@hotmail.com
"""

# %% required packages
import os
import numpy as np
import pandas as pd
import pandas_profiling as pd_profile
from sklearn import preprocessing
from sklearn import model_selection
from sklearn import decomposition

# %% def a function to read csv and sas7bat data sets
def read_data(path2data, index_col=None):
    """read data given the path and the index column

    Args:
        path2data (str): a path in string format to the data
        index_col (int, optional): the column for index, a common
            value is 0. Defaults to None.

    Raises:
        IOError: when data is not found at path2data
        IOError: when file types is not in ['csv', 'sas7bdat']

    Returns:
        pd.dataframe: a pd dataframe contains X and y
    """
    # check if file exists
    if not os.path.isfile(path2data):
        raise IOError(
            f"Read error: the path2data doesn't point to a data. The specificied path is {path2data}"
        )

    # get the suffix of the data
    data_suffix = os.path.basename(path2data).split(".")[-1]

    # choose the reading method according to the suffix
    if data_suffix == "csv":
        data = pd.read_csv(path2data)
    elif data_suffix == "sas7bdat":
        data = pd.read_sas(path2data)
    else:
        raise IOError("Only .csv and .sas7bdat formats are supported")

    # if the column according to the index_col is the index
    if index_col is not None:
        data_index = data.iloc[:, index_col].to_numpy()
        n_index = len(np.unique(data_index))
        if n_index == len(data_index):
            # set index
            data.index = data.iloc[:, index_col]
            drop_column = data.columns[index_col]
            data.drop(drop_column, axis=1, inplace=True)
        else:
            print(
                "Warning: the index must be unique for all samples.\n"
                "The specified index_col is not used"
            )

    return data


# %% define a function to summarize the data
def summarize_data(data, name, max_sample=1000, minimal=True):
    """summarize the data

    Args:
        data (pd.dataframe): data contains X and y
        name (str): name for the generated report to summarize the data
        max_sample (int, optional): the maximum number of samples for data summary.
            Defaults to 1000.
        minimal (bool, optional): minimal mode in generating the report.
            Defaults to True.

    Returns:
        None: return nothing
    """
    # generate the report
    # make results folder when necessary
    if not os.path.isdir("results"):
        os.mkdir("results")

    # make results/name folder when necessary
    target_path = os.path.join("./results", name)
    if not os.path.isdir(target_path):
        os.mkdir(target_path)

    # path to the report
    path2report = os.path.join(target_path, "summary_report.html")
    if os.path.isfile(path2report):
        print("Report is already exist.\n")
    else:
        # only summarize at most max_sample samples
        profile_report = pd_profile.ProfileReport(
            data.sample(min(max_sample, data.shape[0])), minimal=minimal
        )
        profile_report.to_file(path2report)
    return None


# %% define a fun to split the data
def split_data(X, y, test_size=0.2, random_state=None):
    """split data into training and test set

    Args:
        X (np.ndarray): design matrix
        y (np.ndarray): outcome
        test_size (float, optional): the proportion left for test set.
            Defaults to 0.2. The training data is (1-test_size). The model will be
            selected and fitted on the training data and test data will be used in
            the evaluation. When test_size is close to 0 (<=0.01), K-Fold CV will be
            used to evaluate the selected model.
        random_state (int, optional): seed for randomness control. Defaults to None.

    Returns:
        tuple: X_train, X_test, y_train, y_test
    """
    stratify = None
    if len(pd.value_counts(pd.Series(y))) <= 10:
        stratify = y

    if test_size > 0.01:
        X_train, X_test, y_train, y_test = model_selection.train_test_split(
            X, y, test_size=test_size, stratify=stratify, random_state=random_state
        )
    else:
        X_train = X
        y_train = y
        X_test = None
        y_test = None

    return X_train, X_test, y_train, y_test


# %% def a fun to infer the type of the task
def infer_task(y):
    """infer the task for data analysis

    Args:
        y (np.ndarray): outcome

    Returns:
        str: the task, regression, binary or multiclass classification
    """
    task = "reg"
    n_y_uniques = len(pd.Series(y).value_counts())

    if y.dtype != "object":
        if n_y_uniques <= 5:
            y = pd.Series(y).astype(str).to_numpy()

    if y.dtype == "object":
        task = "binary_clf"
        if n_y_uniques > 2:
            task = "multi_clf"
    return task


# %% define a dict to map abbreviation names to full names
task_names = {
    "reg": "regression problem",
    "binary_clf": "binary classification problem",
    "multi_clf": "multiclass classification problem",
}

# %% def a fun to get the scaler
def get_scaler(scaler_name="standard"):
    """get the scaling or standardization fun

    Args:
        scaler_name (str, optional): the name of the scaler. Defaults to 'standard'.
            Other options include "max_abs", "min_max", "robust"

    Returns:
        function: the specificied scaler
    """
    if scaler_name == "standard":
        scaler = preprocessing.StandardScaler()
    elif scaler_name == "max_abs":
        scaler = preprocessing.MaxAbsScaler()
    elif scaler_name == "min_max":
        scaler = preprocessing.MinMaxScaler()
    elif scaler_name == "robust":
        scaler = preprocessing.RobustScaler()
    else:
        scaler = None
    return scaler


# %% def a fun to get the transformer
def get_decomposer(decomposer_name="pca", n_components=3):
    if decomposer_name == "pca":
        decomposer = decomposition.PCA(n_components)
    elif decomposer_name == "fast_ica":
        decomposer = decomposition.FastICA(n_components)
    elif decomposer_name == "nmf":
        decomposer = decomposition.NMF(n_components)
    elif decomposer_name == "kernel_pca":
        decomposer = decomposition.KernelPCA(n_components, kernel="rbf")
    else:
        decomposer = None
    return decomposer


# %% def a class to hold the results of the trained model
class SavedResults:
    """an class to save the results of selecting and fitting model"""

    def __init__(
        self,
        feature_importance=None,
        selected_hyperparameter=None,
        searching_range=None,
        selected_model=None,
    ):
        self.feature_importances_ = feature_importance
        self.selected_hyperparameters_ = selected_hyperparameter
        self.searching_ranges_ = searching_range
        self.selected_model_ = selected_model
        self.time_ = None
        self.n_jobs = None

    def __repr__(self):
        message = (
            f"{'-' * 75} \n"
            + "The attributes are: \n"
            + "\t .feature_importances_: coefficients or feature importance"
            + "for all the variables.\n"
            + "\t .selected_hyperparameters_: selected hyperparameters.\n"
            + "\t .searching_ranges_: searching ranges for all the hyperparameters\n"
            + "\t .selected_model_: saved selected model\n"
            + "\t .time_: the time used to select and fit the model\n"
            + "The saved model is: \n"
            + f"\t {self.selected_model_} \n"
            + "The time used to select and train the model is: \n"
            + f"\t {self.time_} seconds \n"
            + f"{'-' * 75} \n"
        )

        return message


# %% define a class to hold the preprocessing procedure
class SavedPreprocessing:
    """save the data preprocessing procedure for preprocess future data"""

    def __init__(
        self, kept_variables, cat_variables, num_variables, cat_encoder, imputer
    ):
        self.kept_variables = kept_variables
        self.cat_variables = cat_variables
        self.num_variables = num_variables
        self.cat_encoder = cat_encoder
        self.imputer = imputer

    # using exact the same preprocessing procedures on the test data
    def transform(self, X_test):
        """Apply saved preprocessing steps on new test set

        Args:
            X_test (pd.DataFrame): the test set in the original form as the training data

        Raises:
            TypeError: X_test must be a pandas dataframe
            ValueError: X_test doesn't contain all the variables used in training process

        Returns:
            [np.ndarray]: the preprocessed X_test
        """
        # X_test must be a dataframe
        if type(X_test) != pd.core.frame.DataFrame:
            raise TypeError("X_test must be a pandas dataframe")

        # make sure that the kept variables are all in X_test
        common_variables = intersection(self.kept_variables, X_test.columns)
        if len(common_variables) != len(self.kept_variables):
            raise ValueError("X_test doesn't contain all the variables")

        # index out the variables in the same way as the traning data
        X_test = X_test.loc[:, self.kept_variables]

        # change all categorical variables to string formate
        X_test.loc[:, self.cat_variables] = X_test.loc[:, self.cat_variables].astype(
            str
        )

        # set the infinite elements as nan
        X_test.replace([np.inf, -np.inf], np.nan, inplace=True)

        ## encoding the categorical variables
        # replace the missing values in categorical variables to 'nan'
        X_cat = X_test.loc[:, self.cat_variables]
        X_cat.fillna("nan", inplace=True)
        X_num = X_test.loc[:, self.num_variables]

        # one-hot encoding using saved encoder
        X_cat_dummy = pd.DataFrame(
            data=self.cat_encoder.transform(X_cat),
            index=X_cat.index,
            columns=self.cat_encoder.get_feature_names(self.cat_variables),
        )

        # recombine the cat and num data sets
        X_test = pd.concat([X_num, X_cat_dummy], axis=1)
        self.feature_names_ = X_test.columns
        self.index_ = X_test.index

        ## input missing values
        X_test = self.imputer.transform(X_test)

        return X_test

    def __repr__(self):
        message = (
            f"{'-' * 75} \n"
            + "Introduction: \n"
            + "\t this object contains all the necessary steps to apply the"
            + " saved data preprocessing steps on the new data set. A member function"
            + " '.transform' is used to preprocess new test data.\n"
            + f"{'-' * 75} \n"
            + "Usage: \n"
            + "\t X_test = object.transform(X_test) \n"
            + "\t check help(saved_preprocessing.transform) for more information.\n"
            + f"{'-' * 75} \n"
        )
        return message


# %% some commonly used functions
# def a fun to do intersection
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


# def a fun to do set diff
def setdiff(lst1, lst2):
    lst3 = [value for value in lst1 if value not in lst2]
    return lst3
