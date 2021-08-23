#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from qiniu import Auth, put_file, zone, config, BucketManager
from pywkcloud.storage import StoreConfig, StorageBase
logger = logging.getLogger('KodoUtils')


class KodoUtils(StorageBase):

    def __init__(self, store_config: StoreConfig):
        super(KodoUtils, self).__init__(store_config)

    def get_auth(self):
        if not self._auth:
            config.set_default(connection_timeout=self._store_config.connection_timeout)
            if self._store_config.default_zone:
                config.set_default(default_zone=zone.Zone(up_host=self._store_config.default_zone))
            self._auth = Auth(self._store_config.access_key, self._store_config.secret_key)
        return self._auth

    def check_bucket(self, key):
        bucket = BucketManager(self.get_auth())
        ret, info = bucket.stat(self._store_config.bucket_name, key)
        logger.debug(key, info)
        if info.status_code == 200:
            return True
        else:
            return False

    def upload_file(self, key, file_path):
        q = self.get_auth()
        token = q.upload_token(self._store_config.bucket_name, key, 3600)
        ret, info = put_file(token, key, file_path)
        logger.debug(ret, info)
        return ret, info

    def delete_file(self, key):
        q = self.get_auth()
        bucket = BucketManager(q)
        ret, info = bucket.delete(self._store_config.bucket_name, key)
        logger.debug(ret, info)
        return ret, info

    def get_file(self, key, filename):
        from pywkmisc import HttpClientUtils
        q = self.get_auth()
        base_url = 'http://{bucket_domain}/{key}'.format(bucket_domain=self._store_config.endpoint, key=key)
        private_url = q.private_download_url(base_url)
        logger.debug(private_url)
        return HttpClientUtils.save_file(private_url, filename)


if __name__ == '__main__':
    pass
