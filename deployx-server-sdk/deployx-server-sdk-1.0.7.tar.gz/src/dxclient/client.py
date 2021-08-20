import logging
from urllib3 import HTTPConnectionPool, HTTPSConnectionPool
from .store import FeatureFlagStore
import json
import urllib3

class DXClient:

    def __init__(self, config):
        self.config = config

        logging.info('Start Pool connection to host.')
        if not self.config.debug:
            self.pool = HTTPSConnectionPool(self.config.api_url)
        else:
            self.pool = HTTPConnectionPool(self.config.api_url, port=self.config.api_port)
        # initializate redis database
        self.store = FeatureFlagStore()


    def get_flag(self, flag_key, user, default=None):
        self.flag_key = flag_key

        try:
            r = self.pool.request('PUT', 
                                '/api/client/v1/get_point/{}/{}/'.format(self.config.sdk_key, self.flag_key),
                                headers={'Content-Type': 'application/json'},
                                body=json.dumps(user))
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
            logging.info("deploy-x.com connection lost or have trouble with internet connection.")
            if self.store.redis_db:
                status = self.store.r.hget(user['unique_identifier'] or user['UNIQUE_IDENTIFIER'] or '-', '{}_{}'.format(self.config.sdk_key, flag_key))
                if status:
                    logging.info("Got last value of flag from redis db.")
                    return self.store.decode_byte_status(status)
                else:
                    logging.info("Can\'t get status from redis database, use default status.")
                    return default


    def close(self):
        if self.pool.num_connections:
            self.pool.close()
        logging.info('Closing connection in initialized client instance.')
