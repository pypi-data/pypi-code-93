import re
import json
import collections
import time
import pymongo
import redis



# 应对业务需求，快速匹配出他们想要的消化数据
def merge_mongo(
    left_table_name="ziru_stock", right_table_name="ziru_name_list", left_join_field="所属业务组",
    right_join_field="ziru_zone", conditions_dict={}, project_dict={"_id":0}, db=None,
    ):
    """
    notes:
        1. project_dict的功能是表示哪些字段需要显示，哪些不要显示。但是只有“_id”可以为0，其他只能标记为1.
        2. 右连接的字段前必须加上matched_field才行
        3. 返回得到的 all_join_docs 中， 右连接得到的所有内容都包含在 matched_field 字段中，以dict形式存在
    """

    if db is None:
        client = pymongo.MongoClient("127.0.0.1")
        db = client["zufang_001"]

    # 输入接口：
    # left_table_name
    # right_table_name

    # 管道筛选：
    pipeline = [
                {
                    "$lookup":
                    {
                        "from":right_table_name,
                        "localField":left_join_field,
                        "foreignField":right_join_field,
                        "as":"matched_field",
                    }
                },
                {
                    "$match": conditions_dict,
                },
                {
                    "$project": project_dict,
                }
                ]

    all_join_docs = db[left_table_name].aggregate(pipeline)
    return all_join_docs




def main():
    pass



if __name__ == '__main__':
    print("start test!")
    main()
    print("\n\n\neverything is ok!")
