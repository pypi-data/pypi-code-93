# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" AutoML classification metrics computation wrapper class."""

from ignite.metrics import EpochMetric
from azureml.automl.runtime.shared.score.scoring import score_classification
from azureml.automl.runtime.shared.score.scoring import constants
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np


def _automl_classification_metrics_compute_fn_wrapper(labels, multilabel, is_train):
    """
    This wrapper method will help set the metrics to be computed depending on the flags.

    :param labels: class labels
    :type labels: List of class labels
    :param multilabel: flag indicating whether this is multilabel problem
    :type multilabel: bool
    :param is_train: flag indicating whether the metric is computed with training data or not.
    :type is_train: bool
    :return: Dictionary of (MetricLiteral, metric values).
    """

    def automl_classification_metrics_compute_fn(y_preds, y_targets):
        num_classes = len(labels)
        y_true = y_targets.detach().numpy()
        y_pred = y_preds.detach().numpy()

        if not multilabel:
            y_transformer = LabelEncoder()
            y_transformer.fit(labels)
        else:
            y_transformer = MultiLabelBinarizer()
            y_transformer.fit([labels])

        metrics_names = list()

        if not is_train:
            metrics_names.append(constants.ACCURACY)
            metrics_names.append(constants.LOG_LOSS)
            metrics_names.append(constants.PRECISION_MICRO)
            metrics_names.append(constants.PRECISION_MACRO)
            metrics_names.append(constants.PRECISION_WEIGHTED)
            metrics_names.append(constants.RECALL_MICRO)
            metrics_names.append(constants.RECALL_MACRO)
            metrics_names.append(constants.RECALL_WEIGHTED)
            metrics_names.append(constants.F1_MICRO)
            metrics_names.append(constants.F1_MACRO)
            metrics_names.append(constants.F1_WEIGHTED)
            metrics_names.append(constants.AUC_MICRO)
            metrics_names.append(constants.AUC_MACRO)
            metrics_names.append(constants.AUC_WEIGHTED)
            metrics_names.append(constants.AVERAGE_PRECISION_MICRO)
            metrics_names.append(constants.AVERAGE_PRECISION_MACRO)
            metrics_names.append(constants.AVERAGE_PRECISION_WEIGHTED)
            metrics_names.append(constants.PRECISION_CLASSWISE)
            metrics_names.append(constants.RECALL_CLASSWISE)
            metrics_names.append(constants.F1_CLASSWISE)
            metrics_names.append(constants.AVERAGE_PRECISION_CLASSWISE)
            metrics_names.append(constants.AUC_CLASSWISE)
            metrics_names.append(constants.CLASSIFICATION_REPORT)

            if not multilabel:
                metrics_names.append(constants.CONFUSION_MATRIX)
                metrics_names.append(constants.ACCURACY_TABLE)
            else:
                metrics_names.append(constants.IOU)
                metrics_names.append(constants.IOU_MICRO)
                metrics_names.append(constants.IOU_MACRO)
                metrics_names.append(constants.IOU_WEIGHTED)
                metrics_names.append(constants.IOU_CLASSWISE)

        else:
            if not multilabel:
                metrics_names.append(constants.ACCURACY)
            else:
                metrics_names.append(constants.IOU)

        metrics = score_classification(y_true, y_pred, metrics_names,
                                       np.array(range(num_classes)),
                                       np.array(range(num_classes)),
                                       y_transformer=y_transformer,
                                       multilabel=multilabel)

        return metrics

    return automl_classification_metrics_compute_fn


class AutoMLClassificationMetrics(EpochMetric):
    """
    This metric calls the Automated ML Classification Metrics Scoring Module.
    """

    def __init__(self, labels, multilabel=False, is_train=False):
        """
        :param labels: class labels
        :type labels: List of class labels
        :param multilabel: flag indicating whether this is multilabel problem
        :type multilabel: bool
        :param is_train: flag indicating whether the metric is computed with training data or not.
        :type is_train: bool
        """

        super(AutoMLClassificationMetrics, self).__init__(
            _automl_classification_metrics_compute_fn_wrapper(
                labels, multilabel, is_train))
