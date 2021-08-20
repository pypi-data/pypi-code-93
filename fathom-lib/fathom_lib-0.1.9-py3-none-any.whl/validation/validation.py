import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import holoviews as hv

hv.extension("bokeh")

from fathom_lib.metrics.sklearn_metrics import SklearnMetrics
from fathom_lib.metrics.shap_feature_importance import ShapFeatureImportance

from fathom_lib.metrics.aft_concordance_index import AftConcordanceIndex
from fathom_lib.metrics.aft_accuracy import AftAccuracy


def expanding_window_validation(
    pipeline,
    X,
    y_columns,
    time_column,
    train_cutoff_window_str,
    test_cutoff_window_str,
    test_freq,
    model_type,
    metrics,
    verbose=True,
):
    """
    Starts training on data from interval <min_dt,  (min_dt + train_cutoff_window))
    and tests on data from interval <min_dt + 2 * train_cutoff_window,
    min_dt + 2 * train_cutoff_window + test_cutoff_window) to avoid look-ahead bias.
    On the next step each interval end is increased by train_cutoff_window.
    """

    y = X[y_columns]

    min_dt = min(X[time_column])
    max_dt = max(X[time_column])

    train_cutoff_window = pd.Timedelta(train_cutoff_window_str)
    test_cutoff_window = pd.Timedelta(test_cutoff_window_str)

    validation_scores = dict()

    test_dates = pd.date_range(min_dt, max_dt, freq=test_freq)

    if verbose:
        print("Date range from: ", min_dt, " to:  ", max_dt)
        print("Testing started!\n")

    X_test = None
    for test_start_dt in test_dates:
        cutoff_dt = test_start_dt - train_cutoff_window
        train_indices = np.where(X[time_column] < cutoff_dt)[0]

        test_indices = np.where(
            (X[time_column] >= test_start_dt)
            & (X[time_column] < test_start_dt + test_cutoff_window)
        )[0]

        X_train, X_test = X.iloc[train_indices], X.iloc[test_indices]
        y_train, y_test = y.iloc[train_indices], y.iloc[test_indices]

        if X_train.shape[0] == 0 or X_test.shape[0] == 0:
            continue

        pipeline = pipeline.fit(X_train)

        if verbose:
            print("Training cutoff date:", cutoff_dt)
            print(
                "Training size:", X_train.shape, "| Testing size:", X_test.shape, "\n"
            )

        if model_type == "classifier":
            y_train_pred = pipeline.predict_proba(X_train).iloc[:, -1]
            y_test_pred = pipeline.predict_proba(X_test).iloc[:, -1]
        elif model_type == "regressor":
            y_train_pred = pipeline.predict(X_train)
            y_test_pred = pipeline.predict(X_test)

        recent_test_data = pipeline.get_most_recent_data()
        y_test = recent_test_data.get_y_data()

        context = dict(
            train_size=len(train_indices),
            y_train=y_train,
            y_train_pred=y_train_pred,
            test_size=len(test_indices),
            y_test=y_test,
            y_test_pred=y_test_pred,
        )

        validation_scores[test_start_dt] = calc_list_of_metrics(metrics, context)
        validation_scores[test_start_dt].update({"train_size": context["train_size"]})
        validation_scores[test_start_dt].update({"test_size": context["test_size"]})

    shap_feature_importance = ShapFeatureImportance().calc_metrics(
        {"pipeline": pipeline, "model_type": model_type}
    )
    validation_scores.update(shap_feature_importance)

    add_aggregate_report(recent_test_data, y_test_pred, validation_scores, model_type)
    add_prediction_plot(y_test, y_test_pred, validation_scores, model_type)
    add_per_id_plots(
        y_test,
        y_test_pred,
        pipeline.get_most_recent_data().data,
        time_column,
        validation_scores,
        model_type,
    )

    return validation_scores


