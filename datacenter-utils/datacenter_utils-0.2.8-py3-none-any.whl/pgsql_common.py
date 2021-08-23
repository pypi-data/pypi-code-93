# -*-coding:utf-8 -*-

import psycopg2
from psycopg2 import OperationalError
from datetime import datetime, date
import pandas as pd
import re
import numpy as np
import yaml
import os
import json
from datacenter_utils.logger import logger


def read_yaml(file_path, key='pg'):
    with open(file_path, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg[key]


class Postgres(object):

    def __init__(self, conf=None, conf_path='/etc/db.yaml'):
        """
        生成数据库连接self.cursor。默认加载conf配置，当conf配置不存在时，再加载环境变量PG_CONF的配置，
        若PG_CONF的配置也不存在，最后加载conf_path（默认/etc/db.yaml）的文件配置
        优先级：conf字典配置 > 环境变量配置 > conf_path文件配置

        :param conf: 对应数据库配置
        :param conf_path: yaml配置文件绝对路径（可放在环境下任意路径），文件格式参考同目录下的db.yaml
        """
        if not conf:
            conf_str = os.environ.get('PG_CONF')
            if conf_str:
                conf = json.loads(conf_str)
                # conf = eval(conf_str)
                # if isinstance(conf, str):
                #     conf = eval(conf)
            if not conf:
                conf = read_yaml(conf_path)
        try:
            self.database_postgres = psycopg2.connect(database=conf['database'],
                                                      user=conf['user'],
                                                      password=conf['password'],
                                                      host=conf['host'],
                                                      port=int(conf['port']))

            self.cursor = self.database_postgres.cursor()
        except OperationalError as e:
            raise e

    def is_table_exist(self, table_str):
        # TODO 表名字符长度限制63
        exec_str = f"select exists(select * from information_schema.tables where table_name='{table_str.lower()[:63]}');"
        self.cursor.execute(exec_str)
        exist = self.cursor.fetchone()[0]
        logger.info(f'{table_str} is_table_exist: {exist}')
        return exist

    def upsert_df(self, df, table_name, constraint_columns,
                  date_columns=None, timestamp_columns=None
                  ):
        """
        dataframe按照规定的字段设计upsert到指定数据库。
        针对constraint_columns列表，df任一记录任一字段与数据库不一样，就会插入一条新的数据，否则会更新数据库里原有记录。

        :param df: 待插入到数据库里的dataframe
        :type df: pandas.Dataframe
        :param table_name: 目标表名
        :type table_name: str
        :param constraint_columns: 表结构设计中的primary key
        :type constraint_columns: list of str
        :param date_columns: 定义为date类型的字段
        :type date_columns: list of str
        :param timestamp_columns:  定义为timestamp类型的字段
        :type timestamp_columns: list of str
        """
        data_list = df.values.tolist()
        columns = list(df.columns)
        column_list = [f'"{c}"' for c in columns]
        exclude_columns = column_list.copy()
        constraint_columns = [f'"{i}"' for i in constraint_columns]

        for remove_c in constraint_columns:
            exclude_columns.remove(remove_c)
        for row in data_list:
            if len(column_list) - len(constraint_columns) == 1:
                sql = '''
                           INSERT INTO {t} 
                                VALUES  ({column_str})
                                ON CONFLICT ({constraint_columns})
                                DO UPDATE SET
                                    {exclude_columns}
                                    = {exclude_values} ;
                        '''
            elif len(column_list) - len(constraint_columns) > 1:
                sql = '''
                           INSERT INTO {t} 
                                VALUES  ({column_str})
                                ON CONFLICT ({constraint_columns})
                                DO UPDATE SET
                                    ({exclude_columns})
                                    = ({exclude_values}) ;
                        '''
            else:
                raise Exception('length of constraint_columns error')

            for i in range(len(row)):
                if date_columns and column_list[i] in date_columns:
                    if isinstance(row[i], pd.Timestamp):
                        row[i] = row[i].date()
                    elif isinstance(row[i], str):
                        row[i] = datetime.strptime(row[i], '%Y-%m-%d').date()
                    elif isinstance(row[i], date):
                        pass
                    elif isinstance(row[i], datetime):
                        row[i] = row[i].date()
                    else:
                        row[i] = None

                    if timestamp_columns and column_list[i] in timestamp_columns:
                        if isinstance(row[i], pd.Timestamp):
                            row[i] = row[i].datetime()
                        elif isinstance(row[i], str):
                            row[i] = datetime.strptime(row[i], '%Y-%m-%d %H:%M:%S')
                        elif isinstance(row[i], date):
                            pass
                        elif isinstance(row[i], datetime):
                            pass
                        else:
                            row[i] = None
                if row[i] == '' or (isinstance(row[i], float) and np.isnan(row[i])):
                    row[i] = None

            c_str = ','.join(['%s' for i in range(len(row))])

            exclude_values = [f'EXCLUDED.{i}' for i in exclude_columns]
            sql_format = sql.format(t=table_name,
                                    column_str=c_str,
                                    constraint_columns=','.join(constraint_columns),
                                    exclude_columns=','.join(exclude_columns),
                                    exclude_values=','.join(exclude_values))
            self.cursor.execute(sql_format, row)

        logger.info(f'saved {table_name}')
        self.database_postgres.commit()

    def update_insert_df(self, df, table_name, text_columns, constraint_columns,
                         date_columns=None, timestamp_columns=None
                         ):
        """
        dataframe按照规定的字段设计upsert到指定数据库。
        针对constraint_columns列表，df任一记录任一字段与数据库不一样，就会插入一条新的数据，否则会更新数据库里原有记录。
        当表（table_name）不存在时，该函数操作会自动创建表，按照字段类型参数（text_columns、constraint_columns、date_columns、
        timestamp_columns）创建相应类型，未指定的按照float类型处理

        :param df: 待插入到数据库里的dataframe，其columns需要明确且与text_columns、constraint_columns、date_columns、timestamp_columns保持一致
        :type df: pandas.Dataframe
        :param table_name: 目标表名
        :type table_name: str
        :param text_columns: 定义为text类型的字段
        :type text_columns: list of str
        :param constraint_columns: 设置为CONSTRAINT
        :type constraint_columns: list of str
        :param date_columns: 定义为date类型的字段
        :type date_columns: list of str
        :param timestamp_columns:  定义为timestamp类型的字段
        :type timestamp_columns: list of str
        """
        data_list = df.values.tolist()
        columns = list(df.columns)
        data_list.insert(0, columns)
        if date_columns:
            text_columns.extend(date_columns)
        if timestamp_columns:
            text_columns.extend(timestamp_columns)
        # self.cursor.execute(f'DROP TABLE IF EXISTS "{table_name}";')
        count = 0
        column_list = []
        c_str = ''
        for row in data_list:
            if count == 0:
                # 标题format
                column_list = [self._format_str(r) for r in row]

                if not text_columns:
                    text_columns = column_list
                sql_str = ','.join([f'"{j.replace(" ", "_")}" float' if j not in text_columns
                                    else f'"{j.replace(" ", "_")}" text'
                                    for j in column_list])
                if not date_columns:
                    date_columns = []
                for dd in date_columns:
                    sql_str = sql_str.replace(f'"{dd}" text', f'"{dd}" date')

                if not timestamp_columns:
                    timestamp_columns = []
                for dd in timestamp_columns:
                    sql_str = sql_str.replace(f'"{dd}" text', f'"{dd}" timestamp')

                # sql_s = re.findall(r'[^\*/:?\\|<>!]', sql_s, re.S)
                # sql_s = "".join(sql_s)
                logger.info(sql_str)
                # 自定义数据类型
                if not self.is_table_exist(table_name):
                    add_conflict_sql = '''
                    ALTER TABLE "public"."{t}" ADD CONSTRAINT "{pkey}" PRIMARY KEY ({keys});
                    '''.format(t=table_name, pkey=table_name + '_pkey',
                               keys=','.join([f'"{i}"' for i in constraint_columns])
                               )
                    self.cursor.execute(f'create table {table_name} ({sql_str});')
                    self.cursor.execute(add_conflict_sql)
                    logger.info('create table', sql_str)
            else:
                if len(column_list) - len(constraint_columns) == 1:
                    sql = '''
                               INSERT INTO {t} 
                                    VALUES  ({column_str})
                                    ON CONFLICT ({constraint_columns})
                                    DO UPDATE SET
                                        {exclude_columns}
                                        = {exclude_values} ;
                            '''
                elif len(column_list) - len(constraint_columns) > 1:
                    sql = '''
                               INSERT INTO {t} 
                                    VALUES  ({column_str})
                                    ON CONFLICT ({constraint_columns})
                                    DO UPDATE SET
                                        ({exclude_columns})
                                        = ({exclude_values}) ;
                            '''
                else:
                    sql = ''''''

                for i in range(len(row)):
                    if date_columns and column_list[i] in date_columns:
                        if isinstance(row[i], pd.Timestamp):
                            row[i] = row[i].date()
                        elif isinstance(row[i], str):
                            row[i] = datetime.strptime(row[i], '%Y-%m-%d').date()
                        elif isinstance(row[i], date):
                            pass
                        elif isinstance(row[i], datetime):
                            row[i] = row[i].date()
                        else:
                            row[i] = None

                        if timestamp_columns and column_list[i] in timestamp_columns:
                            if isinstance(row[i], pd.Timestamp):
                                row[i] = row[i].datetime()
                            elif isinstance(row[i], str):
                                row[i] = datetime.strptime(row[i], '%Y-%m-%d %H:%M:%S')
                            elif isinstance(row[i], date):
                                pass
                            elif isinstance(row[i], datetime):
                                pass
                            else:
                                row[i] = None
                    if row[i] == '' or (isinstance(row[i], float) and np.isnan(row[i])):
                        row[i] = None
                    # if filter_dict and column_list[i] in filter_dict.keys():
                    #     if filter_dict[column_list[i]] == 'text_format':
                    #         row_s = str(row[i])
                    #         row_s = re.findall(r'[^\*/:?\\|<>!\-]', row_s, re.S)
                    #         row[i] = "".join(row_s)

                # one_sql_str = ','.join(row)
                if not c_str:
                    c_str = ','.join(['%s' for i in range(len(row))])
                    exclude_list = column_list.copy()
                    for remove_c in constraint_columns:
                        exclude_list.remove(remove_c)
                    exclude_columns = [f'"{i}"' for i in exclude_list]
                    constraint_columns = [f'"{i}"' for i in constraint_columns]
                    exclude_values = [f'EXCLUDED."{i}"' for i in exclude_list]
                    sql_str = sql_str.replace('text', '').replace('date', '').replace('float', '')
                sql_format = sql.format(t=table_name,
                                        column_str=c_str,
                                        constraint_columns=','.join(constraint_columns),
                                        exclude_columns=','.join(exclude_columns),
                                        exclude_values=','.join(exclude_values))

                self.cursor.execute(sql_format, row)
            count += 1

        logger.info(f'saved {table_name}')
        self.database_postgres.commit()

    def find(self, table, filter_dict=None, columns=None):
        """
        查询所有满足条件的结果

        :param table: 表格名称
        :param filter_dict: 筛选字典
        :param columns: 返回字段
        :type table: str
        :type filter_dict: dict
        :type columns: list of str
        :return: 查询结果
        """
        if columns:
            columns_str = ",".join([f'"{i}"' for i in columns])
        else:
            columns_str = '*'
        filter_list = []
        if not filter_dict:
            filter_dict = {}
        for k, v in filter_dict.items():
            if isinstance(v, str):
                v = f"'{v}'"
            elif isinstance(v, (datetime, date)):
                v = f"'{v}'"
            filter_list.append(f'"{k}" = {v}')
        filter_str = 'where' + ' and '.join(filter_list) if filter_list else ''
        sql = f"select {columns_str} from {table} {filter_str}"
        logger.info('sql:', sql)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def find_one(self, table, filter_dict, columns):
        """
        查询满足条件的一个结果

        :param table: 表格名称
        :param filter_dict: 筛选字典
        :param columns: 返回字段
        :type table: str
        :type filter_dict: dict
        :type columns: list of str
        :return: 查询结果
        """
        if columns:
            columns_str = ",".join([f'"{i}"' for i in columns])
        else:
            columns_str = '*'
        filter_list = []
        if not filter_dict:
            filter_dict = {}
        for k, v in filter_dict.items():
            if isinstance(v, str):
                v = f"'{v}'"
            elif isinstance(v, (datetime, date)):
                v = f"'{v}'"
            filter_list.append(f'"{k}" = {v}')
        filter_str = 'where' + ' and '.join(filter_list) if filter_list else ''
        sql = f"select {columns_str} from {table} {filter_str}"
        logger.info('sql:', sql)
        self.cursor.execute(sql)
        res = self.cursor.fetchone()
        return res

    def find_by_sql(self, sql):
        """
        通过sql语句查询，返回所有结果
        :param sql: 查询语句
        :return:
        """
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def close_connect(self):
        """
        关闭数据库连接，查询、更新操作结束需要执行此操作
        """
        self.database_postgres.close()

    @staticmethod
    def _format_str(line):
        # 指定字符替换为 -
        line1 = re.sub(r"[\-\n\s \t]", "_", line)
        # 指定字符去除
        line2 = re.sub(r"[‘’“”，。？?]", "", line1)
        return line2
