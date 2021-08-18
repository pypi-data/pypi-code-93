# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, no-self-use
import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch
from sklearn.ensemble import RandomForestClassifier
from soil.data_structures.random_forest_model import RandomForestModel
from iris_dataset.modules import retrain_predictor
from .patch_decorators import patch_modulify


metadata = {
    "_id": "_id",
    "columns": {
        "X_columns": {
            "sepal_length": {
                "name": "sepal_length",
                        "type": "float"
            },
            "sepal_width": {
                "name": "sepal_width",
                        "type": "float"
            },
            "petal_length": {
                "name": "petal_length",
                        "type": "float"
            },
            "petal_width": {
                "name": "petal_width",
                        "type": "float"
            }
        },
        "y_columns": {
            "species": {
                "name": "species",
                        "type": "str"
            }
        }
    }
}


class InputDS:
    def __init__(self, data, metadata=None):
        self.data = data
        self.metadata = metadata if metadata is not None else {}


class TestModulifiedRetrainPredictor(unittest.TestCase):
    def test_output_types(self):
        # This is a bit hacky but in tests it's fine.
        output_types_fn = retrain_predictor.retrain_predictor.__closure__[-1].cell_contents
        assert output_types_fn() == [RandomForestModel]


@patch_modulify(retrain_predictor)
class TestRetrainPredictor(unittest.TestCase):
    @patch('iris_dataset.modules.retrain_predictor.RandomForestModel')
    def test_retrain_predictor(self, mocked_rfmodel):
        np.random.seed(1111)
        mocked_rfmodel.return_value = 'ok'
        fixture = pd.read_csv('./data/iris.csv')
        dataset = InputDS(fixture, metadata)
        [result] = retrain_predictor.retrain_predictor(dataset)
        assert result == 'ok'
        assert len(mocked_rfmodel.call_args_list) == 1
        args, _kwargs = mocked_rfmodel.call_args_list[0]
        assert len(args) == 2
        assert type(args[0]) == RandomForestClassifier
        assert args[0].oob_score
        assert args[1] == {
            'oob_score': 0.9466666666666667,
            'error': 0.053333333333333344,
            'x_labels': metadata['columns']['X_columns'],
            'y_labels': {'species': {'name': 'species', 'type': 'str'}}

        }
