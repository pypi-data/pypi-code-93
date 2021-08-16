# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 13:41:26 2021

@author: yipeng
"""
# %% load into required packages and functions
from sklearn import metrics
import pandas as pd
from sklearn import model_selection

# %% Regression evaluation: test set performance
def regression_evaluation_test(results, X_test, y_test):
    """Evaluate the models' performance on the test set.

    Args:
        results (dict): key, model name; value, saved models and model selection.
        X_test (np.ndarray): test set X
        y_test (np.ndarray): test set y

    Returns:
        pd.dataframe: multiple performance metrics for all the saved models.
    """
    # extract the keys in the dict of the results
    model_names = list(results.keys())

    # get the metrics on the test set for all the selected models
    models_metrics_test = {}
    for key in model_names:
        selected_model = results[key].selected_model_
        models_metrics_test[key] = regression_evaluation_test_(
            selected_model, X_test, y_test
        )
    # generate the model evaluation metrics
    models_metrics_test = pd.DataFrame(models_metrics_test)
    models_metrics_test.index = [ele + "_test" for ele in models_metrics_test.index]
    return models_metrics_test


# %% Regression evaluation: K-Fold CV performance
def regression_evaluation_cv(results, X, y, cv=10, n_jobs=10):
    """evaluate the selected models' performance using K-Fold CV

    Args:
        results (dict): key, model name; value, saved models and model selection.
        X (np.ndarray): X
        y (np.ndarray): y
        cv (int, optional): K-Fold CV. Defaults to 10.
        n_jobs (int, optional): number of cores to be used. Defaults to 10.

    Returns:
        pd.dataframe: multiple performance metrics for all the saved models.
    """
    # extract the keys in the dict of the results
    model_names = list(results.keys())

    # get the metrics on all the data using K-Fold CV for the models
    models_metrics_cv = {}
    for key in model_names:
        selected_model = results[key].selected_model_
        models_metrics_cv[key] = regression_evaluation_cv_(
            selected_model, X, y, cv=cv, n_jobs=n_jobs
        )

    # generate the model evaluation metrics
    models_metrics_cv = pd.DataFrame(models_metrics_cv)
    models_metrics_cv.index = [ele + "_cv" for ele in models_metrics_cv.index]
    return models_metrics_cv


# %% model evaluation performance of a selected model
def regression_evaluation_test_(selected_model, X_test, y_test):
    # predicted vs. actually outcome
    y_true = y_test
    y_hat = selected_model.predict(X_test)

    model_metrics = regression_evaluation_base_(y_true, y_hat)
    return model_metrics


def regression_evaluation_cv_(selected_model, X, y, cv=10, n_jobs=10):
    # predicted vs. actually outcome
    y_true = y
    y_hat = model_selection.cross_val_predict(
        selected_model, X, y, cv=cv, n_jobs=n_jobs
    )

    model_metrics = regression_evaluation_base_(y_true, y_hat)
    return model_metrics


# %% base evaluator
def regression_evaluation_base_(y_true, y_hat):
    # R2 score
    R2_score = metrics.r2_score(y_true, y_hat)

    # MSE
    MSE_error = metrics.mean_squared_error(y_true, y_hat)

    # MAE
    MAE_error = metrics.mean_absolute_error(y_true, y_hat)

    # metrics
    model_metrics = pd.Series(
        [R2_score, MSE_error, MAE_error], index=["R2", "MSE", "MAE"]
    )
    return model_metrics
