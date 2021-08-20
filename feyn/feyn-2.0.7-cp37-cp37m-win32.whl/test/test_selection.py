import unittest
from typing import Tuple, List

import feyn

from feyn._qlattice import connect_qlattice
from feyn._selection import _model_should_decay


class TestBest(unittest.TestCase):
    def setUp(self):
        self.lt = connect_qlattice()
        self.lt.reset()
        self.test_model = self.lt.sample_models(
            ["bmi"], "sex", kind="classification", max_complexity=2
        )[0]

    def test_close_models_are_not_in_output(self):
        unique_models = _get_unique_models(self.test_model, 30)
        dist_before = _max_model_dist(unique_models)
        self.assertEqual(dist_before, 1)

        best_models = feyn.best_diverse_models(unique_models, n=10)
        dist_after = _max_model_dist(best_models)
        self.assertEqual(dist_after, 3)
        self.assertLessEqual(len(best_models), 10)


def _max_model_dist(models: List[feyn.Model]) -> int:
    max_dist = -1
    for i, m in enumerate(models[:-1]):
        next_m = models[i + 1]
        dist = next_m[-1]._latticeloc[0] - m[-1]._latticeloc[0]
        max_dist = dist if dist > max_dist else max_dist
    return max_dist


class TestPruning(unittest.TestCase):
    def setUp(self):
        self.lt = connect_qlattice()
        self.lt.reset()
        self.test_models = self.lt.sample_models(
            ["bmi"], "sex", kind="classification", max_complexity=2
        )
        self.test_model = self.test_models[0]

    def test_duplicates_are_pruned(self):
        hashset = set(hash(m) for m in self.test_models)
        pruned = feyn.prune_models(self.test_models, decay=False, dropout=False)
        self.assertEqual(len(pruned), len(hashset))

    def test_old_model_decays(self):
        self.test_model.age = 10
        density = 20
        max_density = 50
        self.assertTrue(_model_should_decay(self.test_model, density, max_density))

    def test_dropout_removes_models_on_a_single_barren_location(self):
        unique_models = _get_unique_models(self.test_model, 20)
        pruned_models = feyn.prune_models(unique_models, decay=False)
        self.assertEqual(
            len(pruned_models),
            len(unique_models) - 1,
            "Exactly one model is expected to be removed",
        )

    def test_keeping_no_more_than_n_models(self):
       unique_models = _get_unique_models(self.test_model, 20)
       pruned_models = feyn.prune_models(
           unique_models, decay=False, dropout=False, keep_n=5
       )
       self.assertEqual(5, len(pruned_models))


def _set_model_output(
    model: feyn.Model, output_loc: Tuple[int, int, int], feature_name: str
) -> feyn.Model:
    mdict = model._to_dict(include_state=True)
    ret = mdict.copy()
    ret["nodes"][0]["name"] = feature_name
    ret["nodes"][-1]["location"] = output_loc
    return feyn.Model._from_dict(ret)


def _get_unique_models(model, n: int):
    x_location = 0
    models = []
    for i in range(n):
        models.append(_set_model_output(model, (x_location, i, i), str(i)))
        # ensure top models are same location to avoid inconsistencies in the pruning
        if i > 3:
            x_location += 1
    return models
