
from typing import Union
import datetime

from ..api.raw import RawDataApi
from ..api.basic import BasicDataApi
from ..api.derived import DerivedDataApi
from ..api.view import ViewDataApi


class DataManager:

    def __init__(self, start_time, end_time):
        # start_time: None, datetime or '20100101'
        # end_time:   None, datetime or '20100101'
        self.start_time = start_time if isinstance(start_time, datetime.datetime) else datetime.datetime.strptime(start_time,'%Y%m%d')
        self.end_time = end_time if isinstance(end_time, datetime.datetime) else datetime.datetime.strptime(end_time,'%Y%m%d')
        if self.end_time.date() == datetime.datetime.now().date():
            self.end_time = self.end_time - datetime.timedelta(days=1)

    def init(self):
        pass

    def terminate(self):
        pass

    @property
    def start_date(self):
        return self.start_time.date()

    @property
    def end_date(self):
        return self.end_time.date()

    @staticmethod
    def _db_api_helper(api_object: Union[RawDataApi, BasicDataApi, DerivedDataApi, ViewDataApi], func_name: str, *args, **kwargs):
        if func_name.startswith("__"):
            print(f'should not call func that starts with "__" (name){func_name}')
            return

        try:
            func = getattr(api_object, func_name)
        except AttributeError as e:
            print(e)
            return

        if not callable(func):
            print(f'{func_name} is not callable')
            return
        return func(*args, **kwargs)

    # 读取 raw db 中的数据
    @staticmethod
    def raw_data(func_name: str, *args, **kwargs):
        return DataManager._db_api_helper(RawDataApi(), func_name, *args, **kwargs)

    # 读取 basic db 中的数据
    @staticmethod
    def basic_data(func_name: str, *args, **kwargs):
        return DataManager._db_api_helper(BasicDataApi(), func_name, *args, **kwargs)

    # 读取 derived db 中的数据
    @staticmethod
    def derived_data(func_name: str, *args, **kwargs):
        return DataManager._db_api_helper(DerivedDataApi(), func_name, *args, **kwargs)

    # 读取 view db 中的数据
    @staticmethod
    def view_data(func_name: str, *args, **kwargs):
        return DataManager._db_api_helper(ViewDataApi(), func_name, *args, **kwargs)
