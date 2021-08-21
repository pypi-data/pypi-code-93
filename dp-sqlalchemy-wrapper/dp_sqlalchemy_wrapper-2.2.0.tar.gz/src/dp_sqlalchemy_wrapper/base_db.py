import sqlalchemy
from abc import ABC, abstractmethod
from typing import Callable
from sqlalchemy.orm.decl_api import DeclarativeMeta
from .base_config import BaseConfig



class BaseDB(ABC):
    sa = sqlalchemy

    def __init__(self, db_config: BaseConfig, Base: DeclarativeMeta) -> None:
        if (db_config.validate()):
            self._config = db_config
        self._engine = None
        self._Session = None # session factory
        self._Base = Base
    
    @property
    def config(self):
        return self._config

    @property
    def engine(self):
        return self._get_engine()
    
    @property
    def Session(self):
        return self._get_Session()

    @property
    def registry(self):
        return self.Base.registry
    
    @property
    def Base(self):
        return self._Base


    def _get_engine(self):
        if self._engine is None:
            self._engine = self.sa.engine.create_engine(self.config.db_url, echo=True, future=True)
        return self._engine


    def _get_Session(self):
        if self._Session is None:
            session_factory = self.sa.orm.sessionmaker(bind=self.engine)
            self._Session = self.sa.orm.scoped_session(session_factory) # still a factory
        return self._Session

    
    def run_in_session_context(self, runFn: Callable[[sqlalchemy.orm.Session], any]) -> any:
        with self.Session() as session:
            return runFn(session)

    def run_in_transaction_context(self, runFn: Callable[[sqlalchemy.orm.Session], any]) -> any:
        with self.Session() as session:
            with session.begin():
                return runFn(session)

    def create_all_tables(self):
        self.registry.metadata.create_all(self.engine)

    def drop_all_tables(self):
        self.registry.metadata.drop_all(self.engine)
    
    def count_declared_tables(self):
        return len(self.registry.metadata.sorted_tables)
    
    def count_tables_in_db(self):
        def count_table(session: sqlalchemy.orm.Session):
            result = session.execute(
                "SELECT count(*) FROM sqlite_master WHERE type = 'table';"
            )
            return result.scalar()
        return self.run_in_session_context(count_table)

    def populate_all_tables(self):
        self.run_in_session_context(self._populate_all_tables)

    @abstractmethod
    def _populate_all_tables(self, session: sqlalchemy.orm.Session):
        pass 
    
    def setup_database(self):
        self.create_all_tables()
        self.populate_all_tables()

    def reset_database(self):
        self.drop_all_tables()
        self.setup_database()
    
    def reset_orm_metadata(self):
        self.registry.metadata = self.sa.sql.schema.MetaData()

