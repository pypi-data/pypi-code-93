"""Functions to compute metrics and scores"""

import numpy as np
import typing
import feyn.losses

from ._mutual import calculate_mi
from ._linear import calculate_pc
from ._spearman import calculate_spear


def accuracy_score(true: typing.Iterable, pred: typing.Iterable) -> float:
    """
    Compute the accuracy score of predictions

    The accuracy score is useful to evaluate classification models. It is the fraction of the predictions that are correct. Formally it is defined as:

    (number of correct predictions) / (total number of predictions)

    Arguments:
        true -- Expected values
        pred -- Predicted values

    Returns:
        accuracy score for the predictions
    """
    correct = np.equal(true, np.round(pred))
    return np.mean(correct)


def accuracy_threshold(true: typing.Iterable, pred: typing.Iterable) -> typing.Tuple[float, float]:
    """
    Compute the accuracy score of predictions with optimal threshold

    The accuracy score is useful to evaluate classification models. It is the fraction of the predictions that are correct. Accuracy is normally calculated under the assumption that the threshold that separates true from false is 0.5. Hovever, this is not the case when a model was trained with another population composition than on the one which is used.

    This function first computes the threshold limining true from false classes that optimises the accuracy. It then returns this threshold along with the accuracy that is obtained using it.

    Arguments:
        true -- Expected values
        pred -- Predicted values

    Returns a tuple with:
        threshold that maximizes accuracy
        accuracy score obtained with this threshold
    """
    import sklearn.metrics

    fpr, tpr, _thresholds = sklearn.metrics.roc_curve(true, pred)

    # Also compute accuracy and the threshold that maximises it
    num_pos_class = true.sum()
    num_neg_class = len(true) - num_pos_class

    tp = tpr * num_pos_class
    tn = (1 - fpr) * num_neg_class
    acc = (tp + tn) / (num_pos_class + num_neg_class)

    best_threshold = _thresholds[np.argmax(acc)]
    return best_threshold, np.amax(acc)


def roc_auc_score(true: typing.Iterable, pred: typing.Iterable) -> float:
    """
    Calculate the Area Under Curve (AUC) of the ROC curve.

    A ROC curve depicts the ability of a binary classifier with varying threshold.

    The area under the curve (AUC) is the probability that said classifier will
    attach a higher score to a random positive instance in comparison to a random
    negative instance.

    Arguments:
        true -- Expected values
        pred -- Predicted values

    Returns:
        AUC score for the predictions
    """

    pos_class = pred[true == 1]  # Score distribution of positive class
    neg_class = pred[true == 0]  # Score distribution of negative class

    thresholds = np.append([0, 1], np.unique(pred))[
        :, np.newaxis
    ]  # Array of threshold values
    tpr = np.sort(
        np.mean(pos_class >= thresholds, axis=1)
    )  # True positive rates for distinct threshold values
    fpr = np.sort(
        np.mean(neg_class >= thresholds, axis=1)
    )  # False negative rates for distinct threshold values

    auc_score = np.trapz(tpr, fpr)  # Calculating the integral under the ROC curve

    return auc_score


def r2_score(true: typing.Iterable, pred: typing.Iterable) -> float:
    """
    Compute the r2 score

    The r2 score for a regression model is defined as
    1 - rss/tss

    Where rss is the residual sum of squares for the predictions, and tss is the total sum of squares.
    Intutively, the tss is the resuduals of a so-called "worst" model that always predicts the mean. Therefore, the r2 score expresses how much better the predictions are than such a model.

    A result of 0 means that the model is no better than a model that always predicts the mean value
    A result of 1 means that the model perfectly predicts the true value

    It is possible to get r2 scores below 0 if the predictions are even worse than the mean model.

    Arguments:
        true -- Expected values
        pred -- Predicted values

    Returns:
        r2 score for the predictions
    """

    mean = true.mean()

    rss = np.sum(
        (true - pred) ** 2
    )  # Residual sum of squares (this is the squared loss of this predition)
    tss = np.sum(
        (true - mean) ** 2
    )  # Total sum of squares (this is the squared loss of a model that predicts the mean)

    # r2 score expresses how much better the predictions are compared to a model that predicts the mean
    return 1 - rss / tss


