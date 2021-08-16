from __future__ import annotations

from itertools import count
from typing import List, Iterable, Any

import numpy as np
import pandas as pd
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.model_selection import cross_val_score, BaseCrossValidator
from tqdm import tqdm


class WrapperFeatureSelection(TransformerMixin):
    """Iteratively build an optimal feature set by starting with an empty or pre-
    defined feature set and adding new features to it. The algorithm looks as follows:

    1. test performance on initial feature set
    2. while not all features selected:
        1. foreach feature not in selected features:
            1. temporarily add feature to selected features
            2. cross-validate model
        2. find feature with best cross-validated performance
        3. if performance of best feature is better than overall best performance:
            * add feature to selected features
            * else: break

    Parameters
    ----------
    model:
        model with a ``fit`` and ``predict`` function.
        E.g., an sklearn :class:`RandomForestClassifier`.
    scoring:
        which scoring function to use. Forwarded to sklearn's cross_val_score function
    cv:
        how many folds to use to validate the performance of the classifier. The outcome
        is used to determine the performance of the model on the given feature set
    max_features:
        maximum amount of features to select (in addition to warmstart_cols)
    warmstart_cols:
        set of columns that are pre-selected
    speculative_rounds:
        normally, the algorithm would stop when the performance does not improve
        the first time. If speculative rounds are greater than 0, then the algorithm
        continues for the specified amount of iterations in the hope to find a better
        solution in the next iteration.
    progress_bar:
        whether to show a progress bar in each iteration
    n_jobs : int
        number of concurrent jobs. See
        [sklearn documentation](https://scikit-learn.org/stable/glossary.html#term-n_jobs).

    Attributes
    ----------
    selected_: List[str]
        all selected features
    selected_extra_: List[str]
        features that have been selected in addition to the warmstart_cols
    improvements_: List[float]
        improvements of all features in selected_extra_, in terms of the ``scoring``
        function
    score_: float
        cross-validated score of the model on the selected features
    """

    def __init__(
        self,
        estimator: BaseEstimator,
        scoring=None,
        cv: int | Iterable[tuple] | BaseCrossValidator = 5,
        max_features: int = None,
        warmstart_cols: List[str] = None,
        speculative_rounds: int = 0,
        progress_bar: bool = True,
        n_jobs: int = None,
    ):
        self.estimator = estimator
        self.scoring = scoring
        self.cv = cv
        self.max_features = max_features
        self.warmstart_cols = warmstart_cols if warmstart_cols is not None else []
        self.speculative_rounds = speculative_rounds
        self.progress_bar = progress_bar
        self.n_jobs = n_jobs
        self.rounds_ = 0

    def fit(self, X: pd.DataFrame, y):
        selected = []
        improvements: List[float] = []
        if self.warmstart_cols:
            selected = [self.warmstart_cols.copy()]
            best_score = np.mean(
                cross_val_score(
                    self.estimator,
                    X[self.warmstart_cols],
                    y,
                    scoring=self.scoring,
                    cv=self.cv,
                    n_jobs=self.n_jobs,
                )
            )
            self.baseline_ = best_score
            improvements.append(0)
            print(f"Baseline: {best_score}")
        else:
            self.baseline_ = float("-inf")
            best_score = self.baseline_

        feature_pool = X.columns.tolist()
        speculations = 0
        for round_idx in count(1):
            print(f"Starting round #{round_idx}...")
            if speculations:
                print(f"(speculative round #{speculations})")

            candidates = self.make_candidates(feature_pool, selected)
            if not candidates:
                print("No more candidates. Stopping.")
                break
            scores = self._evaluate_candidates(X, y, candidates)
            best_score_in_round = scores[0]["score"]
            best_candidate = scores[0]["features"]

            improvement = (
                best_score_in_round - best_score
                if np.isfinite(best_score)
                else best_score_in_round
            )

            if improvement <= 0:
                if speculations >= self.speculative_rounds:
                    print(f"No improvement for {speculations + 1} rounds. Stopping.")
                    if speculations >= 1:
                        # remove speculatively selected features
                        selected = selected[:-speculations]
                        improvements = improvements[:-speculations]
                    break
                speculations += 1

            if improvement > 0:
                best_score = best_score_in_round
                speculations = 0
            if selected:
                prev_selected = set(selected[-1])
                added = set(best_candidate) - prev_selected
                removed = prev_selected - set(best_candidate)
                if added:
                    print(f"Adding {added}. ")
                if removed:
                    print(f"Removing {removed}. ")
            print(f"Selection now: {best_candidate}.")
            print(f"Improvement: {improvement:.3f}; best_score: {best_score:.2f}")

            selected.append(best_candidate)
            improvements.append(improvement)

        self.selected_ = selected[-1]
        self.candidates_ = selected
        self.improvements_ = improvements
        self.score_ = best_score
        return self

    def make_candidates(
        self, feature_pool: list[str], selection_history: list[list[str]]
    ) -> list[list[str]]:
        raise NotImplementedError

    def _evaluate_candidates(self, X, y, candidates) -> list[dict[str, Any]]:
        scores = []
        for c in tqdm(candidates, disable=not self.progress_bar):
            score = np.mean(
                cross_val_score(
                    self.estimator, X[c], y, scoring=self.scoring, cv=self.cv
                )
            )
            scores.append({"features": c, "score": score})

        result = list(sorted(scores, key=lambda s: s["score"], reverse=True))
        return result

    def _reset(self):
        self.rounds_ = 0
        self.selected_ = None
        self.selected_extra_ = None
        self.improvements_ = None
        self.score_ = None
        self.statistics_ = []

    def _rounds(self, X: pd.DataFrame):
        self.rounds_ = 0
        while len(self.selected_) < X.shape[1] and (
            self.max_features is None or len(self.selected_) < self.max_features
        ):
            self.rounds_ += 1
            yield self.rounds_

    def start_next_round(self, speculative: bool = False):
        self.rounds_ += 1

    def transform(self, X: pd.DataFrame, y=None):
        """Return DataFrame that contains exactly the selected features"""
        return X[self.selected_]


class ForwardFeatureSelection(WrapperFeatureSelection):
    def make_candidates(
        self, feature_pool: list[str], selection_history: list[list[str]]
    ) -> list[list[str]]:
        if selection_history:
            current_selection = selection_history[-1]
        else:
            current_selection = []

        return [
            current_selection + [c] for c in feature_pool if c not in current_selection
        ]


class BackwardFeatureElimination(WrapperFeatureSelection):
    def make_candidates(
        self, feature_pool: list[str], selection_history: list[list[str]]
    ) -> list[list[str]]:
        if not selection_history:
            # first iteration; test on all features
            return [feature_pool]
        else:
            current_selection = selection_history[-1]
            candidates = []
            for c in current_selection:
                candidate = current_selection.copy()
                candidate.remove(c)
                if len(candidate) > 0:
                    candidates.append(candidate)
            return candidates
