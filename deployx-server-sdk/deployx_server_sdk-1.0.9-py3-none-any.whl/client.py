import logging
from typing import Type
from urllib.parse import urlparse
from urllib3 import HTTPConnectionPool, HTTPSConnectionPool, request
from .store import FeatureFlagStore
import json
import urllib3

class DXClient:

    def __init__(self, config):
        self.config = config

        logging.info('Start Pool connection to host.')
        options = {'timeout': 0.0000001, 'retries': 0}
        if not self.config.debug:
            self.pool = HTTPSConnectionPool(self.config.api_url, **options)
        else:
            self.pool = HTTPConnectionPool(self.config.api_url, port=self.config.api_port, **options)
        # initializate redis database
        self.store = FeatureFlagStore()


    def get_flag(self, flag_key, user, default=None, client_debug=False):
        self.flag_key = flag_key
        self.default = default
        self.client_debug = client_debug
        self.user = user

        if not self.config.offline:
            try:
                r = self.pool.request('PUT', 
                                    '/api/client/v1/get_point/{}/{}/'.format(self.config.sdk_key, self.flag_key),
                                    headers={'Content-Type': 'application/json'},
                                    body=json.dumps(user),
                                    timeout=1)
                data = json.loads(r.data)

                if r.status == 200:
                    self.ready_status = self.store.decode_status(data)

                    if hasattr(self.store, 'redis_db') and self.store.redis_db:
                        self.store.init_user(self.config, user, self.flag_key)
                        self.store.save(self.ready_status)


                    return self.ready_status

                elif r.status == 400:
                    raise TypeError(r.data)
                elif r.status == 500:
                    raise ConnectionError("Error when try to connect to server.")
                    # TODO Добавить логику перевода клиента в статус offline
            except urllib3.exceptions.MaxRetryError:
                self.config.offline = True
                logging.info("deploy-x.com connection lost or have trouble with internet connection. Offline mode was set On")
                return self._processing_network_error()

        elif self.config.offline:
            return self._processing_network_error()

    def _processing_network_error(self):
        """
        when we already have offline mode or get first error
        we have to check client_debug and based on this return redis or default value
        """
        if self.client_debug:
            final_result = self._get_default_value()
            if final_result is None:
                final_result = self._get_redis_value()
            if final_result is None:
                raise AttributeError('You have to add default value for dxclient.get function or install redis cache.')
            return final_result
        else:
            final_result = self._get_redis_value()
            if final_result is None:
                final_result = self._get_default_value()
            if final_result is None:
                raise AttributeError('You have to add default value for dxclient.get function or install redis cache.')
            return final_result


    def _get_default_value(self):
        if self.default:
            logging.info('Offline. Return default value')
            return self.default
        return None


    def _get_redis_value(self):
        if self.store.redis_db:
            user_unique = '-'
            if 'unique_identifier' in self.user:
                user_unique = self.user['unique_identifier']
            elif 'UNIQUE_IDENTIFIER' in self.user:
                user_unique = self.user['UNIQUE_IDENTIFIER']

            status = self.store.r.hget(user_unique, '{}_{}'.format(self.config.sdk_key, self.flag_key))
            if status:
                logging.info('Offline. Get value from redis')
                return self.store.decode_byte_status(status)
        return None



    def close(self):
        if self.pool.num_connections:
            self.pool.close()
        logging.info('Closing connection in initialized client instance.')
