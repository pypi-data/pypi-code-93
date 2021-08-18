# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring
# pylint: disable=no-self-use, protected-access
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch, call
from types import GeneratorType
import pandas
from iris_dataset.data_structures import es_data_structure


class MockDBObject():
    def __init__(self, dbtype=None):
        self.type = dbtype
        self.partial_query = None

    def update_query(self, update):
        self.partial_query = update

    def __eq__(self, other):
        return self.type == other.type and self.partial_query == other.partial_query


class TestESDataStructure(unittest.TestCase):
    def test_unserialize_data_disk(self):
        self.assertRaises(NotImplementedError, es_data_structure.ESDataStructure.unserialize, 'Test', None)

    def test_unserialize_no_db_object(self):
        self.assertRaises(NotImplementedError, es_data_structure.ESDataStructure.unserialize, None, 'something', None)

    @patch.object(es_data_structure.ESDataStructure, '__init__', return_value=None)
    def test_unserialize_db_object_no_partial_query(self, mock_init):
        es_data_structure.ESDataStructure.unserialize(None, {'test': 1}, MockDBObject('ElasticSearch'))
        mdb = MockDBObject('ElasticSearch')
        mdb.partial_query = {}
        assert mock_init.mock_calls == [call(None, {'test': 1}, mdb)]

    def test_unserialize_other_db_object(self):
        self.assertRaises(
            NotImplementedError, es_data_structure.ESDataStructure.unserialize,
            None, 'something', MockDBObject('Invalid DB'))

    def test_db_unserializer(self):
        obj = es_data_structure.ESDataStructure()
        res = obj.db_unserializer([[1, 2, 3, 4], None])
        assert isinstance(res, GeneratorType)
        assert list(res) == [1, 2, 3, 4]

    # def test_get_data(self):
    #     obj = es_data_structure.ESDataStructure()
    #     assert obj.get_data() == {}

    def test_serialize_no_index(self):
        obj = es_data_structure.ESDataStructure()
        self.assertRaises(AttributeError, obj.serialize)

    @patch('iris_dataset.data_structures.es_data_structure.create_db_object')
    @patch('iris_dataset.data_structures.es_data_structure._row_to_action')
    def test_serialize_with_index(self, mock_row_to_action, mock_create_db_object):
        obj = es_data_structure.ESDataStructure()
        obj.metadata = {'index': 'test_index'}
        df = pandas.DataFrame({'test': [1, 2, 3, 4]}).to_dict('records')
        obj.data = df
        obj.serialize()
        assert mock_create_db_object.mock_calls[0] == call(force_rewrite=False, index='test_index')
        name, args, kwargs = mock_create_db_object.mock_calls[1]
        assert name == '().bulk'
        assert kwargs == {}
        assert isinstance(args[0], map)
        actions = list(args[0])
        assert len(actions) == 4
        assert mock_row_to_action.mock_calls[0] == call('test_index', {'index': 'test_index'})
        assert len(mock_row_to_action.mock_calls) == 5
        for (i, d) in enumerate(df):
            assert (d == mock_row_to_action.mock_calls[i + 1][1][0])


    @patch('iris_dataset.data_structures.es_data_structure.create_db_object')
    @patch('iris_dataset.data_structures.es_data_structure._row_to_action')
    def test_serialize_with_index_rewrite(self, mock_row_to_action, mock_create_db_object):
        obj = es_data_structure.ESDataStructure()
        obj.metadata = {'index': 'test_index', 'rewrite': True}
        df = pandas.DataFrame({'test': [1, 2, 3, 4]}).to_dict('records')
        obj.data = df
        obj.serialize()
        assert mock_create_db_object.mock_calls[0] == call(force_rewrite=True, index='test_index')
        name, args, kwargs = mock_create_db_object.mock_calls[1]
        assert name == '().bulk'
        assert kwargs == {}
        assert isinstance(args[0], map)
        actions = list(args[0])
        assert len(actions) == 4
        assert mock_row_to_action.mock_calls[0] == call('test_index', {'index': 'test_index', 'rewrite': True})
        assert len(mock_row_to_action.mock_calls) == 5
        for (i, d) in enumerate(df):
            assert (d == mock_row_to_action.mock_calls[i + 1][1][0])
