"""Pytest fixtures"""
from sqlalchemy import create_engine  # type: ignore
from datetime import date, datetime

import pytest

from databasebaseclass.base import DatabaseBaseClass
from schema import Base
from sqlalchemy.orm import Session  # type: ignore
from schema import DatabaseDatetimeTest, DatabaseDateTest


class TestClass(DatabaseBaseClass):
    def __init__(self, conn_str):
        self.engine = create_engine(conn_str, echo=True, future=True)


@pytest.fixture(name='conn_str')
def fixture_conn_str(tmp_path_factory):
    """Fixture for the WorksheetMaker class"""
    conn_str = 'sqlite:///{}'.format(str(tmp_path_factory.mktemp('data') / 'test.db'))
    engine = create_engine(conn_str, echo=True, future=True)
    with engine.begin() as connection:
        Base.metadata.create_all(connection)

    with Session(bind=engine) as session:
        session.add_all([
            # Circulator Arrival
            DatabaseDateTest(
                date=date(2021, 5, 1),
                primary_key=1),
            DatabaseDateTest(
                date=date(2021, 5, 2),
                primary_key=2),
            DatabaseDateTest(
                date=date(2021, 5, 3),
                primary_key=3),
            DatabaseDateTest(
                date=date(2021, 5, 4),
                primary_key=4),
            DatabaseDatetimeTest(
                datetime=datetime(2021, 5, 1),
                primary_key=1),
            DatabaseDatetimeTest(
                datetime=datetime(2021, 5, 2),
                primary_key=2),
            DatabaseDatetimeTest(
                datetime=datetime(2021, 5, 3),
                primary_key=3),
            DatabaseDatetimeTest(
                datetime=datetime(2021, 5, 4),
                primary_key=4),
            ])
        session.commit()
    return conn_str


@pytest.fixture(name='test_class')
def fixture_testclass(conn_str):
    return TestClass(conn_str)
