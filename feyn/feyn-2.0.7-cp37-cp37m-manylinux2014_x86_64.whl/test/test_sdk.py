import re
import unittest
from typing import Tuple, List
import sys

import httpretty
import numpy as np
import pandas as pd
import pytest
import requests

import feyn.filters
import feyn.losses
from feyn import fit_models
from feyn._qlattice import connect_qlattice


def make_node(ix: int, spec: str, location: Tuple[int, int, int], name=""):
    return {
        "id": ix,
        "spec": spec,
        "location": list(location),
        "peerlocation": list(location),
        "name": name,
        "state": {},
    }


@pytest.mark.integration
class TestSDK(unittest.TestCase):
    def test_qlattice_init_arguments_validation(self):
        with self.subTest("raises if config is combined with qlattice or token"):
            with self.assertRaises(ValueError):
                connect_qlattice(
                    config="section", qlattice="qlattice-id", api_token="token"
                )

            with self.assertRaises(ValueError):
                connect_qlattice(config="section", qlattice="qlattice-id")

            with self.assertRaises(ValueError):
                connect_qlattice(config="section", api_token="token")

        with self.subTest("raises if only token is specified"):
            with self.assertRaises(ValueError):
                connect_qlattice(api_token="token")

        with self.subTest(
            "raises if only api_token is missing by qlattice is specified"
        ):
            with self.assertRaises(ValueError):
                connect_qlattice(qlattice="qlattice-id")

    def test_can_add_new_registers(self):
        lt = connect_qlattice()
        lt.reset()
        self.assertEqual(len(lt.registers), 0)

        # Create a model and update the QLattice to create the registers
        m = _simple_binary_model()
        lt.update(m)

        with self.subTest("Registers are available in the qlattice after addition"):
            self.assertEqual(len(lt.registers), 3)

    def test_delete_registers(self):
        lt = connect_qlattice()
        lt.reset()
        self.assertEqual(len(lt.registers), 0)

        # Create a Model and update the QLattice to create the registers
        m = _simple_binary_model()
        lt.update(m)

        with self.subTest("Registers can be deleted with del"):
            del lt.registers["age"]
            self.assertEqual(len(lt.registers), 2)

        with self.subTest("Registers can be deleted with delete"):
            lt.registers.delete("smoker")
            self.assertEqual(len(lt.registers), 1)

        with self.assertRaises(ValueError) as ex:
            lt.registers.delete("non_existing")

        self.assertIn("non_existing", str(ex.exception))

    def test_can_sample_classification_models_from_qlattice(self):
        lt = connect_qlattice()
        lt.reset()
        models = lt.sample_models(
            ["age", "smoker", "sex"], "charges", kind="classification", max_complexity=2
        )

        self.assertTrue(models)

    def test_can_sample_regression_models_from_qlattice(self):
        lt = connect_qlattice()
        lt.reset()
        models = lt.sample_models(
            ["age", "smoker", "sex"], "charges", kind="regression", max_complexity=2
        )

        self.assertTrue(models)

    def test_empty_dic_can_be_passed_to_stypes(self):
        lt = connect_qlattice()
        lt.reset()
        models = lt.sample_models(
            ["age", "smoker", "sex"],
            "charges",
            kind="regression",
            max_complexity=2,
            stypes={},
        )

        self.assertTrue(models)

    def test_fit_models(self):
        models = [_simple_binary_model()]

        data = pd.DataFrame(
            {
                "age": np.array([10, 16, 30, 60]),
                "smoker": np.array([0, 1, 0, 1]),
                "insurable": np.array([1, 1, 1, 0]),
            }
        )

        with self.subTest("Can fit with default arguments"):
            feyn.fit_models(models, data, n_samples=4)

        with self.subTest("Can fit with named loss function"):
            feyn.fit_models(models, data, loss_function="absolute_error", n_samples=4)

        with self.subTest("Can fit with loss function"):
            feyn.fit_models(
                models, data, loss_function=feyn.losses.absolute_error, n_samples=4
            )

        with self.subTest("Can fit with sample weights as list of floats"):
            feyn.fit_models(
                models, data, sample_weights=[1.0, 2.0, 3.0, 4.0], n_samples=4
            )

        with self.subTest("Can fit with sample weights as np.array"):
            feyn.fit_models(
                models, data, sample_weights=np.array([1.0, 2.0, 3.0, 4.0]), n_samples=4
            )

    def test_lattice_auto_run_works(self):
        lt = connect_qlattice()
        lt.reset()

        data = pd.DataFrame(
            {
                "age": np.array([10, 16, 30, 60]),
                "smoker": np.array([0, 1, 0, 1]),
                "insurable": np.array([1, 1, 1, 0]),
            }
        )

        best_models = lt.auto_run(
            data,
            "insurable",
            max_complexity=2,
            function_names=["exp", "log"],
            n_epochs=1,
        )
        self.assertTrue(best_models)

    @pytest.mark.focus
    def test_lattice_auto_run_validates_data(self):
        lt = connect_qlattice()
        lt.reset()

        data = pd.DataFrame(
            {
                "age": np.array([1,2,3]),
                "smoker": np.array([0,0,1]),
                "insurable": np.array([0,0.2,0.4])
            }
        )
        with self.assertRaises(ValueError):
            models = lt.auto_run(
                data,
                "insurable",
                "classification",
                max_complexity=2,
                n_epochs=1
            )

    def test_reproducible_prune(self):
        # Randomness (numpy.random) is controlled via the random_seed on the QLattice
        # Which is why we need one here
        lt = connect_qlattice()
        lt.reset(random_seed=31)
        models = [_simple_binary_model(out_x) for out_x in range(10)]
        first_pruned_models = feyn.prune_models(models)

        lt.reset(random_seed=31)
        models = [_simple_binary_model(out_x) for out_x in range(10)]
        second_pruned_models = feyn.prune_models(models)

        self.assertEqual(first_pruned_models, second_pruned_models)

    @pytest.mark.skipif(
        sys.version_info < (3, 7), reason="requires python3.7 or higher"
    )
    def test_prune_keep_n_as_npint_raises(self):
        lt = connect_qlattice()
        models = [_simple_binary_model()]
        keep_n = np.int_(5)
        with self.assertRaises(TypeError):
            feyn.prune_models(models, keep_n=keep_n)

    def test_reproducible_auto_run(self):
        lt = connect_qlattice()
        lt.reset(random_seed=31)

        data = pd.DataFrame(
            {
                "age": np.array([10, 16, 30, 60]),
                "smoker": np.array([0, 1, 0, 1]),
                "insurable": np.array([1, 1, 1, 0]),
            }
        )

        first_models = lt.auto_run(
            data,
            "insurable",
            max_complexity=1,
            function_names=["exp"],
            n_epochs=1,
        )

        lt.reset(random_seed=31)
        second_models = lt.auto_run(
            data,
            "insurable",
            max_complexity=1,
            function_names=["exp"],
            n_epochs=1,
        )

        self.assertEqual(first_models, second_models)

    def test_update_lattice_with_models(self):
        lt = connect_qlattice()
        lt.reset()
        models = lt.sample_models(
            ["age", "smoker", "insurable"], "insurable", max_complexity=2
        )

        with self.subTest("Can update with single model"):
            lt.update(models[0])

        with self.subTest("Can update with several models"):
            lt.update(models[:10])

        with self.subTest("Can update with empty list"):
            lt.update([])

    def test_can_sample_models_with_any_column_as_output(self):
        lt = connect_qlattice()
        lt.reset()
        columns = ["age", "smoker"]
        for target in columns:
            models = lt.sample_models(columns, target, max_complexity=2)
            self.assertTrue(models)

    def test_model_fitting(self):
        lt = connect_qlattice()
        lt.reset()
        models = lt.sample_models(
            ["age", "smoker", "insurable"],
            "insurable",
            max_complexity=2,
            kind="classification",
        )[:5]

        data = pd.DataFrame(
            {
                "age": np.array([10, 16, 30, 60]),
                "smoker": np.array([0, 1, 0, 1]),
                "insurable": np.array([1, 1, 1, 0]),
            }
        )

        with self.subTest("Fitted list is sorted by loss"):
            fitted_models = fit_models(models, data, n_samples=4)
            explicitly_sorted = sorted(
                [m.loss_value for m in fitted_models], reverse=False
            )
            fitted_losses = [m.loss_value for m in fitted_models]
            for esl, fl in zip(explicitly_sorted, fitted_losses):
                self.assertAlmostEqual(esl, fl)

        with self.subTest("Can provide a loss function"):
            fitted_with_ae = fit_models(
                models, data, loss_function=feyn.losses.absolute_error, n_samples=4
            )
            explicitly_sorted = sorted(
                [m.loss_value for m in fitted_with_ae], reverse=False
            )
            fitted_losses = [m.loss_value for m in fitted_with_ae]
            print(explicitly_sorted, fitted_losses)
            for esl, fl in zip(explicitly_sorted, fitted_losses):
                self.assertAlmostEqual(esl, fl)

        with self.subTest("Can provide the name of a loss function"):
            fitted_with_ae = fit_models(
                models, data, loss_function="absolute_error", n_samples=4
            )
            explicitly_sorted = sorted(
                [m.loss_value for m in fitted_with_ae], reverse=False
            )
            fitted_losses = [m.loss_value for m in fitted_with_ae]
            for esl, fl in zip(explicitly_sorted, fitted_losses):
                self.assertAlmostEqual(esl, fl)

    def test_retries_failed_updates(self):
        lt = connect_qlattice()
        lt.reset()
        models = lt.sample_models(
            ["age", "smoker", "insurable"], "insurable", max_complexity=2
        )

        with httpretty.enabled():
            # Ideally we would have liked to just mock out the update http call.
            # But it is not possible in httpretty. And at same time, we are
            # creating the socket through request.session and init time of the
            # qlattice. So this socket cannot be highjacked by httpretty.
            # See this: https://github.com/gabrielfalcao/HTTPretty/issues/381
            lt._http_client = feyn._httpclient.HttpClient("http://example.org/api")
            lt._http_client.get_adapter(
                "http://"
            ).max_retries.backoff_factor = 0.1  # Instant retries

            httpretty.register_uri(httpretty.POST, re.compile(r"http://.*"), status=502)

            with self.assertRaisesRegex(requests.exceptions.HTTPError, "502"):
                lt.update(models[0])

            self.assertEqual(
                len(httpretty.latest_requests()), 3, "Did not retry the failed requests"
            )

    def test_DataFrame_as_input_names(self):
        lt = connect_qlattice()
        lt.reset()
        input_names = pd.DataFrame(
            {"smoker": [1, 2, 3, 4], "age": [5, 6, 7, 10], "target": [6, 8, 10, 12]}
        )
        output_name = "target"

        models = lt.sample_models(input_names, output_name)
        self.assertIsNotNone(models[0])


