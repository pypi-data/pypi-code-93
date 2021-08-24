import logging
import traceback

from gridfs import GridFS
from pymongo import MongoClient

from shangqi_cloud_lib.context import config
from shangqi_cloud_lib.utils.CommonUtil import is_empty
from shangqi_cloud_lib.utils.DBUtil import BaseSession


def mongodb_connect(db, host, port, user, pwd):
    try:
        if not db:
            db = config.mongo_database
        if not host:
            host = config.mongo_ip
        if not user:
            user = config.mongo_user
        if not port:
            port = config.mongo_port
        if not pwd:
            pwd = config.mongo_password
        client = MongoClient(host, int(port))
        db_obj = client.admin  # 先连接系统默认数据库admin
        db_obj.authenticate(user, pwd, mechanism='SCRAM-SHA-1')
        db_obj = client[db]
        return db_obj, client
    except Exception as e:
        logging.warning("连接数据库异常:" + traceback.format_exc())
        return "", str(e)


def convert_to_mongo(value):
    if isinstance(value, str) and not is_empty(value):
        if (value[0] == "'" and value[-1] == "'") or (value[0] == '"' and value[-1] == '"'):
            return value
        else:
            return "'" + value + "'"
    elif isinstance(value, list):
        result = "[{}]"
        temp_list = []
        for item in value:
            temp_list.append(convert_to_mongo(item))
        return result.format(",".join(temp_list))
    return str(value)


def prepare_for_mongo(params: dict):
    result = {}
    for key, value in params.items():
        result[key] = convert_to_mongo(value)
    return result


def query_params_for_mongo(db, query: str, params=None):
    query = query.strip()
    if params and isinstance(params, dict):
        prepared = prepare_for_mongo(params)
        for key, value in prepared.items():
            query = query.replace("%({0})s".format(key), value)
    if "findOne" in query:
        query = query.replace("findOne", "find_one")
    if config.echo_sql:
        logging.info(query)
    res = eval(query)
    return res


class Table:
    condition_key = "condition"
    columns_key = "columns"

    def __init__(self, db, table):
        self.db = db
        self.table = db[table]
        if not table:
            raise ConnectionError
        self.table_name = table
        self.steps = []

    def __iter__(self):
        return self.all()

    def origin(self):
        return self.table

    def insert(self, values):
        self.table.insert(values)

    def update(self, condition, values, **options):
        self.table.update(condition, {"$set": values}, **options)

    def delete(self, condition):
        self.table.remove(condition)

    def _put(self, key, val):
        self.steps.append((key, val))

    def _condition_columns(self):
        condition = {}
        columns = {}
        for step in self.steps:
            key, val = step
            if key == self.condition_key:
                condition.update(val)
            elif key == self.columns_key:
                if isinstance(val, dict):
                    columns.update(val)
                elif isinstance(val, list):
                    for column in val:
                        columns[column] = 1
        return condition, columns if columns else None

    def query(self, condition=None, columns=None):
        self.steps.clear()
        self._put(self.condition_key, condition)
        self._put(self.columns_key, columns)
        return self

    def first(self, **options):
        return self.table.find_one(*self._condition_columns(), **options)

    def one(self, **options):
        return self.first(**options)

    def all(self, **options):
        condition, columns = self._condition_columns()
        return self.table.find(condition, columns, **options)

    def aggregate(self, params: list, **options):
        return self.table.aggregate(params, **options)

    def distinct(self, key):
        return self.all().distinct(key)

    def count(self):
        return self.all().count()

    def limit(self, num):
        return self.all().limit(num)

    def upload(self, filename, data):
        fs = GridFS(self.db, collection=self.table)
        return fs.put(data, filename=filename)

    def download(self, condition):
        fs = GridFS(self.db, collection=self.table)
        return fs.find_one(filter=condition)


class MgSession(BaseSession):
    def __init__(self, db=None, host=None, user=None, port=None, pwd=None):
        super().__init__("mongo")
        self.db, _ = mongodb_connect(db, host, port, user, pwd)
        if self.db == "":
            raise Exception(_)
        else:
            self.client = _

    def get_db_list(self):
        return self.client.list_database_names()

    def get_table_list(self):
        return self.db.list_collection_names()

    def execute(self, sql, params=None):
        return query_params_for_mongo(self.db, sql, params)

    def collection(self, table):
        return Table(self.db, table)
