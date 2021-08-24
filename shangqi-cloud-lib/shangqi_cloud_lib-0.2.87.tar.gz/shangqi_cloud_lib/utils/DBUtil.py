import datetime
import logging
from abc import ABC

from shangqi_cloud_lib.context import config


def echo_sql(func):
    def wrapper(self, *args, **kwargs):
        if config.echo_sql:
            if len(args) > 1:
                logging.info(f"准备执行SQL：{str(args[0])}；参数：{str(args[1:])}")
            else:
                logging.info(f"准备执行SQL：{str(args[0])}")
        return func(self, *args, **kwargs)

    return wrapper


def transfer_str(val):
    if len(val) > 0:
        transfer_char = '\''
        special_chars = ["'"]
        char_list = [val[0]]
        for i in range(1, len(val)):
            c = val[i]
            if c in special_chars and val[i - 1] != transfer_char:
                char_list.append(transfer_char)
            char_list.append(c)
        return "".join(char_list)
    else:
        return val


def convert_val(val):
    if isinstance(val, str):
        if val.startswith("ST_") or val.startswith("st_") or val.lower() == "null":
            return val
        val = transfer_str(val)
        return "'{}'".format(val)
    return str(val)


def parse_values(item, columns):
    values = []
    for column in columns:
        val = convert_val(item.get(column))
        values.append(val)
    return values


def parse_res_val(res):
    if isinstance(res, datetime.datetime):
        val = str(res)
    elif isinstance(res, bytearray) or isinstance(res, bytes):
        val = res.decode('utf-8')
    else:
        val = res
    return val


class BaseSession(ABC):
    def __init__(self, protocol, auto_commit=True):
        self.auto_commit = auto_commit
        self.conn = ""
        self.cursor = ""
        self.protocol = protocol

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb:
            logging.error(f'type:{exc_type}')
            logging.error(f'value:{exc_val}')
            logging.error(f'trace:{exc_tb}')
            self.rollback()
            flag = False
        else:
            flag = True
            if not self.auto_commit:
                try:
                    self.commit()
                except Exception as e:
                    logging.error("事务提交失败：{}".format(str(e)))
                    self.rollback()
        if self.conn and self.conn != "":
            self.close()
        return flag

    @echo_sql
    def query(self, sql):
        if self.conn == "":
            return None
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    @echo_sql
    def query_one(self, sql, data_type="dict", params=None):
        data_type = data_type.lower()
        if data_type not in ["dict", "object", "first", "cursor"]:
            raise NameError(f"Unknown data_type: {data_type}")
        if self.conn != "":
            self.cursor.execute(sql, params)
            res = self.cursor.fetchone()
            if not res:
                return None
            result = None
            if data_type == "dict":
                result = {}
                # 为结果集添加字段名信息
                columns = self.cursor.description
                for i in range(len(columns)):
                    result[columns[i][0]] = parse_res_val(res[i])
            elif data_type == "object":
                result = []
                for item in res:
                    result.append(parse_res_val(item))
            elif data_type == "first":
                result = parse_res_val(res[0])
            elif data_type == "cursor":
                result = res
            return result
        else:
            return None

    @echo_sql
    def query_all(self, sql, data_type="dict", params=None):
        data_type = data_type.lower()
        if data_type not in ["dict", "object", "first", "cursor"]:
            raise NameError(f"Unknown data_type: {data_type}")
        sql = sql.strip()
        if self.conn != "":
            data_list = []
            self.cursor.execute(sql, params)
            res = self.cursor.fetchall()
            if not res:
                return data_list
            if data_type == "cursor":
                return res
            # 为结果集添加字段名信息
            columns = self.cursor.description
            for row in res:
                row_data = None
                if data_type == "dict":
                    row_data = {}
                    for i in range(len(columns)):
                        row_data[columns[i][0]] = parse_res_val(row[i])
                elif data_type == "object":
                    row_data = []
                    for i in range(len(columns)):
                        row_data.append(parse_res_val(row[i]))
                elif data_type == "first":
                    row_data = parse_res_val(row[0])
                if row_data:
                    data_list.append(row_data)
            return data_list
        else:
            return []

    def _execute(self, sql, param=None):
        try:
            if self.protocol == "mysql":
                self.cursor.execute(sql, param)
                self.cursor.execute("SELECT @@IDENTITY as id")
            elif self.protocol == "postgis":
                if sql[-1] == ";":
                    sql = sql[0:-1]
                sql += "RETURNING id"
                self.cursor.execute(sql, param)
        except Exception as e:
            logging.error(f"SQL执行报错：{sql}")
            raise e

    @echo_sql
    def execute_update(self, sql, param=None, batch=False):
        """
        :param sql: 待执行sql
        :param param:  参数字典
        :param batch: 批处理标志（默认：False）
        :return: 行数据id
        """
        if self.conn != "":
            res = 1
            if batch:
                self.cursor.executemany(sql, param)
            else:
                self._execute(sql, param)
                res = self.cursor.fetchone()[0]
            if self.auto_commit:
                self.commit()
            return res
        else:
            return None

    @echo_sql
    def ori_execute(self, sql):
        try:
            res = self.cursor.execute(sql)
            if self.auto_commit:
                self.commit()
            return res
        except Exception as e:
            logging.error(f"SQL执行报错：{sql}")
            raise e

    def _parse_value_list(self, params, column_list):
        if isinstance(params, list):
            for item in params:
                self._parse_value_list(item, column_list)
        elif isinstance(params, dict):
            columns = list(params.keys())
            values = parse_values(params, columns)
            column_list.append({"columns": columns, "values": values})

    def insert(self, table, params):
        """
        :param table: 表名
        :param params: 字典类型（单条插入）/列表类型【元素类型为字典】（多条插入）
        :return:
        """
        insert_sql = "insert into {} ({}) values ({})"
        column_list = []
        self._parse_value_list(params, column_list)
        if self.conn != "":
            res = []
            for column_item in column_list:
                values = column_item.get("values")
                columns = column_item.get("columns")
                values_str = ','.join(values)
                columns_str = ','.join(columns)
                sql = insert_sql.format(table, columns_str, values_str)
                if config.echo_sql:
                    logging.info(sql)
                self._execute(sql)
                row_id = self.cursor.fetchone()[0]
                if row_id <= 0:
                    raise Exception("{} 数据插入失败：{}".format(table, values_str))
                res.append(row_id)
            if self.auto_commit:
                self.commit()
            return res
        else:
            return None

    def commit(self):
        if self.conn != "":
            self.conn.commit()

    def close(self):
        if self.conn != "":
            self.cursor.close()
            self.conn.close()

    def rollback(self):
        if self.conn != "":
            self.conn.rollback()
