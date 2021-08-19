import numpy as np
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker

from ...util.singleton import Singleton
from ...util.config import SurfingConfigurator

class RawDatabaseConnector(metaclass=Singleton):

    def __init__(self,db_tag=None):
        db_conn_str = SurfingConfigurator().get_db_settings(db_name='raw').to_conn_str()
        self.engine = create_engine(db_conn_str, pool_size=20, max_overflow=20, echo_pool=True)
        self.smaker = sessionmaker(bind=self.engine)
        self.scoped_smaker = scoped_session(self.smaker)

    @contextmanager
    def managed_session(self):
        session = self.scoped_smaker()
        try:
            yield session
        finally:
            session.close()

    def get_engine(self):
        return self.engine


class BasicDatabaseConnector(metaclass=Singleton):

    def __init__(self,db_tag=None):
        db_conn_str = SurfingConfigurator().get_db_settings(db_name='basic').to_conn_str()
        self.engine = create_engine(db_conn_str, pool_size=20, max_overflow=20, echo_pool=True)
        self.smaker = sessionmaker(bind=self.engine)
        self.scoped_smaker = scoped_session(self.smaker)

    @contextmanager
    def managed_session(self):
        session = self.scoped_smaker()
        try:
            yield session
        finally:
            session.close()

    def get_engine(self):
        return self.engine


class DerivedDatabaseConnector(metaclass=Singleton):

    def __init__(self,db_tag=None):
        db_conn_str = SurfingConfigurator().get_db_settings(db_name='derived').to_conn_str()
        self.engine = create_engine(db_conn_str, pool_size=20, max_overflow=20, echo_pool=True)
        self.smaker = sessionmaker(bind=self.engine)
        self.scoped_smaker = scoped_session(self.smaker)

    @contextmanager
    def managed_session(self):
        session = self.scoped_smaker()
        try:
            yield session
        finally:
            session.close()

    def get_engine(self):
        return self.engine


class ViewDatabaseConnector(metaclass=Singleton):

    def __init__(self):
        self.db_conn_str = SurfingConfigurator().get_db_settings(db_name='view').to_conn_str()
        self._connect()

    def _connect(self):
        self.engine = create_engine(
            self.db_conn_str,
            pool_size=20,
            max_overflow=20,
            echo_pool=True,
            pool_recycle=3600,
            pool_pre_ping=True,
        )
        self.session_maker = sessionmaker(bind=self.engine)
        self.scoped_maker = scoped_session(self.session_maker)

    @contextmanager
    def managed_session(self):
        if not self.engine:
            self._connect()
        session = self.scoped_maker()
        try:
            yield session
        finally:
            session.close()

    def get_engine(self):
        return self.engine

class TestDatabaseConnector(metaclass=Singleton):

    def __init__(self,db_tag=None):
        db_conn_str = SurfingConfigurator().get_db_settings(db_name='test').to_conn_str()
        self.engine = create_engine(db_conn_str, pool_size=20, max_overflow=20, echo_pool=True)
        self.smaker = sessionmaker(bind=self.engine)
        self.scoped_smaker = scoped_session(self.smaker)

    @contextmanager
    def managed_session(self):
        session = self.scoped_smaker()
        try:
            yield session
        finally:
            session.close()

    def get_engine(self):
        return self.engine

class TLDatabaseConnector(metaclass=Singleton):

    def __init__(self,db_tag=None):
        db_conn_str = SurfingConfigurator().get_db_settings(db_name='TL').to_conn_str()
        self.engine = create_engine(db_conn_str, pool_size=20, max_overflow=20, echo_pool=True)
        self.smaker = sessionmaker(bind=self.engine)
        self.scoped_smaker = scoped_session(self.smaker)
        event.listen(self.engine, "before_cursor_execute", self.add_own_encoders)

    def add_own_encoders(self, conn, cursor, query, *args):
        cursor.connection.encoders[np.int64] = lambda value, encoders: int(value)

    @contextmanager
    def managed_session(self):
        session = self.scoped_smaker()
        try:
            yield session
        finally:
            session.close()

    def get_engine(self):
        return self.engine