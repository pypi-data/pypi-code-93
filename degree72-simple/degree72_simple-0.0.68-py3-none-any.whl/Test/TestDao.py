from Core.DaoBase import DaoBase
import pandas as pd
import re


class TestDao(DaoBase):
    def __init__(self, **kwargs):
        super(TestDao, self).__init__(**kwargs)
        # self.connect_to_mongo()
        # self.db = self.mongo_client['Test']
        # self.data_collection = self.db['data']
        # self.page_collection = self.db['page']
        # self.category_rows = []
        # self.meta_datas.append({
        #     'rows': self.category_rows
        # })

    def save(self, source_block):
        super(TestDao, self).save(source_block)
        # self.save_to_mongo(source_block)

    def save_category(self, source_block):
        self.category_rows.append(source_block)

    def save_to_mongo(self, data_block):
        self.data_collection.insert_one(data_block)






if __name__ == '__main__':
    t = TestDao()
    t.csv_to_mysql('/Users/will/project/python/72s/GoogleMapPopularity/Data/google_map_current_popularity_times_2020-03-15.csv', if_exists='replace')
    # t.csv_to_mysql('/Users/will/project/python/72s/GoogleMapPopularity/Data/google_map_popularity_times_2020-03-14.csv', if_exists='replace')
