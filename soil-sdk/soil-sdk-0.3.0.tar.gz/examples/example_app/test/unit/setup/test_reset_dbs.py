# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, no-self-use

import unittest
from unittest.mock import patch, call
from iris_dataset.setup import reset_dbs


class MockDataRef:
    def __init__(self, alias, metadata=None):
        # pylint: disable=unused-argument
        self.alias = alias
        if alias == 'employees-combinations':
            self.metadata = {'date_colname': 'Date'}

    def __eq__(self, other):
        return self.alias == other.alias


def soil_data_side_effect(alias, metadata=None):
    return MockDataRef(alias, metadata=metadata)


class TestResetDBs(unittest.TestCase):
    @patch('iris_dataset.setup.reset_dbs.soil.alias')
    @patch('iris_dataset.setup.reset_dbs.to_es_data_structure')
    @patch('iris_dataset.setup.reset_dbs.soil.data')
    def test_reset(
        self, soil_data_mock, to_es_data_structure, _mock_alias
    ):
        # pylint: disable=protected-access
        soil_data_mock.side_effect = soil_data_side_effect
        to_es_data_structure.side_effect = lambda ref: [MockDataRef('predictor')]
        reset_dbs._reset_dbs()

        expected_soil_data_calls = [call([], metadata={'index': 'simple-data', 'rewrite': True}),
                                    call([], metadata={'index': 'simple-preds', 'rewrite': True})]
        soil_data_mock.assert_has_calls(expected_soil_data_calls)
