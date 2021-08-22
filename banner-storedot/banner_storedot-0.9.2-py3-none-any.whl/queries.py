import re
from typing import Union, Dict

import MySQLdb as mysql
from MySQLdb.cursors import DictCursor
import pandas as pd
import numpy as np

from banner.utils.const import FIRST_NEWARE_DATA_TABLE, SECOND_NEWARE_DATA_TABLE, FIRST_NEWARE_AUX_TABLE, SECOND_NEWARE_AUX_TABLE, NW_TEMP
from banner.utils.neware import calc_neware_cols
from banner.connection import Connection, __get_known_connection, connections

def simple_query(query: str, connection=None, as_df=True) -> pd.DataFrame:
    '''
        Queries a given Connection/str of a known connection (or first known) return result as DataFrame
        Raises KeyError and OperationalError
    '''
    connection = __get_known_connection(connection)
   
    with connection as con:
        cursor = con.cursor()

        cursor.execute(query)

        records = cursor.fetchall()
        cursor.close()
    
    if as_df:
        records = pd.DataFrame(records)

    return records

def neware_query(device: int, unit: int, channel: int, test: int, connection: Union[Connection, str] = None, raw=False):
    '''
        Queries a given Connection(ip)/str of a known connection (or first known) return result as DataFrame
        Raises KeyError and OperationalError
    '''
    connection = __get_known_connection(connection)
    
    # Look for the tables
    try:
        neware_data = simple_query(
            f"""
                SELECT *
                FROM h_test 
                WHERE dev_uid = {device} 
                    AND unit_id = {unit} 
                    AND chl_id = {channel}
                    AND test_id = {test}
            """,
            connection=connection
        ).iloc[0] # A single row is returned since we looked by primary key

    except IndexError:
        raise TypeError(f'{connection.name} has No data for device:{device}, unit:{unit}, channel:{channel}') 
    
    # Main tables into a single df
    data = pd.concat([
        simple_query(f'SELECT * FROM {neware_data[FIRST_NEWARE_DATA_TABLE]} WHERE unit_id = {unit} AND chl_id = {channel} AND test_id = {test}', connection) if neware_data[FIRST_NEWARE_DATA_TABLE] else pd.DataFrame(),
        simple_query(f'SELECT * FROM {neware_data[SECOND_NEWARE_DATA_TABLE]} WHERE unit_id = {unit} AND chl_id = {channel} AND test_id = {test}', connection) if neware_data[SECOND_NEWARE_DATA_TABLE] else pd.DataFrame()
    ], ignore_index=True)

    # Aux tables into a single df
    aux_data = pd.concat([
        simple_query(f'SELECT * FROM {neware_data[FIRST_NEWARE_AUX_TABLE]} WHERE unit_id = {unit} AND chl_id = {channel} AND test_id = {test}', connection) if neware_data[FIRST_NEWARE_AUX_TABLE] else pd.DataFrame(),
        simple_query(f'SELECT * FROM {neware_data[SECOND_NEWARE_AUX_TABLE]} WHERE unit_id = {unit} AND chl_id = {channel} AND test_id = {test}', connection) if neware_data[SECOND_NEWARE_AUX_TABLE] else pd.DataFrame()
    ], ignore_index=True)
    
    # We have temp data?
    if not aux_data.empty:
        # Unique aux columns
        aux_columns = set(np.setdiff1d(aux_data.columns, data.columns))
        # aux_data holds the correct test_tmp
        aux_columns.add(NW_TEMP)

        # data columns
        data_columns = list(data.columns)
        # aux_data holds the correct test_tmp
        data_columns.remove(NW_TEMP)

        # Add aux_columns to data
        data = pd.concat(
            [
                data[[*data_columns]],
                aux_data[[*aux_columns]]
            ], 
            axis = 1
        )
    
    if not raw:
        data = calc_neware_cols(data)

    return data

def neware_query_by_test(table: str, cell: int, test: int, connection: Union[Connection, str] = None, raw=False):
    '''
        Queries a given Connection(ip)/str of a known connection (or first known) return result as DataFrame
        Queries the given connection for (device: int, unit: int, channel: int, test: int, connection: str) to feed neware_query
        Raises OperationalError and KeyError(Failed to find a connection for given key) 
    '''
    connection = __get_known_connection(connection)
    
    # Look for the tables
    try:
        neware_keys = simple_query(
            f"""
                SELECT device, unit, channel, test_id, ip
                FROM {table}_test 
                WHERE {table}_id = {cell} 
                    AND test_id = {test} 
            """,
            connection=connection
        ).iloc[0] # A single row is returned since we looked by primary key
    
    except IndexError:
        raise TypeError(f'{connection.name} has No data for table:{table}, cell:{cell}, test:{test}') 
    
    return neware_query(*neware_keys, raw=raw)

def describe_table(table, connection: Union[Connection, str] = None):
    '''
        Describes a table in connection
        Raises OperationalError and KeyError(Failed to find a connection for given key) 
    '''
    connection = __get_known_connection(connection)

    return simple_query(f'DESCRIBE {table}', connection)

def describe(connection: Union[Connection, str] = None):
    '''
        Describe Table names in connection
        Raises OperationalError and KeyError(Failed to find a connection for given key) 
    '''
    connection = __get_known_connection(connection)
    
    return simple_query(
        f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{connection.db}'",
        connection
    )