def _simple_unary_model(
    output_x: int = 0,
    spec: str = "cell:exp(i)->i",
    input_name: str = "age",
    stype: str = None,
    state: dict = None,
) -> feyn.Model:

    res = _add_register_to_dict(input_name, stype, state)
    # res = _input_model_dict(n_inputs=1, input_names=[input_name])

    cell_state = {}

    if spec == "cell:linear(i)->i":
        cell_state = {"scale": 1, "w0": 1, "bias": 0}

    res["nodes"].extend(
        [
            {
                "id": 1,
                "spec": spec,
                "location": [0, -1, -1],
                "peerlocation": [0, -1, -1],
                "name": "",
                "state": cell_state,
                "strength": 1.0,
                "legs": 2,
            },
            {
                "id": 2,
                "spec": "out:linear(i)->f",
                "location": [output_x, -1, -1],
                "peerlocation": [output_x, -1, -1],
                "name": "insurable",
                "state": {"scale": 1, "w": 1, "bias": 0},
                "strength": 1.0,
                "legs": 1,
            },
        ]
    )
    res["links"] = [
        {"source": 0, "target": 1, "ord": 0},
        {"source": 1, "target": 2, "ord": 0},
    ]
    return feyn.Model._from_dict(res)


def _simple_binary_model(
    output_x: int = 0,
    spec: str = "cell:add(i,i)->i",
    input_names: List[str] = ["age", "smoker"],
    stypes: dict = {},
    states: dict = {},
) -> feyn.Model:

    res = {}
    for name in input_names:
        if not name in stypes:
            stypes[name] = None
        if not name in states:
            states[name] = None
        res = _add_register_to_dict(name, stypes[name], states[name], res)

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
                "spec": "out:linear(i)->f",
                "location": [output_x, -1, -1],
                "peerlocation": [output_x, -1, -1],
                "name": "insurable",
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
    ]
    return feyn.Model._from_dict(res)


