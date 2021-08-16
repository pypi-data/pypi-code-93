import hashlib
import logging
import os
import shutil
import threading
from enum import Enum
from typing import Optional

import requests
import ujson
from envparse import env

logger = logging.getLogger('default')


class EnumsClient:
    __slots__ = ('_data', '_url', '_hash_sum', '_timeout', '_cache_file', '_is_mocked')

    def __init__(self, url, timeout, is_mocked=False, cache_file=None, fetch_interval=60):
        self._url = url
        self._timeout = timeout
        self._data = dict()
        self._hash_sum = None
        self._is_mocked = is_mocked
        self._cache_file = self._create_cache_file(cache_file) if is_mocked else None

        if is_mocked:
            self.update_from_cache()
        else:
            self.update_from_remote_periodic(fetch_interval)

    def __getattr__(self, item):
        if item in self._data:
            return self._data[item]
        if self._is_mocked:
            raise AttributeError(f'Enum `{item}` can not be fetched when `MOCK` is enabled.')
        updated = self.update_from_remote()
        if not updated:
            raise AttributeError(f'No changes from the remote. Enum `{item}` not found.')
        if item not in self._data:
            raise AttributeError(f'Remote changes were received, but they do not contain `{item}`.')
        return self._data[item]

    @staticmethod
    def _create_cache_file(file_path: Optional[str]):
        if not file_path:
            file_path = '/cache/enums.json'
        cache_file = os.path.join(os.getcwd(), *file_path.split('/'))
        if not os.path.exists(cache_file):
            logger.warning(
                "You're using `REFERENCES_MOCK` without providing cache file.\n"
                "It will be automatically create with data from template.\n"
                "Now you can manually add or change any enums in %s" % cache_file
            )
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            src = os.path.join(os.path.dirname(__file__), 'datafiles/enums_template.json')
            shutil.copy(src, cache_file)
        return cache_file

    @staticmethod
    def _create_enums_values(data: dict) -> dict:
        return {k: data[k] if data[k] is not None else k.lower() for k in data}

    @staticmethod
    def _get_hash(text) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def update_from_remote(self) -> bool:
        text = self.fetch_remote()
        hash_sum = self._get_hash(text)
        if self._hash_sum == hash_sum:
            return False
        self._data = self.deserialize(text)
        self._hash_sum = hash_sum
        return True

    def update_from_cache(self) -> bool:
        with open(self._cache_file) as f:
            text = f.read()
        self._data = self.deserialize(text)
        self._hash_sum = self._get_hash(text)
        return True

    def fetch_remote(self) -> str:
        try:
            response = requests.get(url=self._url, timeout=self._timeout)
            if not (200 <= response.status_code < 400):
                raise ConnectionError(f'Bad status code, expected `200`, got {response.status_code}')
            return response.text
        except Exception as err:
            logger.exception('Exception while connecting to references service.\n'
                             f'REFERENCES_HOST_URL: {self._url}, REFERENCES_TIMEOUT: {self._timeout}.\n'
                             f'Original exception: {err}')
            raise ConnectionError

    def deserialize(self, text: str) -> dict:
        return {ref['name']: Enum(ref['name'], self._create_enums_values(ref['data']))
                for ref in ujson.loads(text)}

    def update_from_remote_periodic(self, fetch_interval):
        self.update_from_remote()
        stop = threading.Event()

        def inner_wrap():
            while not stop.isSet():
                stop.wait(fetch_interval)
                try:
                    self.update_from_remote()
                except Exception as err:
                    logger.exception(f'Exception in the periodic task. Original: {err}.')

        t = threading.Timer(0, inner_wrap)
        t.daemon = True
        t.start()


def _initialize() -> EnumsClient:
    path = env.str('REFERENCES_ENUMS_PATH', default='/api/v1/pages/?directory__name=enums')
    timeout = env.int('REFERENCES_TIMEOUT', default=1)
    url = env.str('REFERENCES_HOST_URL').rstrip('/') + path
    is_mocked = env.bool('REFERENCES_MOCK', default=False)
    cache_file = env.str('REFERENCES_MOCK_FILE', default=None)
    fetch_interval = env.int('REFERENCES_FETCH_INTERVAL', default=60)
    return EnumsClient(url, timeout, is_mocked, cache_file, fetch_interval)


enums = _initialize()
