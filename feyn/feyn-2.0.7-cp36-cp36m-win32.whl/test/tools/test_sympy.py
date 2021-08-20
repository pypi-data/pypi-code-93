import unittest
from typing import List

from feyn.tools import sympify_model
from feyn import connect_qlattice, Model

from feyn.tools._sympy import _signif

import numpy as np
import sympy


class TestTools(unittest.TestCase):

    def setUp(self) -> None:
        self.data = dict({
            'age': np.array([20, 40, 20, 20, 40, 20]),
            'smoker': np.array([0, 1, 1, 0, 1, 0]),
            'sex': np.array(['yes', 'no', 'yes', 'no', 'yes', 'no']),
            'charges': np.array([10000, 20101, 10001, 20101, 20100, 10101])
        })

    def test_signif(self):
        digits = 6

        with self.subTest('Can round floats to significant digits (rather than decimal points)'):
            num = 12345.12345

            expected = 12345.1
            actual = _signif(num, digits)

            self.assertEqual(expected, actual, "Expected signif to round properly")

        with self.subTest('Can round scientific notation as well as floats'):
            from sympy import sympify
            num = sympify(f"{12345.12345:10e}")

            expected = round(sympy.Float(12345.1), 1)
            actual = _signif(num, digits)

            assert(isinstance(actual, sympy.Float))
            self.assertEqual(expected, actual, "Expected signif to round properly")

        with self.subTest("Can round integers to significant digits"):
            num = 1234

            expected = 1230
            actual = _signif(num, 3)
            self.assertEqual(expected, actual, "Expected signif to round properly")



    def test_sympy(self):
        lt = connect_qlattice()
        lt.reset(42)

        model = _simple_binary_model()
        model.fit(self.data)

        expected = model.predict(self.data)

        signif = 15

        symp = sympify_model(model, symbolic_lr=True, signif=signif)

        actual = _predict_sympy_all(symp, self.data, model, signif)
        for e, a in zip(expected, actual):
            self.assertAlmostEqual(e, a, places=signif-5) # These places are after decimal

    def test_weightless_sympy(self):
        model = _simple_binary_model()
        model.fit(self.data)

        symp = sympify_model(model, symbolic_lr=True, include_weights=False)

        assert("age + sex_cat" == str(symp))

    def test_sympy_underscores_get_replaced(self):
        model = _simple_binary_model(input_names=['age_age', 'sex'])
        self.data['age_age'] = self.data['age']
        del self.data['age']
        model.fit(self.data)

        symp = sympify_model(model, symbolic_lr=True, include_weights=False)

        assert("ageage + sex_cat" == str(symp))

    def test_sympy_symboliclr_false(self):
        model = _simple_binary_model(out_spec='out:lr(i)->b')
        model.fit(self.data)

        symp = sympify_model(model, symbolic_lr=False, include_weights=False)

        assert("logreg(age + sex_cat)" == str(symp))

    def test_sympy_symboliclr_true(self):
        model = _simple_binary_model(out_spec='out:lr(i)->b')
        model.fit(self.data)

        symp = sympify_model(model, symbolic_lr=True, include_weights=False)

        assert("1/(exp(-age - sex_cat) + 1)" == str(symp))



def _predict_sympy_all(expr, samples, model, signif=15):
    mappings = get_mappings(model)
    predictions = []

    length = len(next(iter(samples.values())))
    for i in range(length):
        sample = {key: values[i:i+1] for key, values in samples.items()}
        prediction = expr.evalf(n=signif, subs=_prepare_args(sample, mappings))
        predictions.append(prediction)

    return predictions


def _prepare_args(sample, mappings):
    result = {}
    for col in sample.keys():
        name = col.replace(" ","")  # spaces turn to nothing
        if name in mappings:
            category_value = sample[name][0]
            result[name+"_cat"] = mappings[name][category_value]
            continue

        result[name] = sample[name][0]
    return result


def get_mappings(graph):
    mapped_categories = dict()
    for interaction in graph:
        if 'in:cat' in interaction.spec:
            mapped_categories[interaction.name] = dict(interaction.state.categories)
    return mapped_categories


def _simple_binary_model(
    output_x: int = 0,
    spec: str = "cell:add(i,i)->i",
    input_names: List[str] = ["age", "sex"],
    out_spec: str = 'out:linear(i)->f'
) -> Model:
    res = _input_model_dict(n_inputs=2, input_names=input_names)
    res["nodes"].extend(
        [
            {
                "id": 2,
                "spec": spec,
                "location": [0, -1, -1],
                "peerlocation": [0, -1, -1],
                "name": "",
                "state": {},
                "strength": 1.0,
                "legs": 2,
            },
            {
                "id": 3,
                "spec": "cell:linear(i)->i",
                "location": [0, -1, -1],
                "peerlocation": [0, -1, -1],
                "name": "",
                "state": {},
                "strength": 1.0,
                "legs": 1,
            },
            {
                "id": 4,
                "spec": out_spec,
                "location": [output_x, -1, -1],
                "peerlocation": [output_x, -1, -1],
                "name": "charges",
                "state": {},
                "strength": 1.0,
                "legs": 1,
            },
        ]
    )
    res["links"] = [
        {"source": 0, "target": 2, "ord": 1},
        {"source": 1, "target": 2, "ord": 0},
        {"source": 2, "target": 3, "ord": 0},
        {"source": 3, "target": 4, "ord": 0}
    ]
    return Model._from_dict(res)


def _input_model_dict(
    n_inputs: int = 1, input_names: List[str] = ["age", "sex"], specs: List[str] = ["in:linear(f)->i", "in:cat(c)->i"]
) -> dict:
    res = {
        "multigraph": True,
        "directed": True,
        "nodes": [
            {
                "id": 0,
                "spec": specs[0],
                "location": [0, -1, -1],
                "peerlocation": [0, -1, -1],
                "name": input_names[0],
                "state": {},
                "strength": 1.0,
                "legs": 0,
            }
        ],
        "links": [],
    }
    if n_inputs == 2:
        res["nodes"].append(
            {
                "id": 1,
                "spec": specs[1],
                "location": [0, -1, -1],
                "peerlocation": [0, -1, -1],
                "name": input_names[1],
                "state": {},
                "strength": 1.0,
                "legs": 0,
            }
        )
    return res
