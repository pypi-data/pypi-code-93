from wrapt import decorator
from typing import Dict, Any
from sqlalchemy import orm, engine
from functools import cached_property


class SqlEngine(object):

    Session = orm.Session

    def __init__(self, uri: str, pool_size: int = 1):
        self.uri = uri
        self.pool_size = pool_size

    @property
    def settings(self) -> Dict[str, Any]:
        return {
            'echo': False,
            'pool_pre_ping': True,
            'pool_size': self.pool_size,
        }

    @cached_property
    def engine(self) -> engine.Engine:
        return engine.create_engine(self.uri, **self.settings)

    @cached_property
    def session_class(self) -> orm.scoped_session:
        orm.configure_mappers()
        factory = orm.sessionmaker(bind=self.engine, expire_on_commit=False)
        session_class = orm.scoped_session(factory)
        return session_class

    @cached_property
    def registry(self) -> orm.registry:
        return orm.registry()

    @cached_property
    def ModelBase(self) -> orm.declarative_base:
        return self.registry.generate_base()
        # return orm.declarative_base()

    def make_session(self):
        """
        Create a new database session.

        :rtype: sqlalchemy.orm.Session
        """
        return self.session_class()

    def session(self):
        """
        Function decorator which injects a "session" named parameter
        if it doesn't already exists
        """
        @decorator
        def session_decorator(wrapped, instance, args, kwargs):
            session = kwargs.setdefault('session', self.make_session())
            try:
                return wrapped(*args, **kwargs)
            finally:
                session.close()

        return session_decorator

    def atomic(self):
        """
        Function decorator which injects a "session" named parameter
        if it doesn't already exists, and wraps the function in an
        atomic transaction.
        """
        @decorator
        def atomic_wrapper(wrapped, instance, args, kwargs):
            session: orm.Session = kwargs.setdefault('session', self.make_session())
            session.begin()

            try:
                return_value = wrapped(*args, **kwargs)
            except:
                session.rollback()
                raise
            else:
                session.commit()
                return return_value
            finally:
                session.close()

        return atomic_wrapper