def _simple_tertiary_model(
    output_x: int = 0,
    input_names: List[str] = ["age", "smoker", "children"],
    stypes: dict = {},
    states: dict = {},
):
    res = {}
    for name in input_names:
        if not name in stypes:
            stypes[name] = None
        if not name in states:
            states[name] = None
        res = _add_register_to_dict(name, stypes[name], states[name], res=res)

    spec = "cell:add(i,i)->i"

    res["nodes"].extend(
        [
            {
                "id": 3,
                "spec": spec,
                "location": [0, -1, -1],
                "peerlocation": [0, -1, -1],
                "name": "",
                "state": {},
                "strength": 1.0,
                "legs": 2,
            },
            {
                "id": 4,
                "spec": spec,
                "location": [0, -1, -1],
                "peerlocation": [0, -1, -1],
                "name": "",
                "state": {},
                "strength": 1.0,
                "legs": 2,
            },
            {
                "id": 5,
                "spec": "out:linear(i)->f",
                "location": [output_x, -1, -1],
                "peerlocation": [output_x, -1, -1],
                "name": "insurable",
                "state": {},
                "strength": 1.0,
                "legs": 1,
            },
        ]
    )

    res["links"] = [
        {"source": 0, "target": 3, "ord": 0},
        {"source": 1, "target": 3, "ord": 1},
        {"source": 3, "target": 4, "ord": 0},
        {"source": 2, "target": 4, "ord": 1},
        {"source": 4, "target": 5, "ord": 0},
    ]
    model = feyn.Model._from_dict(res)

    return feyn.Model._from_dict(res)


def _add_register_to_dict(
    input_name: str = "age", stype=None, state=None, res=None
) -> dict:
    if not stype or stype == "f":
        spec = "in:linear(f)->i"

    if stype == "c":
        spec = "in:cat(c)->i"

    if not state:
        state = {}

    node = {
        "spec": spec,
        "location": [0, -1, -1],
        "peerlocation": [0, -1, -1],
        "name": input_name,
        "state": state,
        "strength": 1.0,
        "legs": 0,
    }

    if not res:
        node["id"] = 0
        res = {"multigraph": True, "directed": True, "nodes": [], "links": []}
        res["nodes"].append(node)
    else:
        node["id"] = len(res["nodes"])
        res["nodes"].append(node)
    return res
