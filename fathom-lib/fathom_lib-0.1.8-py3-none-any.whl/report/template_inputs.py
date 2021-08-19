import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.metrics import roc_curve, auc, precision_score, f1_score, recall_score
from sklearn.metrics import confusion_matrix
from sklearn.inspection import partial_dependence
import plotly.figure_factory as ff
from sklearn.calibration import calibration_curve
import plotly.graph_objects as go
import numpy as np

from lightgbm import LGBMClassifier
from xgboost import XGBClassifier


def summary(runs, experiment):
    keys = set(runs[0].data.params.keys())
    name = None
    for key in keys:
        if "Classifier" in key:
            name = key.split("_")[0]
            break
    experiment_id = experiment.experiment_id
    experiment_name = experiment.name
    test_size = int(runs[0].data.metrics["test_size"])
    test_accuracy = round(runs[0].data.metrics["test_accuracy_score"], 5)
    return name, experiment_id, experiment_name, test_size, test_accuracy


def classifier_name(params_):
    name = None
    for key, value in params_.items():
        if "Classifier" in key:
            name = key.split("_")[0]
            break
    return name


def features_imp(pipeline, X_columns) -> str:
    model = pipeline.get_most_recent_final_model()
    if isinstance(model, XGBClassifier):
        fi = (
            pipeline.get_most_recent_final_model()
            .get_booster()
            .get_score(importance_type="gain")
        )
        fi = dict(sorted(fi.items(), key=lambda item: item[1]))
    elif isinstance(model, LGBMClassifier):
        fi = dict(zip(model.feature_name_, model.feature_importances_))
        fi = dict(sorted(fi.items(), key=lambda item: item[1]))
    else:
        try:
            fi = dict(zip(X_columns, model.feature_importances_))
            fi = dict(sorted(fi.items(), key=lambda item: item[1]))
        except AttributeError:
            return "Unknown classifier used"
    feat_imp = pd.DataFrame(
        {"Features": list(fi.keys()), "Importance": list(fi.values())}
    )

    return px.bar(feat_imp, x="Features", y="Importance").to_html(
        include_plotlyjs="cdn"
    ) + feat_imp.to_html(index=False)


def partial_d(pipeline, X_train, X_columns) -> str:
    model = pipeline.get_most_recent_final_model()
    if isinstance(model, LGBMClassifier):
        columns = model.feature_name_
        # This dummy is added to pass check_is_fitted from partial_dependence
        model.dummy_ = "Dummy"
    elif isinstance(model, XGBClassifier):
        columns = model.get_booster().feature_names
    else:
        columns = X_columns

    print(columns)
    print(X_train.columns)

    def make_plot(column: str) -> str:

        p_d = partial_dependence(
            model,
            X_train[columns],
            [column],
        )

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Histogram(x=X_train[column], name=f"{column} histogram"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=p_d[1][0],
                y=p_d[0][0],
                mode="lines",
                name=f"{column} partial dependence",
            ),
            secondary_y=True,
        )
        fig.update_xaxes(range=[min(p_d[1][0]), max(p_d[1][0])])
        return fig.to_html(include_plotlyjs="cdn")

    list_of_figs = [make_plot(column) for column in columns]
    return "\n".join(list_of_figs)


def confusion_m(y_test, y_test_pred_prob, pipeline) -> str:
    # Create figure
    model = pipeline.get_most_recent_final_model()
    fig = go.Figure()
    if isinstance(model, XGBClassifier):
        classes = model.classes_
    elif isinstance(model, LGBMClassifier):
        classes = model.classes_
    else:
        try:
            classes = model.classes_
        except AttributeError:
            return "Unknown classes for this model"
    # Add traces, one for each slider step
    for step in np.arange(0, 1.1, 0.1):
        x = classes
        y = classes
        z = confusion_matrix(y_test, np.array(y_test_pred_prob) > step, labels=classes)
        z_text = [[str(y) for y in x] for x in z]
        fig.add_trace(
            go.Heatmap(
                z=z,
                x=x,
                y=y,
                text=z,
                colorscale="Viridis",
                visible=False,
            )
        )

    # Make 5th trace visible
    fig.data[5].visible = True
    # Create and add slider
    steps = []
    for i in range(len(fig.data)):
        step = dict(
            method="update",
            args=[
                {"visible": [False] * len(fig.data)},
                {
                    "title": f"Slider switched to probability: {i*10}%",
                    "annotations": [
                        {
                            "font": {"color": "#FFFFFF", "size": 20},
                            "showarrow": False,
                            "text": f"{fig.data[i]['z'][y][x]}",
                            "x": x,
                            "xref": "x",
                            "y": y,
                            "yref": "y",
                        }
                        for y in [0, 1]
                        for x in [0, 1]
                    ],
                },
            ],
            label=f"{i*10}%",  # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [
        dict(
            active=5,
            currentvalue={"prefix": "Cut-off probability: "},
            pad={"t": 60},
            steps=steps,
        )
    ]

    fig.update_layout(
        annotations=steps[5]["args"][1]["annotations"],
    )

    fig.update_layout(
        sliders=sliders,
        xaxis_title="Predicted",
        yaxis_title="True",
        xaxis=dict(
            tickmode="array",
            tickvals=classes,
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=classes,
        ),
    )

    return fig.to_html(include_plotlyjs="cdn")


