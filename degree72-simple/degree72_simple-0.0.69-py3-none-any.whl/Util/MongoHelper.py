import os
import pymongo


class MongoHelper:
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def connect(**kwargs):
        conn_config = {
            "host": kwargs.get('host', os.getenv('MONGO_HOST', '127.0.0.1')),
            "port": kwargs.get('port', os.getenv('MONGO_PORT', 27017)),
            "user": kwargs.get('user', os.getenv('MONGO_USER', None)),
            "password": kwargs.get('password', os.getenv('MONGO_PASSWORD', None)),
            "db": kwargs.get('db', os.getenv('MONGO_DB', ''))
        }
        if conn_config.get('user'):
            conn_config['creds'] = '{}:{}@'.format(conn_config['user'], conn_config['password'])
        else:
            conn_config['creds'] = ''

        uri = 'mongodb://{creds}{host}:{port}/{db}'.format(**conn_config)
        client = pymongo.MongoClient(uri)

        return client


if __name__ == '__main__':
    t = MongoHelper()
    t.connect()