# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 13:41:26 2021

This file contains the functions to automate evaluate the classification models

@author: yipeng.song@hotmail.com
"""
# %% load into required packages
from sklearn import metrics
import pandas as pd
import numpy as np
import imblearn
from sklearn import model_selection

# when necessary, suppress the warnings, mainly for testing
from warnings import simplefilter
from sklearn.exceptions import ConvergenceWarning

# %% binary classification: test set evaluation
def classification_evaluation_test(results, X_test, y_test):
    """evaluate the selected models' performance on the test set

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
        models_metrics_test[key] = classification_evaluation_test_(
            selected_model, X_test, y_test
        )

    # generate the model evaluation metrics
    models_metrics_test = pd.DataFrame(models_metrics_test)
    models_metrics_test.index = [ele + "_test" for ele in models_metrics_test.index]
    return models_metrics_test


# %% binary classification: K-Fold CV evaluation
def classification_evaluation_cv(results, X, y, cv=10, n_jobs=10):
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
        models_metrics_cv[key] = classification_evaluation_cv_(
            selected_model, X, y, cv=cv, n_jobs=n_jobs
        )

    # generate the model evaluation metrics
    models_metrics_cv = pd.DataFrame(models_metrics_cv)
    models_metrics_cv.index = [ele + "_cv" for ele in models_metrics_cv.index]
    return models_metrics_cv


# %% classification evaluation for a single model: test set
def classification_evaluation_test_(selected_model, X_test, y_test):
    # check if it is binary or multiclass
    task = "binary"
    if len(np.unique(y_test)) > 2:
        task = "multiclass"

    # y_true, y_hat, y_hat_prob
    y_true = y_test
    y_hat = selected_model.predict(X_test)
    y_hat_prob = None
    if hasattr(selected_model, "predict_proba"):
        if len(np.unique(y_test)) > 2:
            y_hat_prob = selected_model.predict_proba(X_test)
        else:
            y_hat_prob = selected_model.predict_proba(X_test)[:, 1]

    # check if it is the output of grandint boosting model
    if hasattr(selected_model, "label_encoder_"):
        label_encoder = selected_model.label_encoder_
        y_hat = label_encoder.inverse_transform(y_hat)

    # metrics on the test set
    if task == "binary":
        model_metrics = binary_evaluation_base_(y_true, y_hat, y_hat_prob)
    elif task == "multiclass":
        model_metrics = multiclass_evaluation_base_(y_true, y_hat, y_hat_prob)

    return model_metrics


# %% classification evaluation for a single model: K-Fold CV
def classification_evaluation_cv_(selected_model, X, y, cv=10, n_jobs=10):
    # check it is binary or multiclass
    task = "binary"
    if len(np.unique(y)) > 2:
        task = "multiclass"

    # y_true, y_hat, y_hat_prob
    y_true = y
    if hasattr(selected_model, "label_encoder_"):
        label_encoder = selected_model.label_encoder_
        y_trans = label_encoder.transform(y)
        y_hat = model_selection.cross_val_predict(
            selected_model, X, y_trans, cv=cv, n_jobs=n_jobs, method="predict"
        )
        y_hat = label_encoder.inverse_transform(y_hat)
    else:
        y_hat = model_selection.cross_val_predict(
            selected_model, X, y, cv=cv, n_jobs=n_jobs, method="predict"
        )

    y_hat_prob = None
    if hasattr(selected_model, "predict_proba"):
        if len(np.unique(y)) > 2:
            y_hat_prob = model_selection.cross_val_predict(
                selected_model, X, y, cv=cv, n_jobs=n_jobs, method="predict_proba"
            )
        else:
            y_hat_prob = model_selection.cross_val_predict(
                selected_model, X, y, cv=cv, n_jobs=n_jobs, method="predict_proba"
            )[:, 1]

    # metrics on the test set
    if task == "binary":
        model_metrics = binary_evaluation_base_(y_true, y_hat, y_hat_prob)
    elif task == "multiclass":
        model_metrics = multiclass_evaluation_base_(y_true, y_hat, y_hat_prob)

    return model_metrics


# %% base evaluators
def binary_evaluation_base_(y_true, y_hat, y_hat_prob):
    """Part of the codes in this fun is from Dan"""
    # confusion matrix
    CM = metrics.confusion_matrix(y_true, y_hat)
    TN = CM[0][0]
    FN = CM[1][0]
    TP = CM[1][1]
    FP = CM[0][1]

    # multiple evaluation metrics
    sensitivity = TP / (TP + FN)
    specificity = TN / (TN + FP)
    balanced_accuracy = (TP / (TP + FN) + TN / (TN + FP)) / 2
    recall = sensitivity
    precision = TP / (TP + FP)
    f1_score = 2 * TP / (2 * TP + FP + FN)

    AUC = np.nan
    if y_hat_prob is not None:
        AUC = metrics.roc_auc_score(y_true, y_hat_prob)

    # metrics
    model_metrics = pd.Series(
        [sensitivity, specificity, balanced_accuracy, recall, precision, f1_score, AUC],
        index=[
            "sensitivity",
            "specificity",
            "balanced_accuracy",
            "recall",
            "precision",
            "f1_score",
            "AUC",
        ],
    )

    return model_metrics


def multiclass_evaluation_base_(y_true, y_hat, y_hat_prob):
    # sensitivity
    sensitivity = imblearn.metrics.sensitivity_score(y_true, y_hat, average="weighted")
    specificity = imblearn.metrics.specificity_score(y_true, y_hat, average="weighted")
    balanced_accuracy = metrics.balanced_accuracy_score(y_true, y_hat)
    recall = sensitivity
    precision = metrics.precision_score(y_true, y_hat, average="weighted")
    f1_score = metrics.f1_score(y_true, y_hat, average="weighted")

    AUC = np.nan
    if y_hat_prob is not None:
        AUC = metrics.roc_auc_score(
            y_true, y_hat_prob, average="weighted", multi_class="ovr"
        )
    # metrics
    model_metrics = pd.Series(
        [sensitivity, specificity, balanced_accuracy, recall, precision, f1_score, AUC],
        index=[
            "sensitivity",
            "specificity",
            "balanced_accuracy",
            "recall",
            "precision",
            "f1_score",
            "AUC",
        ],
    )

    return model_metrics
