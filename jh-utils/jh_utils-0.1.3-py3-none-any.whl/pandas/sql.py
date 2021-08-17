## importing libs
import pandas as pd
import json
from sqlalchemy import create_engine
import psycopg2

def get_data(query, engine, close_connection = False):
    """
    make a query in a database
    """
    ## open connection
    engine.connect()
    
    ## make select query
    table = pd.read_sql(query, engine)

    # ## close connection
    if close_connection:
        engine.close()
    return table

def write_table(table, table_name, schema, engine, if_exists = 'append', chunksize = 10_000, index= False, close_connection = False):
    """
    if_exists => ["append","replace"]
    
    """

    ## open connection
    engine.connect()

    ## write or replace table
    table.to_sql(name = table_name,
                 if_exists = if_exists,
                 con = engine,
                 schema=schema,
                 method='multi',
                 chunksize = chunksize,
                 index = index)

    # ## close connection
    if close_connection:
        engine.close()

def get_first_row(table, schema, engine):
    return get_data(f'select * from {schema}.{table} dc limit 1',engine)

def create_table_structure(pandas_df, table_name, engine, schema, index = False, if_exists = 'append'):
    pandas_df.to_sql(name = table_name,
                    con = engine, 
                    schema=schema, index=index, if_exists = if_exists)
    conn = engine.connect()
    conn.execute(f'DELETE FROM {schema}.{table_name}')
    conn.close()