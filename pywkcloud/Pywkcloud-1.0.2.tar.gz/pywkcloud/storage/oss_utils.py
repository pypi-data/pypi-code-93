#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from oss2 import Auth, Bucket
from pywkcloud.storage import StoreConfig, StorageBase
logger = logging.getLogger('OSSUtils')


class OSSUtils(StorageBase):

    def __init__(self, store_config: StoreConfig):
        super(OSSUtils, self).__init__(store_config)

    def get_auth(self):
        if not self._auth:
            self._auth = Auth(self._store_config.access_key, self._store_config.secret_key)
        return self._auth
    
    def _Bucket(self):
        q = self.get_auth()
        return Bucket(q, self._store_config.endpoint, self._store_config.bucket_name)

    def check_bucket(self, key):
        bucket = self._Bucket()
        logger.debug(key)
        # 获取文件的状态信息
        return bucket.object_exists(key)

    def upload_file(self, key, file_path):
        bucket = self._Bucket()
        ret = bucket.put_object_from_file(key, file_path, None, None)
        logger.debug(ret)
        return ret

    def delete_file(self, key):
        bucket = self._Bucket()
        ret = bucket.delete_object(key, params=None, headers=None)
        logger.debug(ret)
        return ret

    def get_file(self, key, filename):
        bucket = self._Bucket()
        return bucket.get_object_to_file(key, filename, None, None, None, None, None)


if __name__ == '__main__':
    pass