def mae(true: typing.Iterable, pred: typing.Iterable):
    """
    Compute the mean absolute error

    Arguments:
        true -- Expected values
        pred -- Predicted values

    Returns:
        MAE for the predictions
    """
    return feyn.losses.absolute_error(true, pred).mean()


def mse(true: typing.Iterable, pred: typing.Iterable):
    """
    Compute the mean squared error

    Arguments:
        true -- Expected values
        pred -- Predicted values

    Returns:
        MSE for the predictions
    """
    return feyn.losses.squared_error(true, pred).mean()


def rmse(true: typing.Iterable, pred: typing.Iterable):
    """
    Compute the root mean squared error

    Arguments:
        true -- Expected values
        pred -- Predicted values

    Returns:
        RMSE for the predictions
    """
    return np.sqrt(feyn.losses.squared_error(true, pred).mean())


def get_summary_metrics_classification(true: typing.Iterable, pred: typing.Iterable):
    """
    Get summary metrics for classification

    Arguments:
        true -- Expected values
        pred -- Predicted values

    Returns:
        A dictionary of summary metrics
    """
    from sklearn.metrics import roc_auc_score

    precision, recall = precision_recall(true, np.round(pred))  # Round just in case
    return {
        "Accuracy": accuracy_score(true, pred),
        "AUC": roc_auc_score(true, pred),
        "Precision": precision,
        "Recall": recall,
    }


def get_summary_metrics_regression(true: typing.Iterable, pred: typing.Iterable):
    """
    Get summary metrics for regression

    Arguments:
        true -- Expected values
        pred -- Predicted values

    Returns:
        A dictionary of summary metrics
    """
    return {
        "R2": r2_score(true, pred),
        "RMSE": rmse(true, pred),
        "MAE": np.mean(feyn.losses.absolute_error(true, pred)),
    }


def confusion_matrix(true: typing.Iterable, pred: typing.Iterable) -> np.ndarray:
    """
    Compute a Confusion Matrix.

    Arguments:
        true -- Expected values (Truth)
        pred -- Predicted values

    Returns:
        [cm] -- a numpy array with the confusion matrix
    """

    classes = np.union1d(pred, true)

    sz = len(classes)
    matrix = np.zeros((sz, sz), dtype=int)
    for tc in range(sz):
        pred_tc = pred[true == classes[tc]]
        for pc in range(sz):
            matrix[(tc, pc)] = len(pred_tc[pred_tc == classes[pc]])
    return matrix


def precision_recall(true: typing.Iterable, pred: typing.Iterable):
    """
    Get precision and recall

    Arguments:
        true -- Expected values
        pred -- Predicted values

    Returns:
        precision, recall
    """
    cm = confusion_matrix(true, pred)

    tp = cm[1][1]
    fn = cm[1][0]
    fp = cm[0][1]

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)

    return precision, recall


def f1_score(true: typing.Iterable, pred: typing.Iterable):
    """Get F1 score

    Args:
        true (typing.Iterable): Expected values
        pred (typing.Iterable): Predicted values

    Returns:
        f1 score
    """
    precision, recall = precision_recall(true, pred)
    f1_score = (2 * precision * recall) / (precision + recall)
    return f1_score


def false_positive_rate(true: typing.Iterable, pred: typing.Iterable):
    cm = confusion_matrix(true, pred)

    fp = cm[0][1]
    tn = cm[0][0]

    return fp / (fp + tn)


def segmented_loss(model, data, by=None, loss_function="squared_error"):
    # Magic support for pandas DataFrame
    if type(data).__name__ == "DataFrame":
        data = {col: data[col].values for col in data.columns}

    if by is None:
        by = model.target

    if data[by].dtype == object or len(np.unique(data[by])) < 10:
        return discrete_segmented_loss(model, data, by, loss_function)
    else:
        return continuous_segmented_loss(model, data, by, loss_function)