def single_split_validation(
    pipeline,
    X,
    y_columns,
    model_type,
    metrics,
    split_at=0.8,
    verbose=True,
):
    """
    Single split validation.
    """

    validation_scores = dict()
    y = X[y_columns]

    train_indices = [i for i in range(int(split_at * len(X)))]
    test_indices = [i for i in range(int(split_at * len(X)), len(X))]

    X_train, X_test = X.iloc[train_indices], X.iloc[test_indices]
    pipeline = pipeline.fit(X_train)

    y_train = pipeline.get_most_recent_data().get_y_data()
    X_train_ = pipeline.get_most_recent_data().get_X_data()

    if verbose:
        print("Training on:", X_train.shape, "| Testing on:", X_test.shape)

    if model_type == "classifier":
        y_train_pred = pipeline.predict_proba(X_train).iloc[:, -1]
        y_test_pred = pipeline.predict_proba(X_test).iloc[:, -1]
    elif model_type == "regressor":
        y_train_pred = pipeline.predict(X_train)
        y_test_pred = pipeline.predict(X_test)

    recent_test_data = pipeline.get_most_recent_data()
    y_test = recent_test_data.get_y_data()
    X_test_ = recent_test_data.get_X_data()

    context = dict(
        train_size=len(train_indices),
        y_train=y_train,
        y_train_pred=y_train_pred,
        test_size=len(test_indices),
        y_test=y_test,
        y_test_pred=y_test_pred,
    )

    validation_scores["validation"] = calc_list_of_metrics(metrics, context)
    validation_scores["validation"].update({"train_size": context["train_size"]})
    validation_scores["validation"].update({"test_size": context["test_size"]})

    shap_feature_importance = ShapFeatureImportance().calc_metrics(
        {"pipeline": pipeline, "model_type": model_type}
    )
    validation_scores.update(shap_feature_importance)

    add_aggregate_report(recent_test_data, y_test_pred, validation_scores, model_type)
    add_prediction_plot(y_test, y_test_pred, validation_scores, model_type)
    validation_scores["y_test_pred"] = pipeline.predict(X_test)
    validation_scores["y_test_pred_prob"] = y_test_pred
    validation_scores["pipeline"] = pipeline
    validation_scores["X_test"] = X_test_
    validation_scores["X_train"] = X_train_
    validation_scores["y_test"] = y_test
    validation_scores["X_columns"] = recent_test_data.X_columns
    validation_scores["recent_test_data"] = recent_test_data
    return validation_scores


def add_aggregate_report(recent_test_data, y_test_pred, validation_scores, model_type):
    # add report by id, aggregate by the mean prediction
    X_test = recent_test_data.data
    if X_test is not None and X_test.shape[0] > 0 and "id" in X_test.columns:
        df_results_by_id: pd.DataFrame = X_test[["id"]].copy().reset_index()
        if model_type == "classifier":
            df_results_by_id["probability"] = y_test_pred
            df_results_by_id = (
                df_results_by_id.groupby("id")["probability"].mean().reset_index()
            )
            df_results_by_id["probability"] = (
                df_results_by_id["probability"] * 100
            ).map(int)
            df_results_by_id.sort_values("probability", ascending=False, inplace=True)
        elif model_type == "regressor":
            df_results_by_id["prediction"] = y_test_pred
            df_results_by_id = (
                df_results_by_id.groupby("id")["prediction"].mean().reset_index()
            )
            df_results_by_id.sort_values("prediction", inplace=True)
        validation_scores["results_by_id"] = df_results_by_id.to_html(index=False)


def add_prediction_plot(y_test, y_test_pred, validation_scores, model_type):
    if model_type == "classifier":
        plt.scatter(y_test_pred, y_test, c=np.array(y_test))
        plt.title("Prediction Plot")
        plt.xlabel("Probability")
        plt.ylabel("Class")
    elif model_type == "regressor":
        y_test = y_test.iloc[:, 0]
        plt.scatter(y_test, y_test_pred, label="True vs. Prediction Plot")
        plt.title("Prediction Plot")
        plt.xlabel("True Values")
        plt.ylabel("Predicted Values")
        plt.legend(loc="upper left")

    plt.rcParams["figure.figsize"] = (20, 10)

    f = BytesIO()
    plt.savefig(f, format="png")
    f.seek(0)

    validation_scores["prediction_plot"] = f


def calc_list_of_metrics(metrics, context):
    """
    For a list o metrics, the function calculates their values and
    returns them in a dictionary.
    """
    scores = dict()
    for metric_name in metrics:
        cls = eval(metric_name)
        if isinstance(cls, SklearnMetrics):
            scores.update(cls.calc_metrics(context))
        else:
            scores[cls.__class__.__name__] = cls.calc_metrics(context)
    return scores


def add_per_id_plots(
    y_test, y_test_pred, X_test, time_column, validation_scores, model_type
):
    """
    Creates a dashboard in HoloView with prediction plots for every ID used in the data.
    """
    if model_type == "regressor":
        ids_len = len(X_test["id"].unique())
        prediction_plots_per_id = {}
        for id_name in X_test["id"].unique():
            X_id = X_test.loc[X_test["id"] == id_name]
            x_axis = X_id[time_column]
            y_id_test = y_test.iloc[X_id.index]
            y_id_test_pred = y_test_pred.iloc[X_id.index]
            plot_1 = [
                hv.Scatter(
                    (x_axis, np.array(y_id_test).flatten()), label="True Values"
                ).opts(xlabel="Date", ylabel="Value", width=550, height=450)
            ]
            plot_2 = [
                hv.Curve(
                    (x_axis, np.array(y_id_test_pred).flatten()),
                    label="Predicted Values",
                ).opts(
                    color="orange", xlabel="Date", ylabel="Value", width=550, height=450
                )
            ]
            plot_final = hv.Overlay(plot_1 + plot_2)
            prediction_plots_per_id[str(id_name)] = plot_final
        holo_map = hv.HoloMap(prediction_plots_per_id, kdims="ID")
        f = BytesIO()
        renderer = hv.renderer("bokeh")
        renderer.save(holo_map, f)
        f.seek(0)
        validation_scores["prediction_plots_per_id"] = f
