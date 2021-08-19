'''
========================================================
Mongo DB Utilities
--------------------------------------------------------
'''
import os
from pymongo import MongoClient

DB_HOST = os.environ.get('MONGO_DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('MONGO_DB_PORT', '27017')


def raw_connection(connection_args={}):
    '''
        connection_args = {
        'database':  '',
        'username': '',
        'password': '',
        'host': '',
        'port': ''}
    '''
    user = connection_args.get('username', None)
    password = connection_args.get('password', None)
    host = connection_args.get('host', DB_HOST)
    port = connection_args.get('port', DB_PORT)

    if user is not None and password is not None:
        connection_string = f'mongodb://{user}:{password}@{host}:{port}/'
    else:
        connection_string = f'mongodb://{host}:{port}/'

    client = MongoClient(connection_string)

    return client


if __name__ == '__main__':
    client = raw_connection()
