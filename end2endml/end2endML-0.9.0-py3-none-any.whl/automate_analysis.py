# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 20:44:59 2021

The file define a procedure to do automate data analysis

@author: yipeng.song@hotmail.com
"""
# %% load required libs
import os
import pandas as pd
import joblib
from end2endML.preprocessing import data_preprocessing
from end2endML.automate_modeling_evaluation import automate_modeling
from end2endML.automate_modeling_evaluation import automate_evaluation
import end2endML.utilities as utilities

# %% define an automate data analysis procedure
def automate_analysis(
    path2data,
    outcome,
    imbalance=True,
    imbalance_force=False,
    index_col=0,
    test_size=0.2,
    eval_cv=False,
    scaler="standard",
    decomposer=None,
    n_components=None,
    models=["linear", "elasticNet", "gb", "rf"],
    cv=10,
    cv_force=False,
    n_trials=30,
    n_jobs=10,
    max_iter=100,
    max_sample=1000,
    verbose=1,
    cat_levels_threshold=15,
    missing_threshold=0.5,
    for_future_test=False,
    save_results=True,
    random_state=None,
):
    """automate data analysis pipelines using ML models

    Args:
        path2data (str): path to the data for data analysis.
        outcome (str): the name of the outcome in the data.
        imbalance (bool, optional): whether to allow imbalance classification
            to be used when necessary? Defaults to False. If imbalance is True,
            when majority class is 10 times of the minority class, imbalance
            classification models will be used. Defaults to True.
        imbalance_force (bool, optional): force the procedure to choose the
            imbalanced classification models. Defaults to False. When it is True,
            imbalanced classification models will be used anyway. Defaults to False.
        index_col (int, optional): the index column for ID. Defaults to 0.
        test_size (float, optional): the proportion left for test set.
            Defaults to 0.2. The training data is (1-test_size). The model will be
            selected and fitted on the training data and test data will be used in
            the evaluation. When test_size is close to 0 (<=0.01), K-Fold CV will be
            used to evaluate the selected model.
        eval_cv (bool, optional): whether to use K-Fold CV to evaluate the selected models.
            Defaults to False.
        scaler (str, optional): scaling method on the columns. Defaults to 'standard'.
            Other possibilities include "max_abs", "min_max", "robust". Check the sklearn
            scaler method to find the meaning of different choices.
        decomposer (str, optional): dimension reduction method. Defaults to None. Other
            possibilities include "pca", "fast_ica", "nmf", "kernel_pca" with rbf kernel.
            Check the sklearn decomposition method to find the meaning of different choices.
        n_components (int, optional): the number of components in dimension reduction. Defaults
            to None. if it is None, n_components will be set to int(0.5 * min(X.shape)).
        models (list, optional): all the combinations from the following list.
            ['linear', 'lasso', 'ridge', 'elasticNet', 'svm', 'nn', 'gb', 'rf'],
            Defaults to ['linear', 'elasticNet', 'gb', 'rf']. Defaults to
            ['linear', 'elasticNet', 'gb', 'rf'].
        cv (int, optional): K-Fold CV. Defaults to 10.
        cv_force (bool, optional): whether to force the model selection to use
            K-Fold CV to evaluate the model. nn, gb and rf use the performance on the
            validation set (15% of the traning set, and the left part is the new training set)
            to do model selection. If cv_force is True, these models will also use CV to do
            model selection. Defaults to False.
        n_trials (int, optional): number of Bayesian Optimization experiments for model
            selection. nn, gb, svm and rf use this approach, while other methods using
            grid search. Defaults to 30.
        n_jobs (int, optional): number of cores used to select and fit the model.
            Defaults to 10.
        max_iter (int, optional): maximum iterations for linear models.
            Defaults to 100.
        max_sample (int, optional): the maximum number of samples used for data summary.
            Defaults to 1000. max_sample samples will randomly sampled to summarize the data.
        verbose (int, optional): whether to show log information.
            Defaults to 1. 1: show log information; 0: not show log information.
        cat_levels_threshold (int, optional): When the unique values of
            a column is less than this threshold, will take it as a categorical
            variable even the data type of this column is int or float. Defaults to 6.
        missing_threshold (float, optional): [0, 1], When the propotation
            of missing values larger than this threshold, remove the corresponding
            rows and columns. Defaults to 0.2.
        for_future_test (bool, optional): If the saved preprocessing is going
            to be used to preprocess the future test data, it is better set it
            as True. This argument is mainly about how to do one-hot encoding.
            When it is True, the first level will not be dropped and unknown class
            in the test set will be ignored. Defaults to False.
        save_results (bool, optional): whether to save the data summary report,
            preprocessed data, saved models and evaluation metrics. Defaults to True.
        random_state ([type], optional): random seed for splitting train and test.
            Defaults to None. If it is None, no random seed is used.

    Returns:
        None: results has already been written to the driver if save_results is True,
            check ./results for the saved data summary report, preprocessed data,
            saved models and evaluation metrics.
    """
    # using the data name + outcome as the experiment name to save the results
    name = os.path.basename(path2data).split(".")[0] + "_" + outcome

    ## load and summarize the data
    # load the data
    data = utilities.read_data(path2data, index_col=index_col)
    if verbose == 1:
        print(f"The size of the loaded data is {data.shape} \n {'-' * 50}")

    # summarize the data set
    if save_results:
        utilities.summarize_data(data, name, max_sample=max_sample, minimal=True)

    ## preprocess the data set
    # preprocess the data
    X, y, _, _, saved_preprocess_steps = data_preprocessing(
        data,
        outcome,
        name,
        cat_levels_threshold=cat_levels_threshold,
        missing_threshold=missing_threshold,
        for_future_test=for_future_test,
        verbose=verbose,
        save_results=save_results,
    )

    ## prepare the training and test set
    # split train and test set
    X_train, X_test, y_train, y_test = utilities.split_data(
        X, y, test_size=test_size, random_state=random_state
    )

    ## if some models have already been selected and trained, append rather than
    # replace the previous models
    if save_results:
        target_path = os.path.join("./results", name)
        path2result = os.path.join(target_path, "saved_selected_models.joblib")
        if os.path.isfile(path2result):
            previous_results = joblib.load(path2result)

            # remove the already saved models
            previous_models = previous_results.keys()
            previous_models = [ele.split("_")[-1] for ele in previous_models]
            trained_models = utilities.intersection(previous_models, models)
            if len(trained_models) > 0:
                if verbose == 1:
                    print(f"These models {trained_models} have already existed.")
                models = utilities.setdiff(models, previous_models)
                if len(models) == 0:
                    print("All the specified models have already trained and saved.")
                    return None

    ## selected and fit the model
    results = automate_modeling(
        X_train,
        y_train,
        scaler=scaler,
        decomposer=decomposer,
        n_components=n_components,
        models=models,
        imbalance=imbalance,
        imbalance_force=imbalance_force,
        cv=cv,
        cv_force=cv_force,
        n_trials=n_trials,
        n_jobs=n_jobs,
        max_iter=max_iter,
        verbose=verbose,
    )

    if verbose == 1:
        print(f"{'-' * 75} \n Selected and trained models are listed as follows:\n")
        print(results)

    ## evaluate the selected models
    # test evaluation or cv evaluation or all of them
    eval_test = True if test_size > 0.01 else False
    if (not eval_cv) and (test_size < 0.01):
        eval_cv = True

    # evaluate the models' performance on the test sets or K-Fold CV
    models_metrics = automate_evaluation(
        results,
        X_test,
        y_test,
        X,
        y,
        eval_test=eval_test,
        eval_cv=eval_cv,
        cv=cv,
        n_jobs=n_jobs,
    )
    if verbose == 1:
        print(f"{'-' * 75} \n The performance of the selected models: \n")
        print(models_metrics)

    ## save the selected models and evaluation metrics
    if save_results:
        # save models
        # combine current results and previous results
        if os.path.isfile(path2result):
            results.update(previous_results)
        joblib.dump(results, filename=path2result)

        # save metrics on the selected models
        path2metrics = os.path.join(target_path, "metrics.csv")
        if os.path.isfile(path2metrics):
            models_metrics_old = pd.read_csv(path2metrics, index_col=0)

            # join the current metrics and previous one
            models_metrics = models_metrics_old.join(models_metrics, how="outer")
        models_metrics.to_csv(path2metrics)

        # save the preprocessing piplines
        path2preprocess = os.path.join(target_path, "saved_preprocess_steps.joblib")
        joblib.dump(saved_preprocess_steps, filename=path2preprocess)

    return None
