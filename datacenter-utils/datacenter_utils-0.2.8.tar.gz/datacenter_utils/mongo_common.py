# -*- encoding:utf-8 -*-
import pandas as pd
from pymongo import MongoClient, ASCENDING, DESCENDING
import time
from datetime import datetime, timedelta
from pymongo.errors import OperationFailure


class MongoObject(object):
    """
    class MongoObject
    """
    def __init__(self, host, port, username, password, auth_db='admin'):
        self.insert_bench = 6000
        self.client = MongoClient(f"mongodb://{host}:{port}")
        db = self.client[auth_db]
        db.authenticate(username, password)

    def upsert_many_df(self, collection, df_data, key_field, update_field):
        """
        dataframe按照规定的字段设计upsert到指定数据库

        :param collection: collection connect object，通过实例化MongoObject的mongo_object[db_name][table_name]得到
        :param df_data: dataframe，需要插入mongodb的df数据
        :param key_field: list，确定唯一性的一组字段，任一字段变化都新增一条数据，否则则更新其他字段
        :param update_field: list，上述需要更新的字段列表
        """
        df_data_js = df_data.to_dict(orient='records')  # json.loads(df_data.T.to_json())
        # 添加需要的索引，即主键
        for index_field in key_field:
            collection.create_index(index_field)
        # 写入操作
        bulk = collection.initialize_unordered_bulk_op()

        for num in range(len(df_data_js)):
            item = df_data_js[num]
            insert_data = self._join_upsert_dict(item, key_field, update_field)

            bulk.find(insert_data['key_data']).upsert().update_one(insert_data['change_data'])

            if num % self.insert_bench == 0:
                bulk.execute()
                bulk = collection.initialize_unordered_bulk_op()
            if num == len(df_data_js) - 1:
                bulk.execute()

    @staticmethod
    def _join_upsert_dict(item, key_field, update_field):
        # key_data_dict: if key data exist remain else insert new
        key_data_dict = {}
        for field in key_field:
            joint_dict = {field: item[field]}
            key_data_dict = {**key_data_dict, **joint_dict}

        # change_data_dict ,data need to be update
        change_data_dict = {}
        for field in update_field:
            joint_dict = {field: item[field]}
            change_data_dict = {**change_data_dict, **joint_dict}
        joint_dict = {"updateTime": datetime.utcfromtimestamp(time.time())}
        change_data_dict = {**change_data_dict, **joint_dict}
        change_data_dict = {'$set': change_data_dict}

        # join key_data and change_data
        insert_data = {"key_data": key_data_dict, "change_data": change_data_dict}
        return insert_data

    @staticmethod
    def remove(collection, filter_dict):
        """
        删除满足条件的数据

        :param collection: collection connect object，通过实例化MongoObject的mongo_object[db_name][table_name]得到
        :param filter_dict: dict，需要删除数据的筛选条件
        """
        try:
            collection.remove(filter_dict)
        except:
            collection.delete_many(filter_dict)

    @staticmethod
    def insert_one(collection, data):
        """
        插入一条数据字典

        :param collection: collection connect object，通过实例化MongoObject的mongo_object[db_name][table_name]得到
        :param data: dict，新增的数据字典
        """
        res = collection.insert_one(data)
        return res.inserted_id

    @staticmethod
    def insert_many(collection, data):
        """
        插入数据列表

        :param collection: collection connect object，通过实例化MongoObject的mongo_object[db_name][table_name]得到
        :param data: list，新增的数据列表
        """
        res = collection.insert_many(data)
        return res.inserted_ids

    @staticmethod
    def update_one(collection, condition, data):
        """
        更新一条记录

        :param collection: collection connect object，通过实例化MongoObject的mongo_object[db_name][table_name]得到
        :param condition: dict，被更新数据满足的条件
        :param data: dict，需要更新到的状态
        """
        res = collection.find_one(condition)
        if not res:
            data.update(condition)
            insert_res = collection.insert_one(data)
            return 0, insert_res
        else:
            update_result = collection.update(condition, {'$set': data})
            return 1, update_result

    @staticmethod
    def find_many_df(collection, filter_dict=None, projection=None, order_by=None,
                     offset=0, limit=20
                     ):
        """
        从指定表获取满足筛选条件的数据，返回dataframe

        :param collection: collection connect object，通过实例化MongoObject的mongo_object[db_name][table_name]得到
        :param filter_dict: dict，筛选字段
        :param projection: dict，规定返回字段和不返回的字段，{<c1>: 1, <c2>: -1}表示字段c1返回、字段c2不返回
        :param order_by: str，规定排序的字段，'-c1'表示对字段c1逆序排列，'-c2'表示对字段c2顺序排列
        :param offset: int，截取offset值以后的记录
        :param limit: int，截取offset值以后的limit条记录
        :return:
        """
        cursor = None
        if filter_dict and not projection:
            projection = dict()
            projection.update({'_id': 0})
            cursor = collection.find(filter_dict).limit(limit).skip(offset)
        if filter_dict and projection:
            projection.update({'_id': 0})
            cursor = collection.find(filter_dict, projection).limit(limit).skip(offset)
        if not filter_dict and not projection:
            cursor = collection.find({}).limit(limit).skip(offset)

        if order_by:
            order = -1 if '-' in order_by else 1
            order_by = order_by.replace('-', '')
            cursor.sort([(order_by, order)])

        if cursor:
            docs = list(cursor)
            return pd.DataFrame(docs)


