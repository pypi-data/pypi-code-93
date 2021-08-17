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
from datetime import datetime
from decimal import Decimal

import pandas as pd
from sc_utilities import Singleton

from sc_gz_dashboard.db.common_db_module import CommonDBModule
from sc_gz_dashboard.db.common_sql import *
from sc_gz_dashboard.utils import MonthUtils


class DashBoardDataView(metaclass=Singleton):
    """
    看板数据展现
    """

    def __init__(self):
        self._db_module = CommonDBModule()
        self._category_dict = {
            "对公": "Corporate",
            "普惠": "Inclusive_Finance",
            "零售": "Retail",
        }
        self._init_column_index()
        self._datetime_format = "%Y-%m-%d %H:%M:%S"
        self._latest_update_time_dict: dict = {}
        self._latest_history_count_dict: dict = {}
        self._empty_records_dict = {
            "Corporate": [],
            "Inclusive_Finance": [],
            "Retail": [],
        }
        self._cached_dashboard_data = dict()

    def _init_column_index(self):
        """
        初始化列索引
        :return:
        """
        index = 0
        self._index_id = index
        index += 1
        self._index_indicator_id = index
        index += 1
        self._index_indicator_name = index
        index += 1
        self._index_indicator_category = index
        index += 1
        self._index_indicator_type = index
        index += 1
        self._index_indicator_unit = index
        index += 1
        self._index_indicator_dept = index
        index += 1
        self._index_indicator_year = index
        index += 1
        self._index_indicator_month = index
        index += 1
        self._index_indicator_value = index
        index += 1
        self._index_report_time = index

    def get_all_dashboard_data(self, year: int):
        """
        获取看板数据
        :param year: 分析年份
        :return: 看板数据
        """
        all_year_dict = self.get_available_years()
        if len(all_year_dict) <= 0 or year not in all_year_dict.keys():
            # 记录不存在
            logging.getLogger(__name__).info('记录不存在')
            self._cached_dashboard_data[year] = dict()
            self._cached_dashboard_data[year].update(self._empty_records_dict)
            return self._cached_dashboard_data.get(year)
        max_update_time = datetime.strptime(all_year_dict.get(year).get("max_update_time"), self._datetime_format)
        record_count = all_year_dict.get(year).get("record_count")
        logging.getLogger(__name__).info('%s年数据记录存在，最新更新时间为%s, 记录数为：%s', year, max_update_time, record_count)
        latest_update_time_in_cache = self._latest_update_time_dict.get(year)
        latest_history_count_in_cache = self._latest_history_count_dict.get(year)
        if (latest_update_time_in_cache is not None and max_update_time <= latest_update_time_in_cache) \
                and latest_history_count_in_cache == record_count:
            logging.getLogger(__name__).info("无需更新数据，从缓存获取数据")
            return self._cached_dashboard_data.get(year)
        self._cache_dashboard_data(year=year)
        self._latest_update_time_dict[year] = max_update_time
        self._latest_history_count_dict[year] = record_count
        return self._cached_dashboard_data.get(year)

    def _cache_indicator_item_dict(self, result_dict: dict) -> None:
        """
        处理指标项目信息
        :param result_dict: 结果字典
        :return:
        """
        # 待返回的结果字典
        # 查询指标项目信息
        filter_params, page_limit_params = "1=1", ""
        sql = SELECT_ALL_INDICATOR_ITEMS % (filter_params, page_limit_params)
        logging.getLogger(__name__).info('执行SQL查询：{}'.format(sql))
        cursor, conn = self._db_module.get_conn()
        indicator_item_df = pd.read_sql(sql, con=conn)
        if indicator_item_df.size <= 0:
            logging.getLogger(__name__).warning('指标项目表无记录')
            return
        indicator_items = indicator_item_df.to_dict(orient="records")
        for key in self._category_dict.values():
            result_dict[key] = dict()
        for item_dict in indicator_items:
            indicator_id = item_dict['id']
            indicator_category = item_dict['indicator_category']
            indicator_type = item_dict['indicator_type']
            indicator_name = item_dict['indicator_name']
            indicator_unit = item_dict['indicator_unit']
            # 拼接标题
            title = "{}（{}）".format(indicator_name, indicator_unit)
            item = {
                "indicator_id": indicator_id,
                "indicator_title": title,
                "indicator_type": indicator_type,
            }
            real_category = self._category_dict.get(indicator_category)
            result_dict[real_category][indicator_id] = item

    def _cache_last_year_data(self, year: int, result_dict: dict) -> None:
        """
        处理年初基数
        :param year: 年份
        :param result_dict: 结果字典
        :return:
        """
        # 查询年初数据，也即去年12月的数据
        # 过滤参数
        filter_params = "ih.indicator_year = '{}'".format(year - 1)
        filter_params = filter_params + " and ih.indicator_month = '{}'".format(12)
        # 分页查询参数
        page_limit_params = ""
        sql = SELECT_ALL_INDICATOR_HISTORY % (filter_params, page_limit_params)
        logging.getLogger(__name__).info('执行SQL查询：{}'.format(sql))
        cursor, conn = self._db_module.get_conn()
        last_year_df = pd.read_sql(sql, con=conn)
        if last_year_df.size <= 0:
            logging.getLogger(__name__).warning('指标历史表无{}年初记录'.format(year))
            # 如果年初无记录，则年初值当作0
            for category, item_dict in result_dict.items():
                for indicator_id, item in item_dict.items():
                    result_dict[category][indicator_id]["yearly_begin_value"] = Decimal(0)
            return
        last_year_items = last_year_df.to_dict(orient="records")
        for item_dict in last_year_items:
            indicator_id = item_dict['indicator_id']
            indicator_category = item_dict['indicator_category']
            indicator_value = item_dict['indicator_value']
            real_category = self._category_dict.get(indicator_category)
            if indicator_id not in result_dict[real_category]:
                continue
            result_dict[real_category][indicator_id]["yearly_begin_value"] = Decimal(str(indicator_value))

    def _cache_current_year_data(self, year, result_dict):
        """
        处理当年数据
        :param year: 年份
        :param result_dict: 结果字典
        :return:
        """
        # 过滤参数
        filter_params = "ih.indicator_year = '{}'".format(year)
        # 分页查询参数
        page_limit_params = ""
        sql = SELECT_INDICATOR_HISTORY_GROUP_BY_ID % (filter_params, page_limit_params)
        logging.getLogger(__name__).info('执行SQL查询：{}'.format(sql))
        cursor, conn = self._db_module.get_conn()
        year_df = pd.read_sql(sql, con=conn)
        if year_df.size <= 0:
            logging.getLogger(__name__).warning('指标历史表无{}年记录'.format(year))
            return
        last_year_items = year_df.to_dict(orient="records")
        for item_dict in last_year_items:
            indicator_id = item_dict['indicator_id']
            indicator_category = item_dict['indicator_category']
            real_category = self._category_dict.get(indicator_category)
            if indicator_id not in result_dict[real_category]:
                continue
            month_list = item_dict['month_list'].split(",")
            month_list_str = ["{}月".format(int(numeric_string)) for numeric_string in month_list]
            last_month = int(item_dict['last_month'])
            value_list = item_dict['value_list'].split(",")
            value_list_float = [Decimal(numeric_string) for numeric_string in value_list]
            indicator_value = Decimal(item_dict['last_indicator_value'])
            result_dict[real_category][indicator_id]["indicator_value"] = indicator_value
            result_dict[real_category][indicator_id]["month_list"] = month_list_str
            result_dict[real_category][indicator_id]["value_list"] = value_list_float
            (yearly, seasonal, monthly) = MonthUtils.calculate_month(year, last_month)
            year_begin_value = result_dict[real_category][indicator_id]["yearly_begin_value"]
            yearly_compare_value = indicator_value - year_begin_value
            result_dict[real_category][indicator_id]["yearly_compare_value"] = yearly_compare_value
            if seasonal == (year - 1, 12):
                seasonal_begin_value = year_begin_value
            else:
                seasonal_index = int(seasonal[1]) - 1
                # 如果季度数据无记录，则当作0
                if 0 <= seasonal_index < len(value_list_float):
                    seasonal_begin_value = value_list_float[seasonal_index]
                else:
                    seasonal_begin_value = Decimal(0)
            seasonal_compare_value = indicator_value - seasonal_begin_value
            result_dict[real_category][indicator_id]["seasonal_compare_value"] = seasonal_compare_value
            if monthly == (year - 1, 12):
                monthly_begin_value = year_begin_value
            else:
                monthly_index = int(monthly[1]) - 1
                # 如果月度数据无记录，则当作0
                if 0 <= monthly_index < len(value_list_float):
                    monthly_begin_value = value_list_float[monthly_index]
                else:
                    monthly_begin_value = Decimal(0)
            monthly_compare_value = indicator_value - monthly_begin_value
            result_dict[real_category][indicator_id]["monthly_compare_value"] = monthly_compare_value

    def _cache_dashboard_data(self, year: int):
        """
        缓存看板查询的数据
        :param year: 分析年份
        :return:
        """
        # 处理结果字典
        result_dict = dict()
        # 查询指标项目信息
        self._cache_indicator_item_dict(result_dict)

        # 查询年初数据，也即去年12月的数据
        self._cache_last_year_data(year, result_dict)

        # 查询当年所有数据
        self._cache_current_year_data(year, result_dict)

        # 按ID排序
        result = dict()
        result.update(self._empty_records_dict)
        for key, value in result_dict.items():
            result[key] = [value.get(key) for key in sorted(value)]

        # 缓存处理后的数据
        if year not in self._cached_dashboard_data.keys():
            self._cached_dashboard_data[year] = result
        else:
            self._cached_dashboard_data.get(year).clear()
            self._cached_dashboard_data.get(year).update(result)

    def get_available_years(self):
        """
        获取看板数据的所有年份
        :return: 看板数据的所有年份
        """
        rows = self._db_module.select_all(
            sql=SELECT_MAX_UPDATE_TIME_INDICATOR_HISTORY,
        )
        all_years_dict = dict()
        if rows is None:
            logging.getLogger(__name__).warning('指标历史表无记录')
            return all_years_dict
        for row in rows:
            year = int(row[0])
            max_update_time = row[1]
            report_time = row[2]
            record_count = row[3]
            all_years_dict[year] = {
                "max_update_time": max_update_time.strftime(self._datetime_format),
                "report_time": report_time.strftime(self._datetime_format),
                "record_count": record_count,
            }
        return all_years_dict
