# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 13:41:26 2021

@author: yipeng
"""
# %% load into required packages and functions
import time
import numpy as np
import pandas as pd
from sklearn import tree
from sklearn import model_selection
from sklearn import metrics
import imblearn.ensemble as ensemble

# Bayesian optimization related package
import optuna

# utilities functions
from end2endML.utilities import SavedResults

# %% fun to select and fit imbalanced classification models
def train_imbalanced_classification_models(
    X, y, models=["rf", "gb"], cv=10, cv_force=False, n_jobs=10, n_trials=30, verbose=1
):
    """automate select and train classification models

    Args:
        X (np.ndarray): (n, p) design matrix; n, samples; p, variables
        y (np.ndarray): (n, ) outcome; n, samples
        models (list, optional): a list of models to be selected and fitted.
            Defaults to ['gb','rf']. gb, gradient boosting; rf, random forest.
        cv (int, optional): K-Fold cv for model selection. Defaults to 10.
        cv_force (bool, optional): whether to force the model selection to use
            K-Fold CV to evaluate the model. Defaults to False.
        n_trials (int, optional): number of Bayesian Optimization trials. Defaults to 30.
        n_jobs (int, optional): number of cores to be used in model selection. Defaults to 10.
        verbose (int, optional): show log or not. Defaults to 1.

    Returns:
        [dictatory]: key, the model name; value, an object contains selected model, selected
        hyperparameters, searching range. print it to show the attributes of this object.
    """
    # adjust the model names according to the task
    clf_models = []
    if ("rf" not in models) and ("gb" not in models):
        print(
            "Current implemented models for imbalanced classification"
            " only include rf: random forest and gb: gradient boosting."
            " At least rf and random forest, models will be included."
        )
        models.append("rf")
    if "rf" in models:
        clf_models.append("clf_imb_rf")
    if "gb" in models:
        clf_models.append("clf_imb_rus_gb")
        clf_models.append("clf_imb_easy_gb")

    ## fit the models ------------------------------------
    result = {}
    # fit random forest model
    if "clf_imb_rf" in clf_models:
        tic = time.time()
        rf_model = train_imb_random_forest(
            X, y, cv=cv, cv_force=cv_force, n_jobs=n_jobs, n_trials=n_trials, verbose=0
        )
        toc = time.time() - tic
        rf_model.time_ = toc
        rf_model.n_jobs = 10
        result["clf_imb_rf"] = rf_model
        if verbose == 1:
            print(
                f"{round(toc, 4)} seconds taken to select and fit the imbalanced"
                f" random forest model. \n {'-' * 50}"
            )

    # fit RUSBoostClassifier model
    if "clf_imb_rus_gb" in clf_models:
        tic = time.time()
        gb_rus_model = train_gradient_boost_rus(
            X, y, cv=cv, n_jobs=n_jobs, n_trials=n_trials, verbose=0
        )
        toc = time.time() - tic
        gb_rus_model.time_ = toc
        gb_rus_model.n_jobs = None
        result["clf_imb_rus_gb"] = gb_rus_model
        if verbose == 1:
            print(
                f"{round(toc, 4)} seconds taken to select and fit the imbalanced"
                f" RUSBoostClassifier model. \n {'-' * 50}"
            )

    # fit EasyEnsembleClassifier model
    if "clf_imb_easy_gb" in clf_models:
        tic = time.time()
        gb_easy_model = train_gradient_boost_easy(
            X, y, cv=cv, n_jobs=n_jobs, n_trials=n_trials, verbose=0
        )
        toc = time.time() - tic
        gb_easy_model.time_ = toc
        gb_easy_model.n_jobs = 10
        result["clf_imb_easy_gb"] = gb_easy_model
        if verbose == 1:
            print(
                f"{round(toc, 4)} seconds taken to select and fit the imbalanced"
                f" EasyEnsembleClassifier model. \n {'-' * 50}"
            )

    return result


# %% fit to select and fit the random forest model
def train_imb_random_forest(
    X, y, cv=10, cv_force=False, n_jobs=10, n_trials=30, verbose=0
):
    if not cv_force:
        oob_score = True
    else:
        oob_score = False

    # index out the positive label
    values_counts = pd.value_counts(pd.Series(y)).sort_values(ascending=True)
    positive_label = values_counts.index.to_list()[0]

    # random forest model
    rf_model = ensemble.BalancedRandomForestClassifier(
        criterion="entropy", oob_score=oob_score, n_jobs=n_jobs
    )

    def rf_objective(trial):
        # parameter space
        param = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 1500, log=True),
            "max_features": trial.suggest_float("max_features", 0.1, 1.0, step=0.1),
        }

        # using cross validation to evaluate the model's performance on the training set
        rf_model.set_params(**param)
        if oob_score:
            rf_model.fit(X, y)
            val_score = rf_model.oob_score_
        else:
            y_hat = model_selection.cross_val_predict(
                rf_model, X, y, cv=cv, n_jobs=n_jobs
            )
            if len(np.unique(y)) == 2:
                val_score = metrics.f1_score(y, y_hat, pos_label=positive_label)
            else:
                val_score = metrics.f1_score(y, y_hat, average="weighted")
        return val_score

    if verbose == 0:
        optuna.logging.set_verbosity(optuna.logging.WARNING)
    rf_study = optuna.create_study(direction="maximize")
    rf_study.optimize(rf_objective, n_trials=n_trials)

    rf_selected = rf_model
    rf_selected.set_params(**rf_study.best_params)
    rf_selected.fit(X, y)

    # feature importance
    feature_importance = rf_selected.feature_importances_

    # selected hyper parameter
    selected_hyperparameter = rf_study.best_params

    # hyperparameter searching range
    searching_range = {"n_estimators": [50, 1500], "max_features": [0.1, 1.0]}

    # selected model
    selected_model = rf_selected

    # Using a class to save the results
    result = SavedResults(
        feature_importance, selected_hyperparameter, searching_range, selected_model
    )
    return result


# %% fun to select and fit RUSBoostClassifier
def train_gradient_boost_rus(
    X, y, cv=10, cv_force=False, n_jobs=10, n_trials=30, verbose=0
):
    # index out the positive label
    values_counts = pd.value_counts(pd.Series(y)).sort_values(ascending=True)
    positive_label = values_counts.index.to_list()[0]

    # using validation set to select the model
    if not cv_force:
        # split X,y into train and val set using validation error to select model
        # stratified splitting for classification problem
        X_train, X_val, y_train, y_val = model_selection.train_test_split(
            X, y, test_size=0.15, stratify=y
        )

    # Bayesian optimization procedure for model selection
    def gb_objective(trial):
        # parameter space
        n_estimators = trial.suggest_int("n_estimators", 50, 1500, log=True)
        max_depth = trial.suggest_int("max_depth", 1, 15)

        # set up the model
        gb_model = ensemble.RUSBoostClassifier(
            base_estimator=tree.DecisionTreeClassifier(max_depth=max_depth),
            n_estimators=n_estimators,
            learning_rate=0.1,
        )

        # evaluate the model
        if not cv_force:
            gb_model.fit(X_train, y_train)
            y_val_hat = gb_model.predict(X_val)
            if len(np.unique(y)) == 2:
                val_score = metrics.f1_score(y_val, y_val_hat, pos_label=positive_label)
            else:
                val_score = metrics.f1_score(y_val, y_val_hat, average="weighted")
        else:
            y_hat = model_selection.cross_val_predict(
                gb_model, X, y, cv=cv, n_jobs=n_jobs
            )
            if len(np.unique(y)) == 2:
                val_score = metrics.f1_score(y, y_hat, pos_label=positive_label)
            else:
                val_score = metrics.f1_score(y, y_hat, average="weighted")
        return val_score

    if verbose == 0:
        optuna.logging.set_verbosity(optuna.logging.WARNING)
    gb_study = optuna.create_study(direction="maximize")
    gb_study.optimize(gb_objective, n_trials=n_trials)

    # save the selected model
    best_parameters = gb_study.best_params
    gb_selected = ensemble.RUSBoostClassifier(
        base_estimator=tree.DecisionTreeClassifier(
            max_depth=best_parameters["max_depth"]
        ),
        n_estimators=best_parameters["n_estimators"],
        learning_rate=0.1,
    )
    gb_selected.fit(X, y)

    # feature importance
    feature_importance = gb_selected.feature_importances_

    # selected hyper parameter
    selected_hyperparameter = gb_study.best_params

    # hyperparameter searching range
    searching_range = {"n_estimators": [50, 1500], "max_depth": [2, 15]}

    # selected model
    selected_model = gb_selected

    # Using a class to save the results
    result = SavedResults(
        feature_importance, selected_hyperparameter, searching_range, selected_model
    )
    return result


# %% fun to select and fit EasyEnsembleClassifier
def train_gradient_boost_easy(
    X, y, cv=10, cv_force=False, n_jobs=10, n_trials=30, verbose=0
):
    # index out the positive label
    values_counts = pd.value_counts(pd.Series(y)).sort_values(ascending=True)
    positive_label = values_counts.index.to_list()[0]

    # define a base model
    gb_model = ensemble.EasyEnsembleClassifier(n_estimators=10, n_jobs=n_jobs)

    # using validation set to select the model
    if not cv_force:
        # split X,y into train and val set using validation error to select model
        # stratified splitting for classification problem
        X_train, X_val, y_train, y_val = model_selection.train_test_split(
            X, y, test_size=0.15, stratify=y
        )

    # Bayesian optimization for model selection
    def gb_objective(trial):
        # parameter space
        param = {"n_estimators": trial.suggest_int("n_estimators", 5, 50)}

        # set up the model
        gb_model.set_params(**param)
        if not cv_force:
            gb_model.fit(X_train, y_train)
            y_val_hat = gb_model.predict(X_val)
            if len(np.unique(y)) == 2:
                val_score = metrics.f1_score(y_val, y_val_hat, pos_label=positive_label)
            else:
                val_score = metrics.f1_score(y_val, y_val_hat, average="weighted")
        else:
            y_hat = model_selection.cross_val_predict(
                gb_model, X, y, cv=cv, n_jobs=n_jobs
            )
            if len(np.unique(y)) == 2:
                val_score = metrics.f1_score(y, y_hat, pos_label=positive_label)
            else:
                val_score = metrics.f1_score(y, y_hat, average="weighted")
        return val_score

    if verbose == 0:
        optuna.logging.set_verbosity(optuna.logging.WARNING)
    gb_study = optuna.create_study(direction="maximize")
    gb_study.optimize(gb_objective, n_trials=n_trials)

    # save the selected model
    gb_selected = gb_model.set_params(**gb_study.best_params)
    gb_selected.fit(X, y)

    # feature importance
    feature_importance = None

    # selected hyper parameter
    selected_hyperparameter = gb_study.best_params

    # hyperparameter searching range
    searching_range = {"n_estimators": [5, 50]}

    # selected model
    selected_model = gb_selected

    # Using a class to save the results
    result = SavedResults(
        feature_importance, selected_hyperparameter, searching_range, selected_model
    )
    return result
