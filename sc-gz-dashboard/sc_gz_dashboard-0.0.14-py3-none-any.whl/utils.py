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
import decimal
import json
import logging

from sc_config.config import Config
from sc_utilities import Singleton

from .configs.default import DEFAULT_CONFIG


class ConfigUtils(metaclass=Singleton):
    """
    配置文件相关工具类
    """

    _config = None

    def __init__(self):
        pass

    @classmethod
    def load_configurations(cls):
        """
        加载配置文件
        :return:
        """
        try:
            # load configurations
            cls._config = Config.create(project_name="sc-gz-dashboard", defaults=DEFAULT_CONFIG)
        except Exception as error:
            cls._config = {}
            logging.getLogger(__name__).exception("failed to read configuration", exc_info=error)

    @classmethod
    def get_config(cls):
        """
        获取配置信息
        :return: 配置信息字典
        """
        if cls._config is None:
            cls.load_configurations()
        return cls._config


class MonthUtils:

    @classmethod
    def calculate_month(cls, year_str, month_str):
        """
        计算月份：年初、季初、月初
        :param year_str: 年份
        :param month_str: 月份
        :return: (
                    (year, yearly_compare_month),
                    (year, seasonal_compare_month),
                    (year, monthly_compare_month)
                )，年初对应的年份和月份、季初对应的年份和月份、月初对应的年份和月份
        """
        illegal_result = (None, None), (None, None), (None, None)
        try:
            year = int(year_str)
        except ValueError:
            logging.getLogger(__name__).error("年份参数错误：{}".format(year_str))
            return illegal_result
        except TypeError:
            logging.getLogger(__name__).error("年份参数错误：{}".format(year_str))
            return illegal_result
        try:
            month = int(month_str)
        except ValueError:
            logging.getLogger(__name__).error("月份参数错误：{}".format(month_str))
            return illegal_result
        except TypeError:
            logging.getLogger(__name__).error("月份参数错误：{}".format(month_str))
            return illegal_result

        # 年初为去年的12月
        yearly = (year - 1, 12)

        # 季度的开始月份
        seasons = [1, 4, 7, 10, 13]
        # 计算季度初
        if seasons[0] <= month < seasons[1]:
            seasonal_start = seasons[0]
        elif seasons[1] <= month < seasons[2]:
            seasonal_start = seasons[1]
        elif seasons[2] <= month < seasons[3]:
            seasonal_start = seasons[2]
        elif seasons[3] <= month < seasons[4]:
            seasonal_start = seasons[3]
        else:
            logging.getLogger(__name__).error("月份参数错误：{}".format(month_str))
            return illegal_result
        # 计算季初
        last_month = seasonal_start - 1
        if last_month == 0:
            seasonal = yearly
        else:
            seasonal = (year, last_month)

        # 计算月初，即上个月
        last_month = month - 1
        if last_month == 0:
            monthly = yearly
        else:
            monthly = (year, last_month)
        return yearly, seasonal, monthly


class DecimalEncoder(json.JSONEncoder):
    """
    Decimal类型的数据JSON序列化类
    """

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)

        super(DecimalEncoder, self).default(o)


__all__ = {
    "ConfigUtils",
    "MonthUtils",
    "DecimalEncoder",
}
