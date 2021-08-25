import functools
import logging
import typing
from contextlib import contextmanager
from copy import deepcopy
from functools import partial

import sqlalchemy as sa
import sqlalchemy.exc
import sqlalchemy.orm.session as orms
from box import Box
from geoalchemy2.shape import to_shape
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

from . import sqla_orms
from .. import logger
from ..common import utils


def get_engine(db_configs: dict, create_if_not_exists=False, drivername='postgres', **connection_kwargs):
    db_configs = db_configs.copy()
    # database=
    database = connection_kwargs.pop('database') if connection_kwargs.get('database') else db_configs.pop('database')
    # if connection_kwargs.get('database'): database=connection_kwargs.pop('database')
    # elif db_configs.get('database'): database=db_configs.pop('database')
    engine_creator = lambda db: sa.create_engine(URL(**dict(dict(db_configs, drivername=drivername, database=db),
                                                            **connection_kwargs)), echo=False)
    
    logger.trace(logging.INFO, skimpy=True)
    
    def __create_database():
        eng = engine_creator('postgres')
        conn = eng.connect()
        conn.execute('commit')
        conn.execute(f'create database {database};')
        conn.close()
    
    if create_if_not_exists:
        try:
            engine = engine_creator(database)
            engine.connect()
        except sa.exc.OperationalError:
            logger.info(f"Database '%s' does not exist.", database)
            __create_database()
            engine = engine_creator(database)
    else:
        engine = engine_creator(database)
    engine.connect().execute("create extension if not exists postgis;"
                             "create extension if not exists postgis_topology;")
    # simple_logger.info('engine: %s',engine)
    return engine


def get_session(engine, autoflush=True, autocommit=False, expire_on_commit=True, info=None, **kwargs) -> orms.Session:
    session: orms.Session = sessionmaker(bind=engine, autoflush=autoflush, autocommit=autocommit,
                                         expire_on_commit=expire_on_commit,
                                         info=info, **kwargs)()
    return session


@contextmanager
def session_context(engine, autoflush=True, autocommit=False, expire_on_commit=True, info=None, **kwargs):
    session = get_session(engine, autoflush=autoflush, autocommit=autocommit, expire_on_commit=expire_on_commit,
                          info=info, **kwargs)
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.exception(str(e))
        session.rollback()
        raise
    finally:
        session.close()


class QueryItem(sqla_orms.Reconnectable):
    _protected_keys = ['info',
                       *['_QueryItem' + x for x in ['__item', '__engine_creator', '__obj_class', '__primary_keys']]]
    
    def __init__(self, obj: sqla_orms.Base, engine_creator, pkeys):
        self.__item = Box(deepcopy(obj.__dict__))
        self.__obj_class = obj.__class__
        self.__engine_creator = engine_creator
        self.__primary_keys = tuple([x for x in pkeys] if type(pkeys[0]) is str else [x.key for x in pkeys])
    
    @property
    def primary_vals(self):
        return tuple(getattr(self.__item, x) for x in self.__primary_keys)
    
    @property
    def info(self):
        return sqla_orms.get_info(self.__item)
    
    def reconnect(self, session):
        target_obj = session.query(self.__obj_class).get(self.primary_vals)
        assert target_obj is not None, f"Query on {self.__obj_class} returned None."
        return target_obj
    
    def get_wkt(self, key='geom'):
        return to_shape(self.__item[key]).wkt
    
    def __setattr__(self, key, value):
        if key in self._protected_keys:
            self.__dict__[key] = value
        else:
            with session_context(self.__engine_creator()) as temp_session:
                setattr(self.reconnect(temp_session), key, value)
                self.__item[key] = value
    
    def __repr__(self):
        return f"QueryItem: {utils.reprer(self.__item)}"
    
    def __getattr__(self, item):
        if item in self._protected_keys:
            return self.__dict__[item]
        return self.__item[item]
    
    def __getstate__(self):
        return self.__dict__
    
    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)


class Manager(object):
    _protected_keys = ['_Manager' + x for x in ['__engine_creator', '__engine', '__session', '__fire_session',
                                                '__box', '__query_item_creator', '__temp_ident']]
    
    def __init__(self, db_configs: dict, create_if_not_exists=False, **connection_kwargs):
        self.__engine_creator = partial(get_engine, db_configs, create_if_not_exists, **connection_kwargs)
        self.__engine = None
        self.__session = None
        self.__query_item_creator = partial(QueryItem, engine_creator=self.__engine_creator)
        self.__box = Box()
        self.__temp_ident = None
    
    @property
    def engine(self):
        if self.__engine is None:
            self.__engine = self.__engine_creator()
        return self.__engine
    
    @property
    def session(self):
        if self.__session is None or not self.__session.is_active:
            self.__session = get_session(self.engine)
        return self.__session
    
    def new_session(self, autoflush=True, autocommit=False, expire_on_commit=True, info=None, **kwargs):
        self.__session = session = get_session(self.engine, autoflush=autoflush, autocommit=autocommit,
                                               expire_on_commit=expire_on_commit, info=info, **kwargs)
        return session
    
    @staticmethod
    def commit_and_close(session):
        session.commit()
        session.close()
    
    def create_table(self, table_class: sqla_orms.Base):
        if self.engine.dialect.has_table(self.engine, table_class.__tablename__):
            logger.info(f"Table '%s' already exists.", table_class.__tablename__)
        else:
            logger.info(f"Creating table '%s'...", table_class.__tablename__)
            table_class.__table__.create(self.engine)
        return self
    
    @contextmanager
    def session_context(self, **kwargs) -> orms.Session:
        self.__session = session = get_session(self.engine, **kwargs)
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.exception(str(e))
            session.rollback()
            raise
        finally:
            session.close()
    
    def query_get(self, entity: typing.Type[sqla_orms.KeysBase], *primary_keys):
        assert len(primary_keys) > 0, 'When querying using query_get, you should provide at least one primary_key.'
        with self.session_context() as session:
            obj = QueryItem(session.query(entity).get(primary_keys), self.__engine_creator, entity.primary_keys)
            return obj
    
    def get_wrapped(self, obj):
        return QueryItem(obj, self.__engine_creator, obj.primary_keys)
    
    def session_wrapper(self, new_engine=True, autoflush=True, autocommit=False, expire_on_commit=True, info=None,
                        **kwargs):
        def wrapper_getter(func):
            @functools.wraps(func)
            def wrapper(*args, **_kwargs):
                has_classarg = utils.func_has_classarg(func, args)
                if new_engine:
                    self.__engine = self.__engine_creator()
                with self.session_context(autoflush=autoflush, autocommit=autocommit,
                                          expire_on_commit=expire_on_commit, info=info, **kwargs) as session:
                    if has_classarg:
                        result = func(args[0], session, *args[1:], **_kwargs)
                    else:
                        result = func(session, *args, **_kwargs)
                    return result
            
            return wrapper
        
        return wrapper_getter