def discrete_segmented_loss(model, data, by, loss_function):
    loss_function = feyn.losses._get_loss_function(loss_function)
    output = model.target

    pred = model.predict(data)

    bins = []
    cnt = []
    stats = []
    for cat in np.unique(data[by]):
        bool_index = data[by] == cat
        subset = {key: values[bool_index] for key, values in data.items()}
        pred_subset = pred[bool_index]

        loss = np.mean(loss_function(subset[output], pred_subset))

        bins.append(cat)
        cnt.append(len(pred_subset))
        stats.append(loss)

    return bins, cnt, stats


def significant_digits(x, p):
    mags = 10 ** (p - 1 - np.floor(np.log10(x)))
    return np.round(x * mags) / mags


def continuous_segmented_loss(model, data, by, loss_function):
    bincnt = 12
    loss_function = feyn.losses._get_loss_function(loss_function)
    output = model.target

    pred = model.predict(data)

    bins = []
    cnt = []
    stats = []

    mn = np.min(data[by])
    mx = np.max(data[by])
    stepsize = significant_digits((mx - mn) / bincnt, 2)

    lower = mn
    while lower < mx:
        upper = lower + stepsize

        bool_index = (data[by] >= lower) & (data[by] < upper)
        subset = {key: values[bool_index] for key, values in data.items()}
        pred_subset = pred[bool_index]

        if len(pred_subset) == 0:
            loss = np.nan
        else:
            loss = np.mean(loss_function(subset[output], pred_subset))
        bins.append((lower, upper))
        cnt.append(len(pred_subset))
        stats.append(loss)

        lower = upper

    return bins, cnt, stats


def _get_activations(model, data):

    n_nodes = len(model)
    n_samples = len(next(data.values().__iter__()))

    res = np.full((n_nodes, n_samples), 0.0)

    for s in range(n_samples):
        row = {col: val[s : s + 1] for col, val in data.items()}
        model._query(row, None)
        for n in range(n_nodes):
            res[n, s] = model[n].activation[0]

    return res


def get_mutual_information(model, data):
    """
    Calculate the mutual information
    between each node of the model and
    the output.
    """
    if data is None:
        return None

    # Magic support for dataframes
    if type(data).__name__ == "DataFrame":
        data = {col: data[col].values for col in data.columns}

    ret = []

    data_output = data[model[-1].name]
    activations = _get_activations(model, data)
    for n in range(len(model)):
        ret.append(calculate_mi([activations[n], data_output]))

    return ret


def get_pearson_correlations(model, data):
    """
    Calculate the pearson correlation
    coefficient between each node of the
    model and the output.
    """
    if data is None:
        return None

    # Magic support for dataframes
    if type(data).__name__ == "DataFrame":
        data = {col: data[col].values for col in data.columns}

    ret = []

    data_output = data[model[-1].name]
    activations = _get_activations(model, data)
    for n in range(len(model)):
        ret.append(calculate_pc(activations[n], data_output))

    return ret


def get_spearmans_correlations(model, data):
    """
    Calculate the Spearman's correlation
    coefficient between each node of the
    model and the output.
    """
    if data is None:
        return None

    # Magic support for dataframes
    if type(data).__name__ == "DataFrame":
        data = {col: data[col].values for col in data.columns}

    ret = []

    data_output = data[model[-1].name]
    activations = _get_activations(model, data)
    for n in range(len(model)):
        ret.append(calculate_spear(activations[n], data_output))

    return ret


def get_summary_information(model, df):
    true = df[model[-1].name]
    pred = model.predict(df)
    if model[-1].spec.startswith("out:lr"):
        return get_summary_metrics_classification(true, pred)
    else:
        return get_summary_metrics_regression(true, pred)
