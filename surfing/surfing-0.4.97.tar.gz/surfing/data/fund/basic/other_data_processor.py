
import datetime
import traceback
import json
import numpy as np
import pandas as pd
from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from .basic_data_helper import BasicDataHelper
from ...view.basic_models import OverseaFundInfo, OverseaFundNav

class OtherBasicData:

    def __init__(self, data_helper: BasicDataHelper):
        self._data_helper = data_helper
        self._raw_data_api = RawDataApi()
        self._basic_data_api = BasicDataApi()

    def make_fund_id_func(self):
        return lambda x : 'os_' + x

    def oversea_fund_nav(self):
        df = self._raw_data_api.get_oversea_fund_nav()
        df['codes'] = df.codes.map(self.make_fund_id_func)
        df = df.drop(columns=['_update_time'])
        self._data_helper._upload_basic(df, OverseaFundNav.__table__.name)

    def oversea_fund_info(self):
        df = self._raw_data_api.get_over_sea_fund_info()
        df['codes'] = df.codes.map(self.make_fund_id_func)
        df = df.drop(columns=['_update_time'])
        self._data_helper._upload_basic(df, OverseaFundInfo.__table__.name)