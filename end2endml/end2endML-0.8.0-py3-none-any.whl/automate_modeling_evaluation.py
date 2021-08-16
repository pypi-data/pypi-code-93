# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 13:41:26 2021

This file includes functions to do automatic modeling and automatic evaluation

@author: yipeng.song@hotmail.com
"""

#%% load required models
import pandas as pd
import numpy as np

# functions from end2endML
import end2endML.utilities as utilities
from end2endML.select_fit_models.classification_models import (
    train_classification_models,
)
from end2endML.select_fit_models.regression_models import train_regression_models
from end2endML.select_fit_models.imbalanced_classification_models import (
    train_imbalanced_classification_models,
)
from end2endML.evaluate_models.classification_metrics import (
    classification_evaluation_test,
)
from end2endML.evaluate_models.classification_metrics import (
    classification_evaluation_cv,
)
from end2endML.evaluate_models.regression_metrics import regression_evaluation_test
from end2endML.evaluate_models.regression_metrics import regression_evaluation_cv

#%% def a fun to do automatic modeling
def automate_modeling(
    X,
    y,
    scaler="standard",
    decomposer=None,
    n_components=None,
    models=["linear", "lasso", "ridge", "elasticNet", "svm", "nn", "gb", "rf"],
    imbalance=False,
    imbalance_force=False,
    cv=10,
    cv_force=False,
    n_trials=30,
    n_jobs=10,
    max_iter=100,
    verbose=1,
):
    """automate modeling and evaluation

    Args:
        X (np.ndarray): (n, p) design matrix; n, samples; p, variables
        y (np.ndarray): (n, ) outcome; n, samples
        scaler (str, optional): scaling method. Defaults to 'standard'. Other
            possibilities include "max_abs", "min_max", "robust". Check the sklearn
            scaler method to find the meaning of different choices.
        decomposer (str, optional): dimension reduction method. Defaults to None. Other
            possibilities include "pca", "fast_ica", "nmf", "kernel_pca" with rbf kernel.
            Check the sklearn decomposition method to find the meaning of different choices.
        n_components (int, optional): the number of components in dimension reduction. Defaults
            to None, which is corresponding to int(0.5 * min(X.shape)).
        models (list, optional): a list of models to be selected and fitted.
            Defaults to ['linear', 'lasso', 'ridge', 'elasticNet', 'svm', 'nn', 'gb','rf'].
            linear, standard linear model; lasso, linear model with lasso penalty; ridge,
            linear model with ridge penalty; elasticNet, linear model with ElasticNet penalty;
            svm, support vector machine; nn, neural network; gb, gradient boosting; rf,
            random forest.
        imbalance (bool, optional): whether to do imbalance classification. Defaults to False.
        imbalance_force (bool, optional): force to choose the imbalanced classification mdoels.
            imbalanced classification models include balanced random forest, RUSBoostClassifier,
            and EasyEnsembleClassifier. Defaults to False.
        cv (int, optional): K-Fold cv for model selection. Defaults to 10.
        cv_force (bool, optional): whether to force the model selection to use
            K-Fold CV to evaluate the model. Defaults to False.
        n_trials (int, optional): number of Bayesian Optimization trials. Defaults to 30.
        n_jobs (int, optional): number of cores to be used in model selection. Defaults to 10.
        max_iter (int, optional): maximum iterations for some models. Defaults to 100.
        verbose (int, optional): show log or not. Defaults to 1.

    Returns:
        [dictatory]: key, the model name; value, an object contains selected model, selected
        hyperparameters, searching range. print it to show the attributes of this object.
    """
    # check what kind of task it is
    task = utilities.infer_task(y)
    task_name = utilities.task_names[task]
    if verbose == 1:
        print(f"The current task is a {task_name} \n {'-' * 50}")

    ## dispath the modeling according to the task
    if task == "reg":
        # regression task
        results = train_regression_models(
            X,
            y,
            scaler=scaler,
            decomposer=decomposer,
            n_components=n_components,
            models=models,
            cv=cv,
            cv_force=cv_force,
            n_jobs=n_jobs,
            n_trials=n_trials,
            max_iter=max_iter,
            verbose=verbose,
        )
    else:
        # classification task
        y_uniques = len(np.unique(y))
        if y_uniques > 10:
            print(
                f"There are {y_uniques} levels in the outcome,"
                " you may need to see if you really want to model"
                " it as outcome in a classification problem."
            )

        # get the frequency of the different classes
        class_freqs = pd.Series(y).value_counts() / len(y)
        imbalanceness = class_freqs.max() / class_freqs.min()

        # imbalanced classification
        if imbalance_force or ((imbalanceness > 10) and imbalance):
            # imbalanced classification
            results = train_imbalanced_classification_models(
                X,
                y,
                models=models,
                cv=cv,
                cv_force=cv_force,
                n_jobs=n_jobs,
                n_trials=n_trials,
                verbose=verbose,
            )
        else:
            if imbalanceness > 10:
                print(
                    "The ratio of majority divides the minority is larger than 10,"
                    " maybe it is better to use imbalanced classification, check the"
                    " imbalance parameter in the function to learn more about it."
                )

            # balanced classification
            results = train_classification_models(
                X,
                y,
                scaler=scaler,
                decomposer=decomposer,
                n_components=n_components,
                models=models,
                cv=cv,
                cv_force=cv_force,
                n_jobs=n_jobs,
                n_trials=n_trials,
                max_iter=max_iter,
                verbose=verbose,
            )

    return results


# %% define a fun to do automatic evaluation
def automate_evaluation(
    results,
    X_test,
    y_test,
    X,
    y,
    eval_test=True,
    eval_cv=True,
    cv=10,
    n_jobs=10,
):
    """automatically evaluate the selected and fitted models

    Args:
        results (dict): key, model_name; value, saved model and model selection process
        X_test (np.ndarray): test set X
        y_test (np.ndarray): test set y
        X (np.ndarray): X
        y (np.ndarray): y
        eval_test (bool, optional): whether to evaluate the selected models on test set.
            Defaults to True.
        eval_cv (bool, optional): whether to evaluate the selected models using K-Fold CV.
            Defaults to True.
        cv (int, optional): K-Fold CV. Defaults to 10.
        n_jobs (int, optional): number of cores to be used. Defaults to 10.

    Returns:
        pd.ndarray: results of evaluating the saved models.
    """
    # get the name of one of the saved models
    model_name = list(results.keys())[0]

    # it is classification problem or regression problem
    if "clf_" in model_name:
        task = "clf"
    elif "reg_" in model_name:
        task = "reg"

    # if X_test is None, eval_cv has to be True
    if X_test is None:
        eval_cv = True

    # test performance
    if eval_test and task == "clf":
        models_metrics_test = classification_evaluation_test(results, X_test, y_test)
    if eval_test and task == "reg":
        models_metrics_test = regression_evaluation_test(results, X_test, y_test)

    # K-fold CV performance
    if eval_cv and task == "clf":
        models_metrics_cv = classification_evaluation_cv(
            results, X, y, cv=cv, n_jobs=n_jobs
        )
    if eval_cv and task == "reg":
        models_metrics_cv = regression_evaluation_cv(
            results, X, y, cv=cv, n_jobs=n_jobs
        )

    # save the metrics
    if eval_test and eval_cv:
        models_metrics = models_metrics = pd.concat(
            [models_metrics_test, models_metrics_cv], axis=0
        )
    elif eval_test and (not eval_cv):
        models_metrics = models_metrics_test
    elif (not eval_test) and eval_cv:
        models_metrics = models_metrics_cv

    return models_metrics