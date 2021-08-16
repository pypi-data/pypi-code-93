import csv
import datetime
import json
import os
import inspect
import traceback
from typing import Union

from Util.JobHelper import get_data_folder
import MySQLdb
import MySQLdb.cursors
from Util.CSVHelper import export_dict_rows_to_csv


class MysqlHelper:
    conn = None
    cursor = None

    def __init__(self, **kwargs):
        self.mysql_hook = kwargs.get('mysql_hook')
        self.table = kwargs.get('table')
        self.mysql_config = self.get_mysql_config(**kwargs)

    @classmethod
    def get_mysql_config(cls, **kwargs):
        return {
            "charset": kwargs.get('charset', os.getenv('MYSQL_CHARSET', 'utf8mb4')),
            "db": kwargs.get('db', os.getenv('MYSQL_DB', 'test')),
            "host": kwargs.get('host', os.getenv('MYSQL_HOST', '127.0.0.1')),
            "port": kwargs.get('port', os.getenv('MYSQL_PORT', 3306)),
            "user": kwargs.get('user', os.getenv('MYSQL_USER', 'root')),
            "password": kwargs.get('password', os.getenv('MYSQL_PASSWORD', 'admin123')),
            "autocommit": kwargs.get('autocommit', True),
            "cursorclass": kwargs.get('cursor', MySQLdb.cursors.DictCursor)
        }

    def __del__(self):
        if self.conn:
            self.conn.close()

    def connect(self):
        if self.mysql_hook:
            self.conn = self.mysql_hook.get_conn()
        else:
            self.conn = MySQLdb.connect(**self.mysql_config)
        self.conn.autocommit(True)

    def _cursor(self):
        return self.conn.cursor()

    def export(self, project_name='.', **kwargs):
        self.connect()
        self.table = kwargs.get('table')
        sql_rundate = kwargs.get('sql_rundate', "select max(rundate) from {}".format(self.table))
        rundate_db = self.get_rundate(sql_rundate)

        '''
        check rundate part
        '''
        if kwargs.get('schedule_interval') == 'hour':
            rundate_check = rundate_db.strftime('%Y-%m-%d-%H')
        elif kwargs.get('schedule_interval') == 'minute':
            rundate_check = rundate_db.strftime('%Y-%m-%d-%H-%M')
        else:
            rundate_check = rundate_db.strftime('%Y-%m-%d')

        hour_delta = kwargs.get('hour_delta', 0)
        check_time = datetime.datetime.now() + datetime.timedelta(hours=hour_delta)
        if rundate_check not in str(check_time):
            raise ValueError("rundate in db not qualified: db: {} now: {} ".format(rundate_db, check_time))
        else:
            print("rundate qualified: db: {} check_time: {} ".format(rundate_db, check_time))

        '''
        check insert time part
        '''

        sql_last_insert_time = kwargs.get('sql_rundate', "select tid, InsertUpdateTime from {table} order by 1 desc limit 1".format(table=self.table))
        last_insert_time = self.get_last_insert_time(sql_last_insert_time)
        now_time = datetime.datetime.now()
        time_diff = now_time - last_insert_time
        if time_diff.total_seconds() < 5 * 50:
            raise ValueError('insert time does not qualified db: {} now: {} '.format(last_insert_time, now_time))
        else:
            print('insert time qualified db: {} now: {} '.format(last_insert_time, now_time))

        '''
        download file part
        '''

        sql = kwargs.get('sql', '''select * from {table} where rundate = (select max(rundate) from {table} ) '''.format(table=self.table))
        file_type = kwargs.get('file_type', 'csv')
        file_name_template = kwargs.get('file_name_template', '{}_%s'.format(self.table))
        file_name = kwargs.get('file_name', file_name_template % rundate_check)
        stack = inspect.stack()
        file_folder = kwargs.get('file_folder', get_data_folder(stack, project_name))

        if not os.path.exists(file_folder):
            os.makedirs(file_folder)

        file = os.path.join(file_folder, file_name)
        if file_type == 'csv':
            return self.export_to_csv(sql, file + '.csv')
        else:
            raise ValueError('unknown file type', file)

    def export_to_csv(self, sql, file):
        cursor = self._cursor()
        try:
            cursor.execute(sql)
            fields = [_[0] for _ in cursor.description]

            rows = cursor.fetchall()
            export_dict_rows_to_csv(file, rows, fields)
            return file
        finally:
            cursor.close()

    def get_rundate(self, sql_rundate):
        cursor = self._cursor()
        try:
            cursor.execute(sql_rundate)
            result = cursor.fetchone()
            rundate_db = list(result.values())[0]
            return rundate_db
        finally:
            cursor.close()

    def get_last_insert_time(self, sql_insert_time):
        cursor = self._cursor()
        try:
            cursor.execute(sql_insert_time)
            last_insert_time = list(cursor.fetchone().values())[-1]
            return last_insert_time
        finally:
            cursor.close()

    def select(self, sql):
        cursor = self._cursor()
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()

    def execute(self, query, *parameters, **kwparameters):
        cursor = self._cursor()
        try:
            cursor.execute(query, kwparameters or parameters)
            return cursor.lastrowid
        except Exception as e:
            if e.args[0] == 1062:
                pass
            else:
                traceback.print_exc()
                raise e
        finally:
            cursor.close()

    def save(self, item):
        '''item is a dict : key is mysql table field'''
        table_name = self.table if self.table else item.__table__
        fields = list(item.keys())
        values = list(item.values())
        fieldstr = ','.join(fields)
        valstr = ','.join(['%s'] * len(item))
        for i in range(len(values)):
            if isinstance(values[i], str):
                values[i] = values[i].encode('utf8')
        sql = 'INSERT INTO %s (%s) VALUES(%s)' % (table_name, fieldstr, valstr)
        try:
            last_id = self.execute(sql, *values)
            return last_id
        except Exception as e:
            if e.args[0] == 1062:
                # just skip duplicated item
                pass
            else:
                traceback.print_exc()
                print('sql:', sql)
                print('item:')
                for i in range(len(fields)):
                    vs = str(values[i])
                    if len(vs) > 300:
                        print(fields[i], ' : ', len(vs), type(values[i]))
                    else:
                        print(fields[i], ' : ', vs, type(values[i]))
                raise e


class MySqlHook:
    conn_name_attr = None  # type: str

    def __init__(self, *args, **kwargs):
        self.conn_name_attr = args[0]
        pass

    def get_conn(self):
        hook_config = self.get_hook_config()
        mysql_config = MysqlHelper.get_mysql_config(**hook_config)
        conn = MySQLdb.connect(**mysql_config)
        return conn

    def get_hook_config(self):
        hook_config = {}
        config_file_path = os.path.join(os.path.expanduser('~'), '.degree72-simple', 'hook_config.json')
        if os.path.exists(config_file_path):
            with open(config_file_path, 'r') as fh:
                hook_config = json.load(fh)
        return hook_config.get(self.conn_name_attr, {})


if __name__ == '__main__':
    MySqlHook('mysql_conn_qa').get_conn()