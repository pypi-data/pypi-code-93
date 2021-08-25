from coopio.ICsvDataService import ICsvDataService, T
from typing import List
from coopio.IDataProcessor import IDataProcessor
from typing import List
from coopio.ICsvDataService import ICsvDataService
import pandas as pd
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import UUIDType
from mapper.object_mapper import ObjectMapper
from coopio.sql.SQLDataService import SqlDataService

class Dummy:
    def __init__(self, id, a, b, c):
        self.id = id
        self.a = a
        self.b = b
        self.c = c

    def __str__(self):
        return f"a: {self.a}, b: {self.b}, c: {self.c} ({self.id})"

    def __repr__(self):
        return self.__str__()

Base = declarative_base()
class ORM_Dummy(Base):
    __tablename__ = "dummies"
    id = db.Column(db.Integer, primary_key=True)
    a = db.Column(db.String)
    b = db.Column(db.String)
    c = db.Column(db.String)

def init_sql_dataservice(servername, db_name):


    orm_obj_mapping_factory = ObjectMapper()
    orm_obj_mapping_factory.create_map(ORM_Dummy, Dummy, {'id': lambda x: x.id,
                                                          'a': lambda x: x.a,
                                                          'b': lambda x: x.b,
                                                          'c': lambda x: x.c})
    orm_obj_mapping_factory.create_map(Dummy, ORM_Dummy, {'id': lambda x: x.id,
                                                          'a': lambda x: int(x.a),
                                                          'b': lambda x: int(x.b),
                                                          'c': lambda x: int(x.c)})
    ds = SqlDataService(servername, db_name, Base, orm_obj_mapping_factory, recreate_db_if_existing=True,
                        create_if_missing=True)

    return ds


class CsvDataService_Dummy(ICsvDataService):

    def __init__(self, data_file_path: str):
        ICsvDataService.__init__(self, data_file_path, obj_identifier='a')

    def translate_from_data_rows(self, Dummy, df: pd.DataFrame) -> List[Dummy]:
        ret_dummies = []

        for i, row in df.iterrows():
            new_dummy = Dummy(
                id=i,
                a=row['a'],
                b=row['b'],
                c=row['c']
            )
            ret_dummies.append(new_dummy)

        return ret_dummies

    def dummies(self, ids: List[str] = None) -> List[Dummy]:

        return self.retrieve_objs(Dummy, ids)


class DummyDataProcessor(IDataProcessor):
    def __init__(self, primary, secondaries):
        IDataProcessor.__init__(self, primary, 'a', secondaries)

    def dummies(self, ids: List[str] = None) -> List[Dummy]:
        dummies = self.retrieve_objs(Dummy, ids)
        return [x for x in dummies]
