"""get session and engine for sqlalchemy sqlite"""
# py -m build
# py -m twine upload --repository pypi dist/*
# py -m pip install sqlalchemy-sqlite-session --index-url https://pypi.org/simple/
# py -m pip install -U sqlalchemy-sqlite-session --index-url https://pypi.org/simple/
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def get_sqlite_session(path_db: str):
    if os.path.exists(path_db):
        path_str = 'sqlite:///' + path_db
        db_engine = create_engine(path_str, echo=False)
        db_session = Session(db_engine)
        return db_session
    else:
        raise Exception(f">>> No such file {path_db}")


def get_sqlite_engine(path_db: str):
    if os.path.exists(path_db):
        path_str = 'sqlite:///' + path_db
        db_engine = create_engine(path_str, echo=False)
        return db_engine
    else:
        raise Exception(f">>> No such file {path_db}")
