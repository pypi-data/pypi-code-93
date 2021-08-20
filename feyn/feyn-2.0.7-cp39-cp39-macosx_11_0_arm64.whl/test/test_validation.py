import numpy as np
import pandas as pd
import pytest
import sys

from feyn._sgdtrainer import fit_models
from feyn._qlattice import connect_qlattice
from feyn._selection import prune_models
from feyn._selection import best_diverse_models
from feyn._validation import _validate_categorical_stypes, _validate_bool_values

from .test_sdk import _simple_binary_model

from .classes import ErrorTestCase


class TestSampleModelsValueErrors(ErrorTestCase):
    def setUp(self):
        self.ql = connect_qlattice()
        self.ql.reset()
        self.input_names = ["hello", "hola"]
        self.output_name = "apples"

    def test_input_names_raise_value_error_if_empty_list(self):
        with self.assertRaises(ValueError) as ctx:
            input_names = []
            self.ql.sample_models(input_names, self.output_name, max_complexity=1)
        self.assertEqual("input_names cannot be empty.", str(ctx.exception))

    def test_max_complexity_raises_value_error_when_negative(self):
        with self.assertRaisesAndContainsMessage(ValueError, "max_complexity"):
            mc = -10
            self.ql.sample_models(self.input_names, self.output_name, max_complexity=mc)

    def test_kind_validation(self):
        with self.assertRaisesAndContainsMessage(ValueError, "kind"):
            kind = "hello"
            self.ql.sample_models(
                input_names=self.input_names,
                output_name=self.output_name,
                kind=kind,
                max_complexity=1,
            )

    def test_function_names_raises_value_error_on_bad_function_names(self):
        with self.assertRaisesAndContainsMessage(
            ValueError, "not a valid function name"
        ):
            fnames = ["multiply", "hello"]
            self.ql.sample_models(
                input_names=self.input_names,
                output_name=self.output_name,
                max_complexity=1,
                function_names=fnames,
            )


class TestPruneModelsValueErrorValidation(ErrorTestCase):
    def setUp(self):
        self.model = _simple_binary_model()

    def test_keep_n_raises_valueerror_when_negative(self):
        with self.assertRaisesAndContainsMessage(ValueError, "keep_n"):
            keep_n = -5
            prune_models([self.model], keep_n=keep_n)

    def test_models_raises_valueerror_when_empty(self):
        with self.assertRaisesAndContainsMessage(ValueError, "Empty list of models"):
            prune_models([])


