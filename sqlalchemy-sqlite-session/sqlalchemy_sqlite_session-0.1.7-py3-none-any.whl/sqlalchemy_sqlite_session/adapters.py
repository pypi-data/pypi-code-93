"""get session and engine for sqlalchemy sqlite"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def get_sqlite_session(path_db: str):
    path_str = 'sqlite:///' + path_db
    db_engine = create_engine(path_str, echo=False)
    db_session = Session(db_engine)
    return db_session


def get_sqlite_engine(path_db: str):
    path_str = 'sqlite:///' + path_db
    db_engine = create_engine(path_str, echo=False)
    return db_engine
