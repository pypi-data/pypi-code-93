import json
import os
import uuid
import unittest
import warnings

import boto3
import syngenta_digital_dta


class S3AdapterTest(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        warnings.simplefilter('ignore', ResourceWarning)
        self.maxDiff = None
        self.bucket = 'unit-test'
        self.endpoint = 'http://localhost:4566'
        self.file = open('./tests/mock/example.json')
        self.__create_unit_test_bucket()
        self.adapter = syngenta_digital_dta.adapter(
            engine='s3',
            endpoint=self.endpoint,
            bucket=self.bucket
        )

    def __create_unit_test_bucket(self):
        try:
            s3_client = boto3.client('s3', endpoint_url=self.endpoint)
            s3_client.create_bucket(Bucket=self.bucket)
        except:
            pass

    def test_init(self):
        self.assertIsInstance(self.adapter, syngenta_digital_dta.S3Adapter)

    def test_create(self):
        results = self.adapter.create(
            s3_path='test/test-create.json',
            data={'test': True},
            json=True
        )
        self.assertEqual(results['ResponseMetadata']['HTTPStatusCode'], 200)

    def test_read(self):
        data = {'test': True}
        s3_path = 'test/test-read.json'
        self.adapter.create(
            s3_path=s3_path,
            data=data,
            json=True
        )
        result = self.adapter.read(
            s3_path=s3_path,
            json=True
        )
        self.assertDictEqual(data, result)

    def test_delete(self):
        s3_path = 'test/test-delete.json'
        self.adapter.create(
            s3_path=s3_path,
            data={'test': True},
            json=True
        )
        results = self.adapter.delete(s3_path=s3_path)
        self.assertEqual(results['ResponseMetadata']['HTTPStatusCode'], 204)

    def test_download(self):
        s3_path = 'test/test-download.json'
        data = {'test': True}
        self.adapter.create(
            s3_path=s3_path,
            data=data,
            json=True
        )
        download_path='/tmp/unit-test-download/test.json'
        self.adapter.download(s3_path=s3_path, download_path=download_path)
        with open(download_path) as json_file:
            json_dict = json.load(json_file)
        self.assertEqual(True, os.path.exists(download_path))
        self.assertDictEqual(json_dict, data)

    def test_object_exist_true(self):
        s3_path = 'test/test_is_exist_true.json'
        self.adapter.create(
            s3_path=s3_path,
            data={'test': True},
            json=True
        )

        result = self.adapter.object_exist(s3_path=s3_path)

        self.assertEqual(result, True)

    def test_object_exist_false(self):
        s3_path = 'test/test_is_exist_false.json'

        result = self.adapter.object_exist(s3_path=s3_path)

        self.assertEqual(result, False)

    def __read_in_chunks(self):
        return self.file.read(6000000)

    def test_multipart_upload(self):
        chunks = []
        for piece in iter(self.__read_in_chunks, ''):
            chunks.append(piece)
        s3_path = 'test/test-multipart.json'
        results = self.adapter.multipart_upload(chunks=chunks, s3_path=s3_path)
        self.assertEqual(results['ResponseMetadata']['HTTPStatusCode'], 200)
        self.assertEqual(results['Location'], 'http://localhost:4566/unit-test/test/test-multipart.json')

    def test_create_presigned_read_url(self):
        s3_path = 'test/test-presigned-url.json'
        self.adapter.create(
            s3_path=s3_path,
            data={'test': True},
            json=True
        )
        result = self.adapter.create_presigned_read_url(s3_path=s3_path, expiration=3600)
        self.assertEqual(True, s3_path in result)

    def test_create_presigned_post_url(self):
        s3_path = 'test/test-presigned-url.json'
        result = self.adapter.create_presigned_post_url(s3_path=s3_path, expiration=3600)
        self.assertEqual(True, self.bucket in result['url'])
