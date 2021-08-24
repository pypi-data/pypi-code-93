"""Module containing database-related utility functions."""

import os

import psycopg2
import aws.paramstore


def get_db_connection() -> psycopg2.extensions.cursor:
    """Assigns a DB connection and cursor object to internal variables."""
    try:
        # Create a local instance of OHLCV-related parameters
        env = os.environ.get('AWS_ENVIRONMENT', 'dev')
        paramstore = aws.paramstore.ParameterStore(f'/{env}/trading/etl/db/')

        # Create a DB connection to fetch exchange and market IDs
        db_connection = psycopg2.connect(
            database=paramstore['name'],
            user=paramstore['username'],
            password=paramstore['password'],
            host=paramstore['host'],
            port=paramstore['port'],
        )
        db_cursor = db_connection.cursor()

        return db_cursor

    except Exception as err:
        raise psycopg2.errors.ConnectionFailure(
            'Unable to connect to DB') from err
