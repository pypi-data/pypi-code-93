import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import UUIDType
from uuid import uuid4
import random as rnd
import pandas as pd
import logging
import datetime
from coopio.sql.SQLDataService import SqlDataService, get_sql_connection, delete_db
from mapper.object_mapper import ObjectMapper

import unittest


letters = 'abcdefghijklmnopqrstuvwxyz'
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def pretty_print_dataframe(df: pd.DataFrame,
                           title: str = None,
                           display_width: int = 2000,
                           display_max_columns: int = 2000,
                           display_max_rows: int = 500,
                           float_format: str = '%.3f',
                           ):
    if title:
        print(title)

    with pd.option_context('display.max_rows', display_max_rows,
                           'display.max_columns', display_max_columns,
                           'display.width', display_width,
                           'display.float_format', lambda x: float_format % x):
        print(f"{df}\n")

Base = declarative_base()

class ORM_Account(Base):
    __tablename__ = "accounts"
    id = db.Column(UUIDType, primary_key=True)
    name = db.Column(db.String)
    active = db.Column(db.Boolean)

class Account:
    def __init__(self,
                 id,
                 name,
                 active):
        self.id = id
        self.name = name
        self.active = active



class Test_SQLDataService(unittest.TestCase):
    servername = r'localhost\SQLEXPRESS'
    db_name = 'unittestdbforSQLDataService'

    def _instantiate_ds(self, orm_obj_mapping_factory = None) -> SqlDataService:
        # Create DataService
        return SqlDataService(self.servername, self.db_name, Base, orm_obj_mapping_factory, recreate_db_if_existing=False, create_if_missing=True)

    def _addORMAccounts(self, ds, n):
        accounts = [ORM_Account(name=''.join(rnd.choices(letters, k=n)),
                            id=uuid4(),
                            active=rnd.choice([True, False])) for ii in range(5)]
        ds.add_or_update(ORM_Account, accounts)

    def _addAccounts(self, ds, n):
        accounts = [Account(name=''.join(rnd.choices(letters, k=n)),
                            id=uuid4(),
                            active=rnd.choice([True, False])) for ii in range(5)]
        ds.add_or_update(Account, accounts)

    def tearDown(self):
        delete_db(self.servername, self.db_name)

    def test_instantiatedb(self):
        ######### ARRANGE ############
        verify_db_sql = f"select * from sys.databases where name = '{self.db_name}'"

        # get a connection
        sqlcon = get_sql_connection(self.servername, "master")

        ########## ACT ###############
        ds = self._instantiate_ds()
        # verify the db exists
        with sqlcon.connect() as connection:
            results = connection.execute(verify_db_sql)
            rows = results.fetchall()

        ######### ASSERT ############
        self.assertEqual(len(rows), 1, f"DB {self.db_name} was not created successfully")

    def test_addobjects(self):
        ######### ARRANGE ############
        n_accounts = 5

        ########## ACT ###############
        ds = self._instantiate_ds()
        self._addORMAccounts(ds, n_accounts)

        # retrieve accounts
        accounts = ds.retrieve_objs(ORM_Account)

        ######### ASSERT ############
        self.assertEqual(len(accounts), n_accounts)
        self.assertEqual(type(accounts[0]), ORM_Account)

    def test_addobjectswithORMMapper(self):
        ######### ARRANGE ############
        n_accounts = 5
        orm_obj_mapping_factory = ObjectMapper()
        orm_obj_mapping_factory.create_map(ORM_Account, Account, {'id': lambda x: x.id})
        orm_obj_mapping_factory.create_map(Account, ORM_Account, {'id': lambda x: x.id})

        ########## ACT ###############
        ds = self._instantiate_ds(orm_obj_mapping_factory=orm_obj_mapping_factory)
        self._addAccounts(ds, n_accounts)

        # retrieve accounts
        accounts = ds.retrieve_objs(Account)

        ######### ASSERT ############
        self.assertEqual(len(accounts), n_accounts)
        self.assertEqual(type(accounts[0]), Account)


if __name__ == "__main__":
    unittest.main()