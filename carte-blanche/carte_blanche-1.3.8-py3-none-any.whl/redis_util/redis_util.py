import os
import redis

'''
======================================================================
Connection utilities for redis
----------------------------------------------------------------------
'''

REDIS_DB_HOST = os.environ.get('REDIS_DB_HOST', 'localhost')
REDIS_DB_PORT = os.environ.get('REDIS_DB_PORT', '6379')
REDIS_DB_DATABASE = int(os.environ.get('REDIS_DB_DATABASE', '0'))


def connect(connection_args={}):
    '''
        connection_args = {
            'host': '',
            'port': '',
            'database': ''
        }
    '''
    db_host = connection_args.get('host', REDIS_DB_HOST)
    port = connection_args.get('port', REDIS_DB_PORT)
    database = connection_args.get('database', REDIS_DB_DATABASE)

    redis_db = redis.Redis(host=db_host, port=port, db=database, socket_connect_timeout=3, decode_responses=True)

    return redis_db
