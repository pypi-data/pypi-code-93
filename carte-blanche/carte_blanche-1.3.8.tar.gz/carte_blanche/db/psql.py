'''
======================================================================
Database connection initialization and handling. Initializes connection,
session and global base model class.
----------------------------------------------------------------------
'''
import os
import psycopg2
from decimal import Decimal
import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime
from sqlalchemy.orm import sessionmaker

DB_HOST = os.environ.get('POSTGRES_DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('POSTGRES_DB_PORT', '5432')
DB_USERNAME = os.environ.get('POSTGRES_DB_USERNAME', 'postgres')
DB_PASSWORD = os.environ.get('POSTGRES_DB_PASSWORD', 'password')
DB_DATABASE = os.environ.get('POSTGRES_DB_DATABASE', 'postgres')


class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


def orm_connection(connection_args):
    '''
    connection_args = {
        'database':  '',
        'username': '',
        'password': '',
        'host': '',
        'port': ''
    }
    '''
    dbname = connection_args.get('database', DB_DATABASE)
    user = connection_args.get('username', DB_USERNAME)
    password = connection_args.get('password', DB_PASSWORD)
    host = connection_args.get('host', DB_HOST)
    port = connection_args.get('port', DB_PORT)
    DB_STRING = f'postgres://{user}:{password}@{host}:{port}/{dbname}'

    db_instance = create_engine(DB_STRING, connect_args={'connect_timeout': 10})
    db_connection = db_instance.connect()
    Session = sessionmaker(db_connection)

    base = declarative_base()

    return {'base': base, 'session': Session, 'db_connection': db_connection}


def raw_connection(connection_args={}):
    '''
        connection_args = {
        'database':  '',
        'username': '',
        'password': '',
        'host': '',
        'port': ''}
    '''
    dbname = connection_args.get('database', DB_DATABASE)
    user = connection_args.get('username', DB_USERNAME)
    password = connection_args.get('password', DB_PASSWORD)
    host = connection_args.get('host', DB_HOST)
    port = connection_args.get('port', DB_PORT)

    connection = None
    try:
        connection = psycopg2.connect(dbname=dbname, user=user,
                                      password=password, host=host,
                                      port=port, connect_timeout=3)

    except Exception as ex:
        print(ex)
        exit()

    return connection


def get_raw_connection_fields(cursor_description):
    fields = [i[0] for i in cursor_description]

    return fields


def execute_raw_write_query(cursor, query, args=None):
    if args is None:
        cursor.execute(query)
    else:
        cursor.execute(query, args)


def execute_raw_select_query(cursor, query_string, mode='all'):
    cursor.execute(query_string)
    fields = get_raw_connection_fields(cursor.description)
    results = []

    if mode == 'all':
        data = cursor.fetchall()

    elif mode == 'batch':
        data = []

        should_query = True

        while should_query:

            batch = cursor.fetchmany(100)

            if len(batch) == 0:
                should_query = False

            else:
                for row in batch:
                    data.append(row)
    for record in data:
        result = {}

        for idx, value in enumerate(record):
            key = fields[idx]

            if isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, datetime.timedelta):
                value = value.total_seconds()

            result[key] = value

        results.append(result)

    return results
