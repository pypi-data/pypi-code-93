import unittest
import warnings

import boto3

import syngenta_digital_dta
from tests.syngenta_digital_dta.dynamodb.mock_table import MockTable


class DynamoDBAdapterTest(unittest.TestCase):

    def setUp(self, *args, **keywargs):
        TABLE_NAME='unittestsort'
        warnings.simplefilter('ignore', ResourceWarning)
        self.maxDiff = None
        self.mock_table = MockTable(table_name=TABLE_NAME)
        self.mock_table.setup_test_table()
        self.adapter = syngenta_digital_dta.adapter(
            engine='dynamodb',
            table=TABLE_NAME,
            endpoint='http://localhost:4000',
            model_schema='test-dynamo-model',
            model_schema_file='tests/openapi.yml',
            model_identifier='test_id',
            model_version_key='modified'
        )

    def test_adapter_read(self):
        data = self.adapter.read(
            operation='get',
            query={
                'Key': {
                    'test_id': 'abc123',
                    'test_query_id': 'def345'
                }
            }
        )
        self.assertDictEqual(data, self.mock_table.mock_data)

    def test_adapter_read_scan(self):
        data = self.adapter.read(operation='scan')
        self.assertEqual(len(data), len(data))

    def test_adapter_get(self):
        data = self.adapter.get(
            query={
                'Key': {
                    'test_id': 'abc123',
                    'test_query_id': 'def345'
                }
            }
        )
        self.assertDictEqual(data, self.mock_table.mock_data)

    def test_adapter_read_query(self):
        data = self.adapter.read(
            operation='query',
            query={
                'IndexName': 'test_query_id',
                'Limit': 1,
                'KeyConditionExpression': 'test_query_id = :test_query_id',
                'ExpressionAttributeValues': {
                    ':test_query_id': 'def345'
                }
            }
        )
        self.assertDictEqual(data[0], self.mock_table.mock_data)

    def test_adapter_query(self):
        data = self.adapter.query(
            query={
                'IndexName': 'test_query_id',
                'Limit': 1,
                'KeyConditionExpression': 'test_query_id = :test_query_id',
                'ExpressionAttributeValues': {
                    ':test_query_id': 'def345'
                }
            }
        )
        self.assertDictEqual(data[0], self.mock_table.mock_data)

    def test_adapter_scan(self):
        data = self.adapter.scan()
        self.assertDictEqual(data[0], self.mock_table.mock_data)

    def test_adapter_create(self):
        new_data = {
            'test_id': 'abc456',
            'test_query_id': 'def789',
            'object_key': {
                'string_key': 'nothing'
            },
            'array_number': [1, 2, 3],
            'array_objects': [
                {
                    'array_string_key': 'a',
                    'array_number_key': 1
                }
            ],
            'created': '2020-10-05',
            'modified': '2020-10-05'
        }
        data = self.adapter.create(
            data=new_data
        )
        self.assertDictEqual(data, new_data)

    def test_adapter_overwrite(self):
        new_data = {
            'test_id': 'abc456',
            'test_query_id': 'def789',
            'object_key': {
                'string_key': 'nothing'
            },
            'array_number': [1, 2, 3],
            'array_objects': [
                {
                    'array_string_key': 'a',
                    'array_number_key': 1
                }
            ],
            'created': '2020-10-05',
            'modified': '2020-10-05'
        }
        data = self.adapter.create(
            operation='overwrite',
            data=new_data
        )
        self.assertDictEqual(data, new_data)

    def test_adapter_create_ignore_key(self):
        new_data = {
            'test_id': 'abc456',
            'test_query_id': 'def789',
            'ignore_key': True,
            'object_key': {
                'string_key': 'nothing'
            },
            'array_number': [1, 2, 3],
            'array_objects': [
                {
                    'array_string_key': 'a',
                    'array_number_key': 1
                }
            ],
            'created': '2020-10-05',
            'modified': '2020-10-05'
        }
        data = self.adapter.create(
            data=new_data
        )
        new_data.pop('ignore_key', None)
        self.assertDictEqual(data, new_data)

    def test_adapter_update(self):
        new_data = {
            'test_id': 'abc456-update',
            'test_query_id': 'def789',
            'object_key': {
                'string_key': 'nothing'
            },
            'array_number': [1, 2, 3],
            'array_objects': [
                {
                    'array_string_key': 'a',
                    'array_number_key': 1
                }
            ],
            'created': '2020-10-05',
            'modified': '2020-10-05'
        }
        data = self.adapter.create(
            data=new_data
        )
        self.assertDictEqual(data, new_data)
        new_data['array_number'] = [1, 2, 3, 4]
        updated_data = self.adapter.update(
            data=new_data,
            operation='get',
            query={
                'Key': {
                    'test_id': 'abc456-update',
                    'test_query_id': 'def789'
                }
            }
        )
        self.assertDictEqual(updated_data, new_data)

    def test_adapter_delete(self):
        new_data = {
            'test_id': 'abc456-delete',
            'test_query_id': 'def789',
            'object_key': {
                'string_key': 'nothing'
            },
            'array_number': [1, 2, 3],
            'array_objects': [
                {
                    'array_string_key': 'a',
                    'array_number_key': 1
                }
            ],
            'created': '2020-10-05',
            'modified': '2020-10-05'
        }
        data = self.adapter.create(
            data=new_data
        )
        self.adapter.delete(
            query={
                'Key': {
                    'test_id': 'abc456-delete',
                    'test_query_id': 'def789'
                }
            }
        )
        deleted_data = self.adapter.get(
            query={
                'Key': {
                    'test_id': 'abc456-delete',
                    'test_query_id': 'def789'
                }
            }
        )
        self.assertDictEqual(deleted_data, {})
