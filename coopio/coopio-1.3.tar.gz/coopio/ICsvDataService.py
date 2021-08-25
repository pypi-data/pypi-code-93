from abc import ABC, abstractmethod
import pandas as pd
import os
from typing import TypeVar, Dict, List
from coopio.IDataService import IDataService, T


class ICsvDataService(IDataService):

    def __init__(self, data_file_path: str, obj_identifier: str):
        self.data_file_path = data_file_path
        self.create_file_if_not_exists(self.data_file_path)
        self.obj_identifier = obj_identifier
        IDataService.__init__(self)

    def read_in_data(self, file_path: str):
        df = pd.read_csv(file_path)
        return df

    def write_data(self, df: pd.DataFrame, file_path: str):
        self.create_file_if_not_exists(file_path)
        df[self.obj_identifier] = df[self.obj_identifier].astype(str)
        df.to_csv(file_path, index=False)
        return True

    def create_file_if_not_exists(self, file_path):
        if not os.path.exists(file_path):
            with open(file_path, "w"):
                pass

    def add_or_update(self, obj_type: T, objs: List[T], objs_as_df: pd.DataFrame = None) -> List[type(T)]:
        if len(objs) == 0 or objs is None:
            return []

        try:
            all_data = self.read_in_data(self.data_file_path)
            all_data[self.obj_identifier] = all_data[self.obj_identifier].astype(str)
        except pd.errors.EmptyDataError:
            all_data = None
        except Exception as e:
            raise e

        if all_data is not None:
            updated_data = objs_as_df if objs_as_df is not None else pd.DataFrame([vars(obj) for obj in objs])
            updated_data[self.obj_identifier] = updated_data[self.obj_identifier].astype(str)

            all_data = (pd.concat([all_data, updated_data])
                            .drop_duplicates([self.obj_identifier], keep='last')
                            .sort_values(by=[self.obj_identifier], ascending=True)
                            .reset_index(drop=True))

        else:
            all_data = objs_as_df if objs_as_df is not None else pd.DataFrame([vars(obj) for obj in objs])

        if self.write_data(all_data, self.data_file_path):
            return self.retrieve_objs(obj_type=obj_type, ids=[str(vars(obj)[self.obj_identifier]) for obj in objs])
        else:
            raise Exception("Unable to update objects")

    def retrieve_objs(self, obj_type: T, ids: List[str] = None) -> List[type(T)]:

        df = self.retrieve_as_df(ids)

        ret = []
        if df is not None:
            ret = self.translate_from_data_rows(obj_type, df)

        return ret

    def retrieve_as_df(self, ids: List[str] = None) -> pd.DataFrame:
        try:
            existing_data = self.read_in_data(self.data_file_path)
        except:
            existing_data = None

        # Raise exception if the obj_identifier isnt in the dataframe.columns that was returned when data was read
        if existing_data is not None and self.obj_identifier not in existing_data.columns:
            raise KeyError(f"[{self.obj_identifier}] is not in the returned data for {type(self)}"
                           f"columns in data: [{[column for column in existing_data.columns]}]")

        if existing_data is not None and ids is not None:
            existing_data = existing_data[existing_data[self.obj_identifier].isin(ids)]

        return existing_data

    def delete(self, obj_type: T, ids: List[str]) -> Dict[str, bool]:
        try:
            existing_data = self.read_in_data(self.data_file_path)
        except:
            existing_data = None

        if existing_data is None:
            return {id: True for id in ids}

        ret = {}
        new_data = existing_data
        for id in ids:
            try:
                existing_indexes = [i for i, line in existing_data.iterrows() if str(line[self.obj_identifier]) == id]

                new_data = new_data.drop(existing_indexes)
                ret[id] = True
            except:
                ret[id] = False

        self.write_data(new_data, self.data_file_path)
        return ret

    @abstractmethod
    def translate_from_data_rows(self, obj_type: T, df: pd.DataFrame) -> List[T]:
        pass
