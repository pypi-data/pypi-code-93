# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 13:41:26 2021

@author: yipeng
"""

# %% load into required packages and functions
import time
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn import linear_model
from sklearn import model_selection
from sklearn import metrics
from sklearn import ensemble
from sklearn import svm
from sklearn import neural_network as nn

# gradient boosting model
from xgboost import XGBRegressor

# Bayesian optimization related package
import optuna

# utilities functions
from end2endML.utilities import get_scaler
from end2endML.utilities import get_decomposer
from end2endML.utilities import SavedResults

# when necessary, suppress the warnings, mainly for testing
from warnings import simplefilter
from sklearn.exceptions import ConvergenceWarning

# %% fun to select and fit linear, gradient boosting and random forest
def train_regression_models(
    X,
    y,
    scaler="standard",
    decomposer=None,
    n_components=None,
    models=["linear", "lasso", "ridge", "elasticNet", "svm", "nn", "gb", "rf"],
    cv=10,
    cv_force=False,
    n_jobs=10,
    n_trials=30,
    max_iter=100,
    verbose=1,
):
    """automate select and train regression models

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
        cv (int, optional): K-Fold cv for model selection. Defaults to 10.
        cv_force (bool, optional): whether to force the model selection to use
            K-Fold CV to evaluate the model. Defaults to False.
        n_trials (int, optional): number of Bayesian Optimization trials. Defaults to 30.
        n_jobs (int, optional): number of cores to be used in model selection. Defaults to 10.
        max_iter (int, optional): maximum iterations for some models. Defaults to 1000.
        verbose (int, optional): show log or not. Defaults to 1.

    Returns:
        [dictatory]: key, the model name; value, an object contains selected model, selected
        hyperparameters, searching range. print it to show the attributes of this object.
    """
    # suppress the warnings when necessary
    if verbose == 0:
        simplefilter("ignore", category=ConvergenceWarning)

    # get the scaler
    scaler = get_scaler(scaler_name=scaler)

    # get the decomposer
    if n_components is None:
        n_components = int(0.5 * min(X.shape))
    decomposer = get_decomposer(decomposer_name=decomposer, n_components=n_components)

    # adjust the model names according to the task
    reg_models = ["reg_" + ele for ele in models]

    ## fit the models ------------------------------------
    result = {}

    # linear regression without penalty
    if "reg_linear" in reg_models:
        tic = time.time()
        reg_linear_model = train_linear(X, y, scaler=scaler, decomposer=decomposer)
        toc = time.time() - tic
        reg_linear_model.time_ = toc
        result["reg_linear"] = reg_linear_model
        if verbose == 1:
            print(
                f"{round(toc, 4)} seconds taken to select and fit the linear model. \n {'-' * 50}"
            )

    # fit linear regression model with lasso penalty
    if "reg_lasso" in reg_models:
        tic = time.time()
        lasso_model = train_linear_lasso(
            X,
            y,
            scaler=scaler,
            decomposer=decomposer,
            cv=cv,
            n_jobs=n_jobs,
            max_iter=max_iter,
        )
        toc = time.time() - tic
        lasso_model.time_ = toc
        result["reg_lasso"] = lasso_model
        if verbose == 1:
            print(
                f"{round(toc, 4)} seconds taken to select and fit the linear model with"
                f" lasso penalty. \n {'-' * 50}"
            )

    # fit linear regression model with ridge penalty
    if "reg_ridge" in reg_models:
        tic = time.time()
        ridge_model = train_linear_ridge(
            X, y, scaler=scaler, decomposer=decomposer, cv=cv
        )
        toc = time.time() - tic
        ridge_model.time_ = toc
        result["reg_ridge"] = ridge_model
        if verbose == 1:
            print(
                f"{round(toc, 4)} seconds taken to select and fit the linear model"
                f" with ridge penalty. \n {'-' * 50}"
            )

    # fit linear regression model with elastic net penalty
    if "reg_elasticNet" in reg_models:
        tic = time.time()
        elasticNet_model = train_linear_elasticNet(
            X,
            y,
            scaler=scaler,
            decomposer=decomposer,
            cv=cv,
            n_jobs=n_jobs,
            max_iter=max_iter,
        )
        toc = time.time() - tic
        elasticNet_model.time_ = toc
        result["reg_elasticNet"] = elasticNet_model
        if verbose == 1:
            print(
                f"{round(toc, 4)} seconds taken to select and fit the linear model"
                f" with elasticnet penalty. \n {'-' * 50}"
            )

    # fit a svm model
    if "reg_svm" in reg_models:
        tic = time.time()
        svm_model = train_svm(
            X,
            y,
            scaler=scaler,
            decomposer=decomposer,
            cv=cv,
            n_jobs=n_jobs,
            n_trials=n_trials,
            verbose=0,
        )
        toc = time.time() - tic
        svm_model.time_ = toc
        result["reg_svm"] = svm_model
        if verbose == 1:
            print(
                f"{round(toc, 4)} seconds taken to select and fit the svm model. \n {'-' * 50}"
            )

    # fit nn model
    if "reg_nn" in reg_models:
        tic = time.time()
        nn_model = train_nn(
            X,
            y,
            scaler=scaler,
            decomposer=decomposer,
            cv=cv,
            cv_force=cv_force,
            n_jobs=n_jobs,
            n_trials=n_trials,
            verbose=0,
            max_iter=max_iter,
        )
        toc = time.time() - tic
        nn_model.time_ = toc
        result["reg_nn"] = nn_model
        if verbose == 1:
            print(
                f"{round(toc, 4)} seconds taken to select and fit the neural network model. \n {'-' * 50}"
            )
    # fit gradient boosting model
    if "reg_gb" in reg_models:
        tic = time.time()
        gb_model = train_gradient_boost(
            X, y, cv=cv, cv_force=cv_force, n_jobs=n_jobs, n_trials=n_trials, verbose=0
        )
        toc = time.time() - tic
        gb_model.time_ = toc
        gb_model.n_jobs = n_jobs
        result["reg_gb"] = gb_model
        if verbose == 1:
            print(
                f"{round(toc, 4)} seconds taken to select and fit the gradient boosting model. \n {'-' * 50}"
            )

    # fit random forest model
    if "reg_rf" in reg_models:
        tic = time.time()
        rf_model = train_random_forest(
            X, y, cv=cv, cv_force=cv_force, n_jobs=n_jobs, n_trials=n_trials, verbose=0
        )
        toc = time.time() - tic
        rf_model.time_ = toc
        rf_model.n_Jobs = n_jobs
        result["reg_rf"] = rf_model
        if verbose == 1:
            print(
                f"{round(toc, 4)} seconds taken to select and fit the random forest model are done. \n {'-' * 50}"
            )

    return result


# %% fun to select and fit a linear regression model
def train_linear(X, y, scaler, decomposer):
    # linear regression model
    linearModel = Pipeline(
        [
            ("scaler", scaler),
            ("decomposer", decomposer),
            ("model", linear_model.LinearRegression()),
        ]
    )

    # fit the model selection process
    linearModel.fit(X, y)

    # feature importance
    feature_importance = linearModel["model"].coef_

    # selected hyper parameter
    selected_hyperparameter = None

    # hyperparameter searching range
    searching_range = None

    # selected model
    selected_model = linearModel

    # Using a class to save the results
    result = SavedResults(
        feature_importance, selected_hyperparameter, searching_range, selected_model
    )

    return result


# %% fun to select and fit linear regression with lasso penalty
def train_linear_lasso(X, y, scaler, decomposer, cv=10, n_jobs=10, max_iter=1000):
    # lasso
    lassoCV = Pipeline(
        [
            ("scaler", scaler),
            ("decomposer", decomposer),
            ("model", linear_model.LassoCV(cv=cv, max_iter=max_iter, n_jobs=n_jobs)),
        ]
    )

    # fit the model selection process
    lassoCV.fit(X, y)

    # create a clean model
    selected_model = Pipeline(
        [
            ("scaler", scaler),
            ("decomposer", decomposer),
            (
                "model",
                linear_model.Lasso(alpha=lassoCV["model"].alpha_, max_iter=max_iter),
            ),
        ]
    )
    selected_model.fit(X, y)

    # feature importance
    feature_importance = selected_model["model"].coef_

    # selected hyper parameter
    selected_hyperparameter = lassoCV["model"].alpha_

    # hyperparameter searching range
    searching_range = lassoCV["model"].alphas_

    # Using a class to save the results
    result = SavedResults(
        feature_importance, selected_hyperparameter, searching_range, selected_model
    )

    return result


# %% fun to select and fit linear regression with lasso penalty
def train_linear_ridge(X, y, scaler, decomposer, cv=10):
    # ridge
    if cv == len(y):
        cv = None  # using default generalized leave one out CV
    ridgeCV = Pipeline(
        [
            ("scaler", scaler),
            ("decomposer", decomposer),
            ("model", linear_model.RidgeCV(alphas=np.logspace(-4, 4, 100), cv=cv)),
        ]
    )

    # fit the model selection process
    ridgeCV.fit(X=X, y=y)

    # create a clean model
    selected_model = Pipeline(
        [
            ("scaler", scaler),
            ("decomposer", decomposer),
            ("model", linear_model.Ridge(alpha=ridgeCV["model"].alpha_)),
        ]
    )
    selected_model.fit(X, y)

    # feature importance
    feature_importance = selected_model["model"].coef_

    # selected hyper parameter
    selected_hyperparameter = ridgeCV["model"].alpha_

    # hyperparameter searching range
    searching_range = np.logspace(-4, 4, 100)

    # Using a class to save the results
    result = SavedResults(
        feature_importance, selected_hyperparameter, searching_range, selected_model
    )

    return result


# %% fun to select and fit linear regression with elasticNet penalty
def train_linear_elasticNet(X, y, scaler, decomposer, cv=10, n_jobs=10, max_iter=1000):
    # elasticNet
    l1_ratios_ = [0.01, 0.1, 0.25, 0.5, 0.7, 0.9, 0.95, 0.99, 1]
    elasticNetCV = Pipeline(
        [
            ("scaler", scaler),
            ("decomposer", decomposer),
            (
                "model",
                linear_model.ElasticNetCV(
                    l1_ratio=l1_ratios_, cv=cv, n_jobs=n_jobs, max_iter=max_iter
                ),
            ),
        ]
    )

    # fit the model selection process
    elasticNetCV.fit(X, y)

    # create a clean model
    selected_model = Pipeline(
        [
            ("scaler", scaler),
            ("decomposer", decomposer),
            (
                "model",
                linear_model.ElasticNet(
                    alpha=elasticNetCV["model"].alpha_,
                    l1_ratio=elasticNetCV["model"].l1_ratio_,
                    max_iter=max_iter,
                ),
            ),
        ]
    )
    selected_model.fit(X, y)

    # feature importance
    feature_importance = selected_model["model"].coef_

    # selected hyper parameter
    selected_hyperparameter = {
        "alpha_": elasticNetCV["model"].alpha_,
        "l1_ratio_": elasticNetCV["model"].l1_ratio_,
    }

    # hyperparameter searching range
    searching_range = {"l1_ratios_": l1_ratios_}

    # Using a class to save the results
    result = SavedResults(
        feature_importance, selected_hyperparameter, searching_range, selected_model
    )

    return result


# %% fun to select and fit svm model
def train_svm(
    X,
    y,
    scaler,
    decomposer,
    cv=10,
    n_jobs=10,
    n_trials=30,
    scoring="neg_mean_squared_error",
    verbose=0,
):
    # def a base model: svm model
    svm_model = Pipeline(
        [
            ("scaler", scaler),
            ("decomposer", decomposer),
            ("model", svm.SVR(gamma="scale")),
        ]
    )

    # define the Bayesian optimization process
    def svm_objective(trial):
        # parameter space
        param = {
            "model__C": trial.suggest_loguniform("model__C", 1e-6, 1e2),
            "model__kernel": trial.suggest_categorical(
                "model__kernel", ["linear", "rbf"]
            ),
        }
        # K-Fold CV
        svm_model.set_params(**param)
        cv_scores = model_selection.cross_val_score(
            svm_model, X, y, cv=cv, n_jobs=n_jobs, scoring=scoring
        )
        return cv_scores.mean()

    if verbose == 0:
        optuna.logging.set_verbosity(optuna.logging.WARNING)
    svm_study = optuna.create_study(direction="maximize")
    svm_study.optimize(svm_objective, n_trials=n_trials)

    # save the selected model
    svm_selected = svm_model
    svm_selected.set_params(**svm_study.best_params)
    svm_selected.fit(X, y)

    # feature importance
    feature_importance = None
    if hasattr(svm_selected, "coef_"):
        feature_importance = svm_selected.coef_

    # selected hyper parameter
    selected_hyperparameter = svm_study.best_params

    # hyperparameter searching range
    searching_range = {
        "model__C": "loguniform: [1e-6, 1e2]",
        "model__kernel": ["linear", "rbf"],
    }

    # selected model
    selected_model = svm_selected

    # Using a class to save the results
    result = SavedResults(
        feature_importance, selected_hyperparameter, searching_range, selected_model
    )
    return result


# %% fun to select and fit nn model
def train_nn(
    X,
    y,
    scaler,
    decomposer,
    cv=10,
    cv_force=False,
    n_jobs=10,
    n_trials=30,
    verbose=0,
    max_iter=1000,
):

    if not cv_force:
        # split X,y into train and val set using validation error to select model
        # stratified splitting for classification problem
        X_train, X_val, y_train, y_val = model_selection.train_test_split(
            X, y, test_size=0.15
        )

    # define the Bayesian optimization process
    def nn_objective(trial):
        # parameter space
        learning_rate_init = trial.suggest_loguniform("learning_rate_init", 1e-4, 1e-2)

        # specify the hidden layers
        n_layers = trial.suggest_int("n_units_layers", 1, 5)  # hidden layers
        layers = []
        for i in range(n_layers):
            # number of units
            n_units = trial.suggest_int("n_units_layer_{}".format(i), 4, 256, log=True)
            layers.append(n_units)
        hidden_layer_sizes = tuple(layers)
        alpha = trial.suggest_loguniform("alpha", 1e-8, 1e0)
        learning_rate = trial.suggest_categorical(
            "learning_rate", ["constant", "invscaling"]
        )
        # the specific parameters
        nn_model = Pipeline(
            [
                ("scaler", scaler),
                ("decomposer", decomposer),
                (
                    "model",
                    nn.MLPRegressor(
                        hidden_layer_sizes=hidden_layer_sizes,
                        alpha=alpha,
                        max_iter=max_iter,
                        learning_rate=learning_rate,
                        learning_rate_init=learning_rate_init,
                        early_stopping=True,
                    ),
                ),
            ]
        )
        if not cv_force:
            nn_model.fit(X_train, y_train)
            y_val_hat = nn_model.predict(X_val)
            val_score = -metrics.mean_squared_error(y_val, y_val_hat)
        else:
            y_hat = model_selection.cross_val_predict(
                nn_model, X, y, cv=cv, n_jobs=n_jobs
            )
            val_score = -metrics.mean_squared_error(y, y_hat)

        return val_score

    if verbose == 0:
        optuna.logging.set_verbosity(optuna.logging.WARNING)
    nn_study = optuna.create_study(direction="maximize")
    nn_study.optimize(nn_objective, n_trials=n_trials)

    # extract the selected hyperparameters
    best_params = nn_study.best_params
    layer_names = [ele for ele in best_params.keys() if "n_units_layer_" in ele]
    hidden_layer_sizes = list()
    for layer_name in layer_names:
        hidden_layer_sizes.append(best_params[layer_name])
    hidden_layer_sizes = tuple(hidden_layer_sizes)

    # save the selected model
    nn_selected = Pipeline(
        [
            ("scaler", scaler),
            ("decomposer", decomposer),
            (
                "model",
                nn.MLPRegressor(
                    hidden_layer_sizes=hidden_layer_sizes,
                    alpha=best_params["alpha"],
                    max_iter=max_iter,
                    learning_rate=best_params["learning_rate"],
                    learning_rate_init=best_params["learning_rate_init"],
                    early_stopping=True,
                ),
            ),
        ]
    )
    nn_selected.fit(X, y)

    # feature importance
    feature_importance = None

    # selected hyper parameter
    selected_hyperparameter = best_params

    # hyperparameter searching range
    searching_range = {
        "learning_rate_init": "loguniform: [1e-4, 1e-2]",
        "n_layers": "uniform: [1, 5]",
        "layer_size": "uniform: [8, 512]",
        "alpha": "loguniform: [1e-8, 1e0]",
        "learning_rate": ["constant", "invscaling"],
    }

    # selected model
    selected_model = nn_selected

    # Using a class to save the results
    result = SavedResults(
        feature_importance, selected_hyperparameter, searching_range, selected_model
    )
    return result


# %% fun to select and fit gradient boosting model
def train_gradient_boost(
    X, y, cv=10, cv_force=False, n_jobs=10, n_trials=30, verbose=0
):
    # def a base model: sklearn gradient boosting model
    gb_model = XGBRegressor(learning_rate=0.1, n_jobs=n_jobs)

    if not cv_force:
        # split X,y into train and val set using validation error to select model
        X_train, X_val, y_train, y_val = model_selection.train_test_split(
            X, y, test_size=0.15
        )

    # define the Bayesian optimization process
    def gb_objective(trial):
        # parameter space
        param = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 1500, log=True),
            "max_depth": trial.suggest_int("max_depth", 2, 15),
        }
        # using cross validation to evaluate the model's performance on the training set
        gb_model.set_params(**param)

        if not cv_force:
            gb_model.fit(X_train, y_train)
            y_val_hat = gb_model.predict(X_val)
            val_score = -metrics.mean_squared_error(y_val, y_val_hat)
        else:
            y_hat = model_selection.cross_val_predict(
                gb_model, X, y, cv=cv, n_jobs=n_jobs
            )
            val_score = -metrics.mean_squared_error(y, y_hat)
        return val_score

    if verbose == 0:
        optuna.logging.set_verbosity(optuna.logging.WARNING)
    gb_study = optuna.create_study(direction="maximize")
    gb_study.optimize(gb_objective, n_trials=n_trials)

    # save the selected model
    gb_selected = gb_model
    gb_selected.set_params(**gb_study.best_params)
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


# %% fit to select and fit the random forest model
def train_random_forest(X, y, cv=10, cv_force=False, n_jobs=10, n_trials=30, verbose=0):
    if not cv_force:
        oob_score = True
    else:
        oob_score = False

    # random forest model
    rf_model = ensemble.RandomForestRegressor(oob_score=oob_score, n_jobs=n_jobs)

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
            val_score = -metrics.mean_squared_error(y, y_hat)
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
