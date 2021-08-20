import unittest

import feyn
from .test_sdk import _simple_unary_model, _simple_binary_model, _add_register_to_dict


class TestExcludeFunctions(unittest.TestCase):
    def setUp(self):
        self.test_models = [
            _simple_unary_model(spec=spec)
            for spec in ["cell:gaussian(i)->i", "cell:exp(i)->i", "cell:log(i)->i"]
        ]

    def test_exclude_single_function_filter(self):
        f = feyn.filters.ExcludeFunctions("gaussian")
        self.assertEqual(2, len(list(filter(f, self.test_models))))

    def test_multiple_function_exclusion(self):
        f = feyn.filters.ExcludeFunctions(["gaussian", "exp"])
        self.assertEqual(1, len(list(filter(f, self.test_models))))


class TestComplexity(unittest.TestCase):
    def test_complexity_filter(self):
        test_models = [
            _simple_unary_model(spec=spec)
            for spec in ["cell:gaussian(i)->i", "cell:exp(i)->i"]
        ]
        test_models += [_simple_binary_model()]
        f = feyn.filters.Complexity(3)
        self.assertEqual(1, len(list(filter(f, test_models))))


class TestContainsInput(unittest.TestCase):
    def test_contains_filter(self):
        unary_models = [
            _simple_unary_model(spec=spec, input_name=name)
            for spec in ["cell:gaussian(i)->i", "cell:exp(i)->i", "cell:log(i)->i"]
            for name in ["age", "smoker"]
        ]

        binary_models = [
            _simple_binary_model(spec=spec, input_names=names)
            for spec in ["cell:add(i,i)->i", "cell:multiply(i,i)->i"]
            for names in [["age", "smoker"], ["smoker", "bmi"]]
        ]

        with self.subTest("Check for single input being included."):
            f = feyn.filters.ContainsInputs("smoker")
            self.assertEqual(3, len(list(filter(f, unary_models))))

        with self.subTest("Check all models returned if they all contain the single input."):
            f = feyn.filters.ContainsInputs("smoker")
            self.assertEqual(4, len(list(filter(f, binary_models))))

        with self.subTest("Check for list of inputs being included."):
            f = feyn.filters.ContainsInputs(["smoker", "bmi"])
            self.assertEqual(2, len(list(filter(f, binary_models))))


class TestContainsFunctions(unittest.TestCase):
    def test_contains_filter(self):
        unary_models = [
            _simple_unary_model(spec=spec)
            for spec in ["cell:gaussian(i)->i", "cell:exp(i)->i", "cell:log(i)->i"]
        ]

        unary2_models = [
            _3edge_2depth_model(spec1, spec2)
            for spec1 in ["cell:gaussian(i)->i", "cell:exp(i)->i", "cell:log(i)->i"]
            for spec2 in ["cell:gaussian(i)->i", "cell:exp(i)->i", "cell:log(i)->i"]
        ]

        with self.subTest("Check for model built with single function."):
            f = feyn.filters.ContainsFunctions("log")
            self.assertEqual(1, len(list(filter(f, unary_models))))

        with self.subTest("Check for model built with list of functions."):
            f = feyn.filters.ContainsFunctions(["log", "exp"])
            self.assertEqual(2, len(list(filter(f, unary2_models))))

        with self.subTest("Check that it only returns models that only contains the specified function."):
            f = feyn.filters.ContainsFunctions("log")
            self.assertEqual(1, len(list(filter(f, unary2_models))))


def _3edge_2depth_model(spec1: str, spec2: str) -> feyn.Model:
    res = _add_register_to_dict()
    res["nodes"].extend(
        [
            {
                "id": 1,
                "spec": spec1,
                "location": [0, -1, -1],
                "peerlocation": [0, -1, -1],
                "name": "",
                "state": {},
                "strength": 1.0,
                "legs": 2,
            },
            {
                "id": 2,
                "spec": spec2,
                "location": [0, -1, -1],
                "peerlocation": [0, -1, -1],
                "name": "",
                "state": {},
                "strength": 1.0,
                "legs": 2,
            },
            {
                "id": 3,
                "spec": "out:linear(i)->f",
                "location": [0, -1, -1],
                "peerlocation": [0, -1, -1],
                "name": "insurable",
                "state": {},
                "strength": 1.0,
                "legs": 1,
            },
        ]
    )
    res["links"] = [
        {"source": 0, "target": 1, "ord": 0},
        {"source": 1, "target": 2, "ord": 0},
        {"source": 2, "target": 3, "ord": 0},
    ]
    return feyn.Model._from_dict(res)
