import os
import datetime
import inspect

from Core.Log import Log
from Util.MongoHelper import MongoHelper
from Util.MySqlHelper import MysqlHelper
from Util.CSVHelper import *
from Util.JobHelper import *
from Core.EntityBase import EntityBase
from Util.JobHelper import get_data_folder
from copy import copy
import threading


class DaoBase(object):
    def __init__(self, **kwargs):
        self._run_date = kwargs.get("run_date", datetime.datetime.now())
        self.log = kwargs.get('log', Log(self.__class__.__name__))
        self.kwargs = kwargs
        self.rows = []
        self.index = 0
        self.mode = 'w' # append or write to the file
        self.buffer_count = kwargs.get('buffer_count', 100000)
        self.export_file = None
        self.project_name = ''
        self.lock = threading.RLock()

    def connect_to_mongo(self):
        self.mongo_client = MongoHelper().connect(**self.kwargs)

    def connect_to_mysql(self):
        mysql = MysqlHelper(**self.kwargs)
        mysql.connect()
        self.mysql_conn = mysql.conn
        self.mysql_cursor = mysql.cursor

    def save(self, source_block):
        self.lock.acquire()
        self.index += 1
        self.lock.release()
        self.rows.append(copy(source_block))
        if self.index % self.buffer_count == 0:
            self.log.info('buffering', self.index)
            self.export_data()
            self.rows.clear()
            self.mode = 'a'

    def parse_data(self, source_block):
        pass

    def parse(self, **kwargs):
        pass

    def df_to_mysql(self, df, table, if_exists):
        mysql_config = {
            "charset": os.getenv('MYSQL_CHARSET', 'utf8mb4'),
            "db": os.getenv('MYSQL_DB', 'test'),
            "host": os.getenv('MYSQL_HOST', '127.0.0.1'),
            "port": os.getenv('MYSQL_PORT', 3306),
            "user": os.getenv('MYSQL_USER', 'dev'),
            "password": os.getenv('MYSQL_PASSWORD', 'Devadmin001')
        }
        from sqlalchemy import create_engine
        engine = create_engine('mysql://{user}:{password}@{host}:{port}/{db}?charset={charset}'.format(**mysql_config))
        with engine.connect() as conn, conn.begin():
            df.to_sql(table, conn, if_exists=if_exists, index=False)

    def csv_to_mysql(self, file, table=None, if_exists='append'):
        import pandas as pd
        if table is None:
            import re
            table = re.search('(\D+)', file.split('/')[-1]).group(1).strip('_')
        df = pd.read_csv(file)
        self.df_to_mysql(df, table, if_exists)
        self.log.info('load csv file to mysql successfuly')

    def export_data(self, **kwargs):
        file = kwargs.get('file', self.export_file)

        if not os.path.dirname(file):  # which means it is only a file name like 'test.parquet'
            stack = inspect.stack()
            file_folder = get_data_folder(stack, self.project_name)
            file = os.path.join(file_folder, file)

        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))

        rows = kwargs.get('rows', self.rows)
        if not rows:
            if self.mode == 'w':  # it means that the rows was never exported
                return None
            else:  # we need to return the file if the rows has been exported before
                return file
        mode = kwargs.get('mode', self.mode)
        fields = kwargs.get('fields')
        if not fields:
            if isinstance(rows[0], EntityBase):
                fields = rows[0].fields()
            else:
                fields = rows[0].keys()

        file_type = str(file).split('.')[-1]
        params = {
            'file': file,
            'rows': rows,
            'fields': fields,
            'mode': mode,
        }
        if file_type == 'csv':
            export_dict_rows_to_csv(file, rows, fields, mode)
        elif file_type == 'parquet':
            self.export_data_to_parquet(**params)
        else:
            raise ValueError('unknown file type', str(self.export_file))
        return file

    def export_data_to_parquet(self, file, rows, fields, mode):
        import pandas as pd
        import pyarrow as pa
        import pyarrow.parquet as pq
        if mode =='a':
            raise ValueError('parquet file mode is appending, please update export_data_to_parquet method')
        df = pd.DataFrame(rows)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, file)
        return file

    def select(self, sql):
        if not self.mysql_cursor:
            self.connect_to_mysql()
        self.mysql_cursor.execute(sql)
        result = self.mysql_cursor.fetchall()
        self.mysql_conn.close()
        return result
