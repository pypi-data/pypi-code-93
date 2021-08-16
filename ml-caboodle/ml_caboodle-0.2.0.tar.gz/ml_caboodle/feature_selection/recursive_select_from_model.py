import numpy as np
import pandas as pd
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.model_selection import cross_val_score


class RecursiveSelectFromModel(TransformerMixin):
    """Recursively select features by training a classifier and dropping the least
    relevant features (according to ``clf.feature_importances_``), while the performance
    does not significantly decrease after dropping the features.

    Parameters
    ----------
    clf:
        classifier with a ``fit`` and ``predict`` function which has a
        ``feature_importances_`` attribute after fitting. E.g., an sklearn
        :class:`RandomForestClassifier`.
    drop_percent:
        which fraction of the attributes to drop after each iteration, e.g., 0.1
    cv_folds:
        how many folds to use to validate the performance of the classifier. The outcome
        is used to determine when the performance begins to drop
    score_delta:
        if the performance drops more than this value from the best performance, it is
        considered as "dropped"
    speculative_rounds:
        normally, the algorithm would stop when the performance drops significantly for
        the first time. If speculative rounds are greater than 0, then the algorithm
        continues for the specified amount of iterations in the hope to find a better
        solution in the next iteration.

    Attributes
    ----------
    selected_: List[str]
        the smallest feature set that does not lead to a significant performance drop
        from the best solution
    score_: float
        the score achieved by the selected features

    See Also
    --------
    * :class:`sklearn.feature_selection.SelectFromModel`

    """

    def __init__(
        self,
        clf: BaseEstimator,
        drop_percent: float,
        cv_folds: int,
        score_delta: float,
        speculative_rounds: int = 0,
    ):
        self.clf = clf
        self.drop_percent = drop_percent
        self.cv_folds = cv_folds
        self.score_delta = score_delta
        self.speculative_rounds = speculative_rounds

    def fit(self, X: pd.DataFrame, y):
        best_score = float("-inf")
        all_cols = X.columns.tolist()
        selected = all_cols
        history = []
        spec_round = 0
        while True:
            print(f"selected: {len(selected)}")
            new_score = cross_val_score(
                self.clf, X[selected], y, cv=self.cv_folds, n_jobs=-2
            )
            new_score = np.mean(new_score)
            print(f"current score: {new_score:.3f}; best score: {best_score:.3f}")
            print()
            if (
                new_score + self.score_delta >= best_score
                or spec_round < self.speculative_rounds
            ):
                if new_score + self.score_delta >= best_score:
                    spec_round = 0
                else:
                    spec_round += 1
                if spec_round > 0:
                    print(f"Starting speculative round #{spec_round}")

                if new_score > best_score:
                    best_score = new_score
                score = new_score
                history.append((score, len(selected), selected))
                self.clf.fit(X[selected], y)
                fimp = self.clf.feature_importances_
                fimp = pd.DataFrame(
                    fimp, columns=["importance"], index=selected
                ).sort_values("importance", ascending=False)
                drop_count = max(int(len(fimp) * self.drop_percent), 1)
                if drop_count >= len(fimp):
                    print("No columns left. Stopping.")
                    break
                selected = fimp.index[:-drop_count].tolist()
            else:
                selected = history[-spec_round - 1][2]
                score = history[-spec_round - 1][0]
                print("Too many rounds without improvement. Stopping.")
                break
        self.score_ = score
        self.selected_ = selected

    def transform(self, X: pd.DataFrame, y=None):
        return X[self.selected_]
