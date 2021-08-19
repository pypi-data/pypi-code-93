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

import pandas as pd
from flask_restful import Resource, reqparse

from sc_gz_dashboard.db.common_db_module import CommonDBModule
from sc_gz_dashboard.db.common_sql import *
from sc_gz_dashboard.exceptions import *


class IndicatorHistoryList(Resource):

    def __init__(self):
        self._db_module = CommonDBModule()

    def _get_indicator_history_list(self, args: dict):
        """
        获取指标历史清单
        :param args: 传入参数列表，包括：年份、指标分类、指标类型，页码，每页大小
        :return: 指标历史清单
        """
        page, size, filter_params, page_limit_params = self._parse_get_parameters(args)
        # 查询总数
        sql = SELECT_ALL_INDICATOR_HISTORY_COUNT % filter_params
        logging.getLogger(__name__).info('执行SQL查询：{}'.format(sql))
        rows = self._db_module.select_one(sql=sql)
        total = rows[0]
        if total == 0:
            logging.getLogger(__name__).warning('指标历史表无记录')
            return {
                "current": page,
                "size": size,
                "total": total,
                "records": [],
            }

        # 查询分页记录
        sql = SELECT_ALL_INDICATOR_HISTORY % (filter_params, page_limit_params)
        logging.getLogger(__name__).info('执行SQL查询：{}'.format(sql))
        cursor, conn = self._db_module.get_conn()
        df = pd.read_sql(sql, con=conn)
        df["report_time"] = df["report_time"].apply(lambda x: x.strftime('%Y-%m-%d'))
        result = {
            "current": page,
            "size": size,
            "total": total,
            "records": df.to_dict(orient="records"),
        }
        return result

    def _parse_get_parameters(self, args):
        """
        解析get方法的参数
        :param args: 传入参数
        :return: 当前页码，每页大小，过滤条件，分页控制
        """
        # 页码
        page = args.get("page")
        if page is not None and page != "":
            try:
                page = int(page)
            except ValueError:
                raise ParameterException("当前页码不是整数")
            except TypeError:
                raise ParameterException("当前页码不是整数")
            if page <= 0:
                raise ParameterException("当前页码必须大于0")
        else:
            page = 1
        # 每页大小
        size = args.get("size")
        if size is not None and size != "":
            try:
                size = int(size)
            except ValueError:
                raise ParameterException("每页大小不是整数")
            except TypeError:
                raise ParameterException("每页大小不是整数")
            if size <= 0:
                raise ParameterException("每页大小必须大于0")
            if size > 100:
                raise ParameterException("每页大小必须小于或者等于100")
        else:
            size = 10
        # 年份
        indicator_year = args.get("indicator_year")
        if indicator_year is not None and indicator_year != "":
            try:
                indicator_year = int(indicator_year)
            except ValueError:
                raise ParameterException("年份不是整数")
            except TypeError:
                raise ParameterException("年份不是整数")
            if indicator_year <= 0:
                raise ParameterException("年份必须大于0")
        # 指标分类、指标类型、指标名称级联
        indicator_items = args.get("indicator_item[]")
        if indicator_items is None or len(indicator_items) == 0:
            indicator_category = ""
            indicator_type = ""
            indicator_id = ""
        elif len(indicator_items) == 1:
            indicator_category = indicator_items[0]
            indicator_type = ""
            indicator_id = ""
        elif len(indicator_items) == 2:
            indicator_category = indicator_items[0]
            indicator_type = indicator_items[1]
            indicator_id = ""
        else:
            indicator_category = indicator_items[0]
            indicator_type = indicator_items[1]
            indicator_id = indicator_items[2]

        if indicator_id is not None and indicator_id != "":
            try:
                indicator_id = int(indicator_id)
            except ValueError:
                raise ParameterException("指标名称不存在")
            except TypeError:
                raise ParameterException("指标名称不存在")
            if indicator_id <= 0:
                raise ParameterException("指标名称不存在")
        # 过滤条件参数
        filter_params = "1=1"
        if indicator_id is not None and indicator_id != "":
            filter_params = filter_params + " and ih.indicator_id = '{}'".format(indicator_id)
        if indicator_year is not None and indicator_year != "":
            filter_params = filter_params + " and ih.indicator_year = '{}'".format(indicator_year)
        if indicator_category is not None and indicator_category != "":
            filter_params = filter_params + " and ii.indicator_category = '{}'".format(indicator_category)
        if indicator_type is not None and indicator_type != "":
            filter_params = filter_params + " and ii.indicator_type = '{}'".format(indicator_type)
        # 分页控制参数
        page_limit_params = "limit {0}, {1}".format((page - 1) * size, size)
        return page, size, filter_params, page_limit_params

    def get(self):
        """
        获取指标历史数据列表
        :return: 指标历史数据列表
        """
        parser = reqparse.RequestParser()
        # 指标分类、指标类型、指标名称级联
        parser.add_argument('indicator_item[]', action="append")
        # 指标年份
        parser.add_argument('indicator_year')
        # 当前页码
        parser.add_argument('page')
        # 分页大小
        parser.add_argument('size')

        args = parser.parse_args()
        logging.getLogger(__name__).info("获取指标历史列表的请求参数：{0}".format(args))
        try:
            history_list = self._get_indicator_history_list(args)
        except ParameterException as e:
            logging.getLogger(__name__).error(e)
            result_info = {'status': '00001', 'reason': str(e), 'data': {}}
            return result_info
        result_info = {'status': '00000', 'reason': '成功', 'data': history_list}
        return result_info

    def _parse_put_post_parameters(self, args):
        """
        解析put和post方法的参数
        :param args: 传入参数
        :return: indicator_id, indicator_year, indicator_month, indicator_value, report_time
        """
        # 页码
        indicator_id = args.get("indicator_id")
        if indicator_id is None or indicator_id == "":
            raise ParameterException("指标ID不能为空")
        try:
            indicator_id = int(indicator_id)
        except ValueError:
            raise ParameterException("指标ID不是整数")
        except TypeError:
            raise ParameterException("指标ID不是整数")
        if indicator_id <= 0:
            raise ParameterException("指标ID必须大于0")
        # 指标年份
        indicator_year = args.get("indicator_year")
        if indicator_year is None or indicator_year == "":
            raise ParameterException("指标年份不能为空")
        try:
            indicator_year = int(indicator_year)
        except ValueError:
            raise ParameterException("指标年份不是整数")
        except TypeError:
            raise ParameterException("指标年份不是整数")
        if indicator_year <= 0:
            raise ParameterException("指标年份必须大于0")
        # 指标月份
        indicator_month = args.get("indicator_month")
        if indicator_month is None or indicator_month == "":
            raise ParameterException("指标月份不能为空")
        try:
            indicator_month = int(indicator_month)
        except ValueError:
            raise ParameterException("指标月份不是整数")
        except TypeError:
            raise ParameterException("指标月份不是整数")
        if indicator_month <= 0 or indicator_month > 12:
            raise ParameterException("指标年份必须是1到12之间的整数")
        indicator_month = "{:02d}".format(indicator_month)
        # 指标值
        indicator_value = args.get("indicator_value")
        if indicator_value is None or indicator_value == "":
            raise ParameterException("指标值不能为空")
        try:
            indicator_value = float(indicator_value)
        except ValueError:
            raise ParameterException("指标值不是数字")
        except TypeError:
            raise ParameterException("指标值不是数字")
        # 统计日期
        report_time = args.get("report_time")
        if report_time is None or report_time == "":
            raise ParameterException("统计日期不能为空")
        try:
            report_time = datetime.strptime(report_time, "%Y-%m-%d")
        except ValueError:
            raise ParameterException("统计日期不是合法日期字符串")
        return indicator_id, indicator_year, indicator_month, indicator_value, report_time

    def put(self):
        """
        更新指标历史数据
        :return:
        """
        parser = reqparse.RequestParser()
        # 指标项目ID
        parser.add_argument('indicator_id')
        # 指标年份
        parser.add_argument('indicator_year')
        # 指标月份
        parser.add_argument('indicator_month')
        # 指标值
        parser.add_argument('indicator_value')
        # 指标统计时间
        parser.add_argument('report_time')
        args = parser.parse_args()
        logging.getLogger(__name__).info("编辑指标历史数据的请求参数：{0}".format(args))
        try:
            indicator_id, indicator_year, indicator_month, indicator_value, report_time = self._parse_put_post_parameters(
                args
            )
        except ParameterException as e:
            logging.getLogger(__name__).error(e)
            result_info = {'status': '00001', 'reason': str(e), 'data': {}}
            return result_info

        row = self._db_module.select_one(
            sql=CHECK_INDICATOR_HISTORY_EXISTENCE,
            param=(indicator_id, indicator_year, indicator_month)
        )
        if row is None:
            # 记录不存在，报错
            error_msg = '(指标ID:{}, 指标年份:{}, 指标月份:{})记录不存在'.format(indicator_id, indicator_year, indicator_month)
            logging.getLogger(__name__).error(error_msg)
            result_info = {'status': '00002', 'reason': "记录不存在", 'data': {}}
            return result_info
        # 记录已存在
        cursor, conn = self._db_module.execute(
            sql=UPDATE_INDICATOR_HISTORY_RECORD,
            param=(indicator_value, report_time, indicator_id, indicator_year, indicator_month),
        )
        rowcount = cursor.rowcount
        logging.getLogger(__name__).info('更新%s条记录', rowcount)
        lastrowid = cursor.lastrowid
        result_info = {'status': '00000', 'reason': '成功', 'data': {
            "rowId": lastrowid
        }}
        return result_info

    def post(self):
        """
        新增指标历史数据
        :return:
        """
        parser = reqparse.RequestParser()
        # 指标项目ID
        parser.add_argument('indicator_id')
        # 指标年份
        parser.add_argument('indicator_year')
        # 指标月份
        parser.add_argument('indicator_month')
        # 指标值
        parser.add_argument('indicator_value')
        # 指标统计时间
        parser.add_argument('report_time')
        args = parser.parse_args()
        logging.getLogger(__name__).info("新增指标历史数据的请求参数：{0}".format(args))
        try:
            indicator_id, indicator_year, indicator_month, indicator_value, report_time = self._parse_put_post_parameters(
                args
            )
        except ParameterException as e:
            logging.getLogger(__name__).error(e)
            result_info = {'status': '00001', 'reason': str(e), 'data': {}}
            return result_info

        row = self._db_module.select_one(
            sql=CHECK_INDICATOR_HISTORY_EXISTENCE,
            param=(indicator_id, indicator_year, indicator_month)
        )
        if row is not None and len(row) > 0 and row[0] > 0:
            # 记录已经存在，报错
            error_msg = '(指标ID:{}, 指标年份:{}, 指标月份:{})已存在'.format(indicator_id, indicator_year, indicator_month)
            logging.getLogger(__name__).error(error_msg)
            result_info = {'status': '00002', 'reason': "记录已存在", 'data': {}}
            return result_info
        # 记录不存在，则插入
        cursor, conn = self._db_module.execute(
            sql=INSERT_INDICATOR_HISTORY_RECORD,
            param=(indicator_id, indicator_year, indicator_month, indicator_value, report_time),
        )
        rowcount = cursor.rowcount
        logging.getLogger(__name__).info('插入%s条记录', rowcount)
        lastrowid = cursor.lastrowid
        result_info = {'status': '00000', 'reason': '成功', 'data': {
            "rowId": lastrowid
        }}
        return result_info
