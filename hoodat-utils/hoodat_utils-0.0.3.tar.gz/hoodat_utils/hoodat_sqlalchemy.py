# Base Imports
import logging

# Libraries
import pandas as pd

# SqlAlchemy Imports
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError


class HoodatSqlalchemy():

    def __init__(self, sqlalchemy_database_uri):
        self.sqlalchemy_database_uri = sqlalchemy_database_uri
        self.engine = create_engine(self.sqlalchemy_database_uri)

    def commit_pandas_df(self, df, table, record_func):
        session = Session(self.engine)
        logging.info(
            f"Populating {table} table")
        n_rows = df.shape[0]
        logging.info(f"Total rows: {n_rows}")
        for i in range(n_rows):
            x = df.iloc[i]
            try:
                record = record_func(x)
                session.add(record)
                session.flush()
            except IntegrityError as e:
                logging.info("Record already exists in db")
                logging.info(e)
                session.rollback()
            else:
                logging.info("Adding row")
                session.commit()
        session.close()
