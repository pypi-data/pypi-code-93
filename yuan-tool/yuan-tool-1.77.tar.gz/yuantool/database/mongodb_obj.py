# coding: utf-8
from pymongo import MongoClient

"""
use admin
db.createUser( 
  { 
    user: "XXX", 
    pwd: "XXXXXXX", 
    roles: [ { role: "root", db: "admin" } ] 
  } )
再开启验证(mongod.conf)


删除用户：
use XXXX
db.dropUser('XXXXX')
"""


class BaseMongoDB(object):
    """
    数据库基类
    """

    def __init__(self, name, host, port, db, **kwargs):
        self.name = name
        # self.client = MongoClient(host, port, **kwargs)
        # self.client.admin.authenticate(config.database.username, config.database.password)
        if 'password' in kwargs and 'user' in kwargs and 'source' in kwargs:
            mongo_url = 'mongodb://{0}:{1}@{2}:{3}/?authSource={4}&authMechanism=SCRAM-SHA-1'.format(
                kwargs['user'], kwargs['password'], host, port, kwargs['source'])
        else:
            mongo_url = 'mongodb://{0}:{1}'.format(host, port)
        # mongo_url = parse.quote(mongo_url)
        self.client = MongoClient(mongo_url)
        self.db = self.client[db]
        self.task = self.db[self.name]

    def change_table(self, name):
        self.name = name
        self.task = self.db[self.name]

    def get_one(self, key: dict):
        return self.task.find_one(key)

    def find(self, key: dict):
        return self.task.find(key)

    def get_all(self):
        return [data for data in self.task.get()]

    def delete_many(self, key: dict):
        return self.task.delete_many(key).deleted_count

    def delete_one(self, key: dict):
        return self.task.delete_one(key).raw_result

    def put(self, obj: dict):
        return self.task.insert_one(obj)

    def update_many(self, key: dict, obj: dict):
        return self.task.update_many(key, {"$set": obj}, upsert=True).raw_result

    def update_one(self, key: dict, obj: dict):
        return self.task.update_one(key, {"$set": obj}, upsert=True).raw_result

    def push_one(self, key: dict, where: str, obj: dict):
        """
        向array插入一条数据
        e.g. mongodb_cursor.push_one({'id': 0}, 'standby', {'task_id': 'mongopushtest', 'number': 'heyhey'})
        """
        return self.task.update_one(key, {"$push": {where: obj}}, upsert=True).raw_result

    def pull_one(self, key: dict, obj: dict):
        """
        从array删除一条数据
        e.g. mongodb_cursor.pull_one({'id': 0}, {'standby': {'task_id': 'mongopushtest'}})
        """
        return self.task.update_one(key, {"$pull": obj}, upsert=True).raw_result

    def pop_one(self, key: dict, where: str):
        """
        从array弹出最早的一条数据
        注意目前where只支持一级目录，不支持比较复杂位置的array（后期再优化吧
        """
        res = self.task.find_one_and_update(key, {"$pop": {where: -1}}, upsert=True)
        return res[where][0] if res[where] else []

    def increment_one(self, key: dict, obj_key: str, step: int):
        """
        对表里的某个数进行自增、自减操作
        [注意]对于嵌套型的数据，需要使用如下格式
        obj_key: "scan_type.s"
        :param key: 索引的key
        :param obj_key:目标的key
        :param step: 增减幅度
        :return:
        """
        return self.task.update_one(key, {"$inc": {obj_key: step}})


"""
由于mongodb中key值不能存在'.'，故对于字典的key值全部进行转换
于是有下面的两个方法
"""


def save_change(d, m='|'):
    """
    清洗变量d，将其中所有字典key的'.'变为'|'（或自定义m）
    """
    if not isinstance(d, dict):
        pass
    else:
        _point_to_m(d, m)
        for key in list(d):
            save_change(d[key])
    return d


def load_change(d, m='|'):
    """
    清洗变量d，将其中所有字典key的'|'（或自定义m）变为'.'
    """
    if not isinstance(d, dict):
        pass
    else:
        _m_to_point(d, m)
        for key in list(d):
            load_change(d[key])
    return d


def _point_to_m(t: dict, m='|'):
    for key in list(t):
        if '.' in key:
            nk = str(key).replace('.', m)
            t[nk] = t.pop(key)
    return t


def _m_to_point(t: dict, m='|'):
    for key in list(t):
        if '.' in key:
            nk = str(key).replace(m, '.')
            t[nk] = t.pop(key)
    return t