def decision_c(y_test, y_test_pred_prob) -> str:
    y_test = np.array(y_test).reshape(-1)
    y_test_pred_prob = np.array(y_test_pred_prob)
    x = np.linspace(0, 1, 101)
    y_precision = [precision_score(y_test_pred_prob > i, y_test) for i in x]
    y_recall = [recall_score(y_test_pred_prob > i, y_test) for i in x]
    y_f1 = [f1_score(y_test_pred_prob > i, y_test) for i in x]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y_precision,
            line=dict(color="blue", width=4, dash="dot"),
            name="Precision",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y_recall,
            line=dict(color="red", width=4, dash="dot"),
            name="Recall",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y_f1,
            line=dict(color="green", width=4, dash="dot"),
            name="F1",
        )
    )

    fig.update_layout(
        title="Decision chart",
        xaxis_title="Cut-off",
        yaxis_title="Scores",
    )
    return fig.to_html(include_plotlyjs="cdn")


def calibration_c(y_test, y_test_pred_prob) -> str:
    fraction_of_positives, mean_predicted_value = calibration_curve(
        y_test, y_test_pred_prob, n_bins=10
    )
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=mean_predicted_value,
            y=fraction_of_positives,
            line=dict(color="firebrick", width=4, dash="dot"),
            name="XGBoost",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=np.linspace(0, 1, 2),
            y=np.linspace(0, 1, 2),
            line=dict(color="black", width=4, dash="dot"),
            name="Perfectly calibrated",
        )
    )
    fig.update_layout(
        title="Calibration curve",
        xaxis_title="Mean predcted value",
        yaxis_title="Fraction of positives",
    )
    return fig.to_html(include_plotlyjs="cdn")


def roc_c(y_test_pred_prob, y_test) -> str:
    y_score = y_test_pred_prob
    fpr, tpr, thresholds = roc_curve(y_test, y_score)
    fig = px.area(
        x=fpr,
        y=tpr,
        title=f"ROC Curve (AUC={auc(fpr, tpr):.4f})",
        labels=dict(x="False Positive Rate", y="True Positive Rate"),
        width=900,
        height=800,
    )
    fig.add_shape(type="line", line=dict(dash="dash"), x0=0, x1=1, y0=0, y1=1)

    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_xaxes(constrain="domain")

    return fig.to_html(include_plotlyjs="cdn")


def density_c(y_test, y_test_pred_prob) -> str:
    # Add histogram data
    x1 = np.array(y_test_pred_prob)[
        np.where(np.array(y_test["Survived"] == 0))
    ].reshape(
        -1,
    )
    x2 = np.array(y_test_pred_prob)[
        np.where(np.array(y_test["Survived"] == 1))
    ].reshape(
        -1,
    )
    # Group data together
    hist_data = [x1, x2]
    group_labels = ["Label 0", "Label 1"]

    # Create distplot with custom bin_size
    fig = ff.create_distplot(
        hist_data,
        group_labels,
        bin_size=[
            0.05,
            0.05,
        ],
    )
    return fig.to_html(include_plotlyjs="cdn")


def metrics_input(metrics_):
    metrics_dict = {}
    for key, value in {
        **metrics_["validation"].pop("accuracy_score"),
        **metrics_["validation"].pop("roc_auc_score"),
        **metrics_["validation"],
    }.items():
        metrics_dict[key.capitalize().replace("_", " ")] = round(value, 5)
    return metrics_dict


def features(recent_test_data) -> str:
    df = recent_test_data.get_X_data()
    df_datatypes = pd.DataFrame(df.dtypes)
    df_null_count = df.count()
    full = pd.concat([df_datatypes, df_null_count], axis=1)
    full.columns = ["DataTypes", "Non-null counts"]
    return full.to_html()


def algorithm_and_preparation(params_):
    algorithm_dict = {}
    preparation_dict = {}
    for key, value in params_.items():
        if "Classifier" in key:
            algorithm_dict[key.split("__")[-1].strip("_")] = value
        else:
            preparation_dict[key.split("__")[-1].strip("_")] = value
    return algorithm_dict, preparation_dict
