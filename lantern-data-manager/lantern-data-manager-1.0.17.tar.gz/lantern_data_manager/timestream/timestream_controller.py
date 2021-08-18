import json, boto3
from lantern_data_manager.utils.logger import logger
from lantern_data_manager.utils.time import ts_to_iso8601_str

class TimestreamController():
    
    def __init__(self, profile_name=None):
        self.client = self._get_client(profile_name, 'timestream-query')
        self.EQUIVALENT_TYPES = {
            'VARCHAR': str,
            'DOUBLE': float,
            'BOOLEAN': self._format_bool,
            'TIMESTAMP': str
        }
                
    def _format_bool(self, bool_str):
        return eval('{}'.format(bool_str.replace('true', 'True').replace('false', 'False')))
                
    def _get_client(self, profile_name, client_operation_name):
        if profile_name:
            try:
                logger.info('Getting client for profile: {}'.format(profile_name))
                session = boto3.Session(profile_name=profile_name)
                return session.client(client_operation_name)
            except Exception as e:
                logger.error('Could not get connection with the specified profile: {}, error: {}'.format(profile_name, e))
                logger.info('Getting client with default profile.')
                return boto3.client(client_operation_name)
        else:
            logger.info('Getting client with default profile.')
            return boto3.client(client_operation_name)
        
    def _normalize_dates(self, from_date, to_date):
        try:
            from_date = "from_iso8601_timestamp('{}')".format(ts_to_iso8601_str(int(from_date)))
        except Exception as e:
            from_date = 'ago({})'.format(from_date)
            
        if to_date:
            try:
                to_date = "from_iso8601_timestamp('{}')".format(ts_to_iso8601_str(int(to_date)))
            except Exception as e:
                to_date = 'ago({})'.format(to_date)
        return from_date, to_date
        
    def _build_query_str(self, device_ids, database, from_date, to_date, measurement, grouper, variable):
        query_str = 'SELECT'
        group_by = False
        if grouper:
            if grouper['functions'] and grouper['functions'][0]:
                group_by = True
                query_str = '{} device_id,'.format(query_str)
                for fn in grouper['functions']:
                    query_str = '{} {}(measure_value::double) AS {},'.format(query_str, fn['fn'], fn['name'])
                query_str = '{} BIN(time, {}) AS time'.format(query_str, grouper['every'])
        if not group_by:
            query_str = '{} *'.format(query_str)
        query_str = '{} FROM {}.{} WHERE time'.format(query_str, database, measurement)
        from_date, to_date = self._normalize_dates(from_date, to_date)
        if to_date:
            query_str = '{} BETWEEN {} AND {}'.format(query_str, from_date, to_date)
        else:
            query_str = '{} > {}'.format(query_str, from_date)
        if variable:
            query_str = "{} AND measure_name = '{}'".format(query_str, variable)
            
        if device_ids:
            query_str = '{} AND device_id in {}'.format(query_str, str(tuple(device_ids)).replace(',)',')'))
        if group_by:
            query_str = '{} GROUP BY device_id, BIN(time, {})'.format(query_str, grouper['every'])
        query_str = '{} ORDER BY time ASC'.format(query_str)
        return query_str
        
    def _get_rows(self, query_str, rows):
        paginator = self.client.get_paginator('query')
        response_iterator = paginator.paginate(QueryString=query_str, PaginationConfig={'MaxItems': rows, 'PageSize': rows})
        rows = []
        columns = []
        for response in response_iterator:
            if not columns:
                columns = response['ColumnInfo']
            for row in response['Rows']:
                _row = {}
                for idx, value in enumerate(row['Data']):
                    if 'NullValue' not in value:
                        column = columns[idx]
                        key = column['Name'] if 'measure_value' not in column['Name'] else 'value'
                        val = self.EQUIVALENT_TYPES[column['Type']['ScalarType']](value['ScalarValue'])
                        _row[key] = val
                rows.append(_row)
        return rows
        
    def query(self, database, device_ids, from_date, rows, measurement, to_date=None, grouper={}, variable=None):
        query_str = self._build_query_str(device_ids, database, from_date, to_date, measurement, grouper, variable)
        rows = self._get_rows(query_str, rows)
        return rows