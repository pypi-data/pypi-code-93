from typing import Dict, Tuple

import numpy as np


class AftAccuracy:
    """
    Generalized accuracy for AFT model.

    In AFT model target variable can be censored and thus is a 2-column array, in which the first
    column corresponds to the lower bound, and the second column to the upper bound of the target
    variable. The cases of no censoring are achieved by letting lower bound equal to upper bound.

    If all data is censored, then the accuracy score can be constructed by checking if predicted
    value is between lower and upper bound. This approach requires generalization to also take
    into account noncensored data.

    This metric solves this problem by creating new lower and upper bounds using `abs_epsilon`
    and `rel_epsilon`. One can think of these parameters as of acceptable errors (absolute and
    relative respectively). This approach extends the allowed interval for censored data and
    creates that interval for noncensored data.
    """

    def __init__(self, abs_epsilon: float = 0.0, rel_epsilon: float = 0.0):
        assert abs_epsilon >= 0 and rel_epsilon >= 0
        self.abs_epsilon = abs_epsilon
        self.rel_epsilon = rel_epsilon

    def calc_metrics(self, context: Dict):
        return {
            "train_accuracy": self.accuracy(
                context["y_train"], context["y_train_pred"]
            ),
            "test_accuracy": self.accuracy(context["y_test"], context["y_test_pred"]),
        }

    def accuracy(self, y, y_pred) -> float:
        y_np = np.array(y)
        y_pred_np = np.array(y_pred).flatten()  # flatten because transforming DataFrame
        lower_bound, upper_bound = self._compute_bounds(y_np)
        correct = sum((y_pred_np >= lower_bound) & (y_pred_np <= upper_bound))
        amount = len(y_np)
        return correct / amount

    def _compute_bounds(self, y: np.array) -> Tuple[np.array, np.array]:
        lower = (1 - self.rel_epsilon) * y[:, 0] - self.abs_epsilon
        upper = (1 + self.rel_epsilon) * y[:, 1] + self.abs_epsilon
        return lower, upper
