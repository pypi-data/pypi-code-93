"""Test models for sqlalchemy"""
# pylint:disable=too-few-public-methods
from sqlalchemy import Column  # type: ignore
from sqlalchemy.ext.declarative import DeclarativeMeta  # type: ignore
from sqlalchemy.orm import declarative_base  # type: ignore
from sqlalchemy.types import Date, DateTime, Integer  # type: ignore

Base: DeclarativeMeta = declarative_base()


class DatabaseDateTest(Base):
    __tablename__ = 'test_table_date'

    primary_key = Column(Integer, primary_key=True)
    date = Column(Date)


class DatabaseDatetimeTest(Base):
    __tablename__ = 'test_table_datetime'

    primary_key = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