class TestBestDiverseModelsValueErrorValidation(ErrorTestCase):
    def test_models_raises_valueerror_when_empty(self):
        with self.assertRaisesAndContainsMessage(ValueError, "Empty list of models"):
            best_diverse_models([])


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
class TestSampleModelsTypeErrors(ErrorTestCase):
    def setUp(self):
        self.ql = connect_qlattice()
        self.ql.reset()
        self.input_names = ["hello", "hola"]
        self.output_name = "apples"

    def test_input_names_validation(self):
        with self.subTest("TypeError if input_names is not an iterable"):
            with self.assertRaisesTypeErrorAndContainsParam("input_names"):
                input_names = 45
                self.ql.sample_models(input_names, self.output_name, max_complexity=1)

        with self.subTest("TypeError if input_names is iterable with mix of strings"):
            with self.assertRaisesTypeErrorAndContainsParam("input_names"):
                input_names = [45, "hello"]
                self.ql.sample_models(input_names, self.output_name, max_complexity=1)

        with self.subTest("ValueError if input_names contains duplicates"):
            with self.assertRaisesAndContainsMessage(ValueError, "input_names"):
                input_names = ["smoker", "smoker", "smoker"]
                self.ql.sample_models(input_names, self.output_name, max_complexity=1)

    def test_output_name_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("output_name"):
            output_name = 42
            self.ql.sample_models(self.input_names, output_name, max_complexity=1)

    def test_max_complexity_validation(self):
        with self.subTest("TypeError if max_complexity is not a integer"):
            with self.assertRaisesTypeErrorAndContainsParam("max_complexity"):
                mc = 3.5
                self.ql.sample_models(
                    self.input_names, self.output_name, max_complexity=mc
                )

    def test_query_string_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("query_string"):
            query_str = 42
            self.ql.sample_models(
                input_names=self.input_names,
                output_name=self.output_name,
                max_complexity=1,
                query_string=query_str,
            )

    def test_function_names_validation(self):
        with self.subTest("TypeError when function names is not a list"):
            with self.assertRaisesTypeErrorAndContainsParam("function_names"):
                fnames = "hello"

                self.ql.sample_models(
                    input_names=self.input_names,
                    output_name=self.output_name,
                    max_complexity=1,
                    function_names=fnames,
                )

        with self.subTest("TypeError when function names is not a list of strings"):
            with self.assertRaisesTypeErrorAndContainsParam("function_names"):
                fnames = [42, "hello"]

                self.ql.sample_models(
                    input_names=self.input_names,
                    output_name=self.output_name,
                    max_complexity=1,
                    function_names=fnames,
                )

    def test_stypes_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("stypes"):
            stypes = {"hello": 3}

            self.ql.sample_models(
                input_names=self.input_names,
                output_name=self.output_name,
                max_complexity=1,
                stypes=stypes,
            )


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
class TestFitModelsValidation(ErrorTestCase):
    def setUp(self):
        self.data = pd.DataFrame(
            {
                "apples": [1, 2, 3, 4],
                "bananas": ["a", "nice", "cat", "feature"],
                "target": [0, 1, 0, 0],
            }
        )
        self.model = _simple_binary_model()
        self.n_samples = 3

    def test_models_validation(self):
        with self.subTest("TypeError when models is not a list"):
            with self.assertRaisesTypeErrorAndContainsParam("models"):
                fit_models(self.model, self.data, n_samples=self.n_samples)

        with self.subTest("TypeError when models is not a list of feyn.models"):
            with self.assertRaisesTypeErrorAndContainsParam("models"):
                models = ["hello"]
                fit_models(models, self.data)

    def test_data_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("data"):
            data = {"a": np.array([1, 2, 3]), "target": np.array([0, 1, 1])}
            fit_models([self.model], data, n_samples=self.n_samples)

    def test_n_samples_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("n_samples"):
            n_samples = 5.5
            fit_models([self.model], self.data, n_samples=n_samples)

    def test_sample_weights_validation(self):
        with self.subTest("TypeError when sample weights is not an iterable of floats"):
            with self.assertRaisesTypeErrorAndContainsParam("sample_weights"):
                fit_models(
                    [self.model],
                    self.data,
                    n_samples=self.n_samples,
                    sample_weights=[3.0, "hello"],
                )

        with self.subTest(
            "ValueError when length of sample weights does not match length of data"
        ):
            with self.assertRaisesAndContainsMessage(ValueError, "sample_weights"):
                fit_models(
                    [self.model],
                    self.data,
                    n_samples=self.n_samples,
                    sample_weights=[1.0],
                )

    def test_threads_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("threads"):
            threads = 4.5
            fit_models(
                [self.model], self.data, n_samples=self.n_samples, threads=threads
            )

    def test_immutable_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("immutable"):
            immutable = 42
            fit_models(
                [self.model], self.data, n_samples=self.n_samples, immutable=immutable
            )


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
class TestPruneModelsTypeErrorValidation(ErrorTestCase):
    def setUp(self):
        self.model = _simple_binary_model()

    def test_models_validation(self):
        with self.subTest("TypeError when models is not a list"):
            with self.assertRaisesTypeErrorAndContainsParam("models"):
                prune_models(self.model)

        with self.subTest("TypeError when models is not a list of feyn.models"):
            with self.assertRaisesTypeErrorAndContainsParam("models"):
                models = ["hello"]
                prune_models(models)

    def test_dropout_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("dropout"):
            dropout = "hello"
            prune_models([self.model], dropout=dropout)

    def test_decay_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("decay"):
            decay = "hello"
            prune_models([self.model], decay=decay)

    def test_keep_n_validation(self):
        with self.subTest("TypeError when keep_n is not an integer"):
            with self.assertRaisesTypeErrorAndContainsParam("keep_n"):
                keep_n = 5.5
                prune_models([self.model], keep_n=keep_n)


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
class TestBestDiverseModelsValidation(ErrorTestCase):
    def setUp(self):
        self.models = [_simple_binary_model(out_x) for out_x in range(10)]

    def test_distance_func_validation(self):
        with self.subTest("TypeError when distance function is not callable"):
            with self.assertRaisesTypeErrorAndContainsParam("distance_func"):
                distance_func = ["banana"]
                best_diverse_models(self.models, distance_func=distance_func)

        with self.subTest("TypeError when distance function does not return boolean"):
            with self.assertRaisesTypeErrorAndContainsParam("distance_func"):
                distance_func = lambda x, y: x
                best_diverse_models(self.models, distance_func=distance_func)

    def test_n_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("n"):
            n = "banana"
            best_diverse_models(self.models, n=n)


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
class TestUpdateValidation(ErrorTestCase):
    def setUp(self):
        self.ql = connect_qlattice()
        self.ql.reset()

    def test_update_validation(self):
        with self.assertRaisesTypeErrorAndContainsParam("models"):
            models = ["bananas"]
            self.ql.update(models)


class TestDataValidation(ErrorTestCase):
    def test_validate_stype_categorical(self):
        df = pd.DataFrame({"A": ["test"]})
        with self.subTest("ValueError when data object column is not specified as categorical in stypes"):
            stypes = None
            with self.assertRaisesAndContainsMessage(ValueError, "stypes"):
                _validate_categorical_stypes(df, stypes=stypes)

        with self.subTest("Success case"):
            stypes = {"A": "c"}
            _validate_categorical_stypes(df, stypes=stypes)

    def test_regression_target_non_numerical_values(self):
        from feyn._validation import _validate_regression_target_non_numerical_values

        df = pd.DataFrame({"target": [1, "banana"]})
        with self.subTest(
            "ValueError when target column has non-numerical values in a regression case"
        ):
            with self.assertRaisesAndContainsMessage(ValueError, "target"):
                _validate_regression_target_non_numerical_values(df, "target")

    def test_validate_bool_values(self):
        df = pd.DataFrame({"target": [0, 0.123, 0.7, 1]})
        with self.subTest("ValueError when target is not bool"):
            self.assertFalse(_validate_bool_values(df["target"]))

        df = pd.DataFrame({"target": [0, 0.0, False, 1, 1.0, True]})
        with self.subTest("Success"):
            self.assertTrue(_validate_bool_values(df["target"]))

    def test_validate_nan_values(self):
        from feyn._validation import validate_data

        with self.subTest("Success if Nan value is in a categorical feature"):
            df = pd.DataFrame({"x": [None, "a", "b"], "y": [1,2,3]})
            self.assertIsNone(validate_data(df, kind="regression", output_name="y", stypes={"x": "c"}))

        with self.subTest("ValueError if Nan value is in a numerical feature"):
            df = pd.DataFrame({"x": [None, 1, 2], "y": [1,2,3]})
            with self.assertRaisesAndContainsMessage(ValueError, "Nan values"):
                validate_data(df, kind="regression", output_name="y")