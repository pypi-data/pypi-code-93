from typing import List

from motor.motor_asyncio import AsyncIOMotorClient


class BaseMotor(object):

    def __init__(self):
        pass

    def AsyncIOMotorClient(self, uri, dbname):
        """
        异步链接mongo客户端
        :param uri:
        :param dbname:
        :return:
        """
        self.connection = AsyncIOMotorClient(uri)
        self.db = self.connection[dbname]

    def get_col(self, colname):
        """
        获取表
        :param colname:
        :return:
        """
        self.col = self.db[colname]

    async def select_yield(self, query={}):
        """
        异步查询
        :param query:
        :return:
        """
        async for doc in self.col.find(query):
            yield doc

    async def select(self, query={}):
        """
        异步查询
        :param query:
        :return:
        """
        docs = self.col.find(query)
        lists = await docs.to_list(None)
        return lists

    async def select_one(self, query={}):
        """
        异步查询一条
        :param query:
        :return:
        """
        doc = await self.col.find_one(query)
        # print(doc)
        return doc

    async def insert_many(self, lists: List[dict], ordered=False, *args, **kwargs):

        """
        插入一个列表（列表内为dict类型）
        :param lists:
        :param ordered: 如果某一条出现错误 设置为False会继续处理其他数据，默认为true
        :param args:
        :param kwargs:
        :return:
        """
        result = await self.col.insert_many(lists, ordered=ordered, *args, **kwargs)
        print('inserted %d docs' % (len(result.inserted_ids),))
        return result

    async def insert_one(self, dicts):
        """
        异步插入一条
        :param dicts:
        :return:
        """
        result = await self.col.insert_one(dicts)
        # print('result %s' % repr(result.inserted_id))

    async def replace_one(self, dicts, iddicts=None):
        if iddicts is None:
            iddicts = {"_id": dicts["_id"]}
        result = await self.col.replace_one(iddicts, dicts)
        print('result %s' % repr(result.modified_count))

    async def find(self, doc_hook, query=None, feild=None):
        """
        异步查询
        for document in await cursor.to_list(length=100):
        """
        async for doc in self.col.find(query, feild):  # 查询所有文档
            await doc_hook(doc)

    async def update(self, query, sets):
        result = await self.col.update_one(query, {'$set': sets})
        # print('updated %s document' % result.modified_count)

    async def run_common(self, doc_hook, commons):
        result = await self.db.command(commons)
        doc_hook(result)

    async def delete_many(self, query):
        """

        :param query: 一个字典 按照条件删除
        :return:
        """
        result = await self.col.delete_many(query)

    async def delet_one(self, query):
        """
        删除一条数据
        :param query_id:
        :return:
        """
        result = await self.col.delete_one(query)

#
# bs = BaseMotor()
# bs.AsyncIOMotorClient(
#     "mongodb://cjrw:vipdatacenter@192.168.31.243:32920,192.168.31.208:32920,192.168.31.206:32920/testdb.jss_pantent_detail?authSource=testdb",
#     "testdb")
# bs.get_col("jss_pantent_detail")
#
# print(bs.select_one({"_id":"Patent_AU19920025315"}))
#
# i = 0
# lists = []
# start_time = time.time()
# for file in BaseDir.get_dir_all_files(r"F:\fun2\gz"):
#     print(file)
#     for line in BaseGzip(100).read_gz_file(file):
#         i = i + 1
#         line = line.strip()
#         dicts = json.loads(line)
#         dicts["export_stat"] = 0
#         dicts["_id"] = dicts["rawid"]
#         del dicts["rawid"]
#         lists.append(dicts)
#         if i % 100000 == 1:
#             print(i)
#             try:
#                 asyncio.get_event_loop().run_until_complete(bs.insert_many(lists))
#             except BulkWriteError as e:
#                 print(e.args)
#                 # print(e.details)
#             lists.clear()
#             print(time.time()-start_time)
#
# try:
#     asyncio.get_event_loop().run_until_complete(bs.insert_many(lists))
# except BulkWriteError as e:
#     print(e.args)
#     # print(e.details)
# lists.clear()
# print(time.time() - start_time)
# print(i)
# asyncio.get_event_loop().run_until_complete(bs.select_one({"_id": "Patent_AU19920025315"}))
