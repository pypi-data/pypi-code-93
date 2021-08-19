from sklearn.metrics import roc_auc_score

from fathom_lib.component_autogeneration.submodules import import_class


class SklearnMetrics:
    def __init__(self, metrics, classification_threshold=0.5):
        self.metrics = metrics
        self.classification_threshold = classification_threshold

    def calc_metrics(self, context):
        scores = dict()
        for metric_name in self.metrics:
            metric = import_class("sklearn.metrics", metric_name)
            train_score = self.calc_sklearn_metric(
                metric,
                context["y_train"],
                context["y_train_pred"],
                self.classification_threshold,
            )
            test_score = self.calc_sklearn_metric(
                metric,
                context["y_test"],
                context["y_test_pred"],
                self.classification_threshold,
            )
            scores[metric.__name__] = {
                "train_" + metric.__name__: train_score,
                "test_" + metric.__name__: test_score,
            }
        return scores

    @classmethod
    def calc_sklearn_metric(cls, metric, y, y_pred, classification_threshold=0.5):
        try:
            if metric.__name__ == "roc_auc_score":
                metric = cls.safe_roc_auc_score
            score = metric(y, y_pred)
        except ValueError:  # When the metric can't support continuous values
            score = metric(y, (y_pred >= classification_threshold).astype(int))
        return score

    @staticmethod
    def safe_roc_auc_score(y, y_pred):
        """
        ROC AUC score is not defined when there is only one class present.
        """
        try:
            return roc_auc_score(y, y_pred)
        except ValueError:
            return 0.5
