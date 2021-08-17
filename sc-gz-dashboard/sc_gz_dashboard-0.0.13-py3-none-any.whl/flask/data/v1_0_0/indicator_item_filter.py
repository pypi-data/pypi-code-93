#  The MIT License (MIT)
#
#  Copyright (c) 2021. Scott Lau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import logging

import pandas as pd
from flask_restful import Resource

from sc_gz_dashboard.db.common_db_module import CommonDBModule
from sc_gz_dashboard.db.common_sql import *


class IndicatorItemFilter(Resource):
    """
    获取指标项目过滤条件选项清单
    """

    def __init__(self):
        self._db_module = CommonDBModule()

    def get(self):
        """
        获取指标项目过滤条件选项清单
        :return: 指标项目过滤条件选项清单
        """
        filter_params, page_limit_params = "1=1", ""
        sql = SELECT_ALL_INDICATOR_ITEMS_FOR_FILTER % (filter_params, page_limit_params)
        logging.getLogger(__name__).info('执行SQL查询：{}'.format(sql))
        cursor, conn = self._db_module.get_conn()
        df = pd.read_sql(sql, con=conn)
        indicator_items = list()

        all_category_dict = dict()
        # 先将各指标项目拼接成三层的级联字典
        for row_i, row in df.iterrows():
            indicator_category = row['indicator_category']
            if indicator_category not in all_category_dict.keys():
                category_dict = dict()
                category_dict['value'] = indicator_category
                category_dict['label'] = indicator_category
                children = dict()
                category_dict['children'] = children
                all_category_dict[indicator_category] = category_dict
            category_children_dict = all_category_dict[indicator_category]["children"]
            indicator_type = row['indicator_type']
            if indicator_type not in category_children_dict.keys():
                type_dict = dict()
                type_dict['value'] = indicator_type
                type_dict['label'] = indicator_type
                children = dict()
                type_dict['children'] = children
                category_children_dict[indicator_type] = type_dict
            type_children_dict = category_children_dict[indicator_type]["children"]
            indicator_name = row['indicator_name']
            indicator_id = row['id']
            if indicator_id not in type_children_dict.keys():
                id_dict = dict()
                id_dict['value'] = indicator_id
                id_dict['label'] = indicator_name
                type_children_dict[indicator_id] = id_dict

        for category_dict in all_category_dict.values():
            category_children_list = list()
            for type_dict in category_dict['children'].values():
                type_children_list = list()
                for id_dict in type_dict['children'].values():
                    type_children_list.append(id_dict)
                type_dict['children'] = type_children_list
                category_children_list.append(type_dict)
            category_dict['children'] = category_children_list
            indicator_items.append(category_dict)

        result = {
            "indicator_items": indicator_items,
        }
        result_info = {'status': '00000', 'reason': u'成功', 'data': result}
        return result_info
