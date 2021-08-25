from coopio.IDataService import IDataService
from typing import List, TypeVar, Dict, Generic
import pandas as pd

T = TypeVar('T')

class IDataProcessor(Generic[T]):
    def __init__(self, primary_data_service: IDataService, object_identifier: str, peripheral_equity_data_services: List[IDataService] = None):
        self.primary_data_service = primary_data_service
        self.peripheral_data_services = peripheral_equity_data_services if peripheral_equity_data_services else []

        self._obj_identifier = object_identifier

    @property
    def data_services(self):
        return [self.primary_data_service] + self.peripheral_data_services

    @property
    def obj_identifier(self):
        return self._obj_identifier

    @obj_identifier.setter
    def obj_identifier(self, val):
        if not type(val) == str:
            raise TypeError("obj_identifier can only be set to type [str]")
        self._obj_identifier = val

    def retrieve_objs(self, obj_type: T, ids: List[str] = None) -> List[type(T)]:
        return self.primary_data_service.retrieve_objs(obj_type=obj_type, ids=ids)

    def add_or_update(self, obj_type: T, objs: List[T], **kwargs) -> List[type(T)]:
        ret = {}
        for service in self.data_services:
            ret[service] = service.add_or_update(obj_type=obj_type, objs=objs, **kwargs)
        return ret[self.primary_data_service]

    def delete(self, obj_type: T, objs: List[T]) -> Dict[IDataService, bool]:
        ret = {}
        for service in self.data_services:
            delete_success = service.delete(obj_type=obj_type, ids=[str(vars(obj)[self.obj_identifier]) for obj in objs])
            ret[service] = all(success for equity_id, success in delete_success.items())

        return ret

    def retrieve_as_df(self, ids: List[str] = None) -> pd.DataFrame:
        return self.primary_data_service.retrieve_as_df(ids=ids)

    def overwrite_peripherals_with_primary(self, obj_type: T):
        primary_objs = self.primary_data_service.retrieve_objs(obj_type)
        for service in self.peripheral_data_services:
            current_objs = service.retrieve_objs(obj_type)
            delete_success = service.delete(obj_type=obj_type, ids=[str(vars(obj)[self.obj_identifier]) for obj in current_objs])
            service.add_or_update(obj_type, primary_objs)

