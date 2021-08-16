import logging
from threading import local

from neo4j import GraphDatabase, basic_auth
from pentaquark.config import gconf as config

logger = logging.getLogger(__name__)


def ensure_connection(func):
    def wrapper(self, *args, **kwargs):
        # must work both for Database and Transaction objects
        if hasattr(self, 'db'):  # Transaction
            _db = self.db
        else:  # Database
            _db = self

        if not _db.connected:
            _db.set_connection()
        return func(self, *args, **kwargs)
    return wrapper


class TransactionProxy(object):
    def __init__(self, db, access_mode=None):
        self.db = db
        self.access_mode = access_mode
        self.outermost = True

    @ensure_connection
    def __enter__(self):
        if self.db.active_transaction:
            self.outermost = False
            return self
        logger.debug("NEW TRANSACTION")
        self.db.begin()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.outermost:
            if exc_value:
                logger.debug("ROLLBACK TRANSACTION")
                self.db.rollback()
                return
            logger.debug("COMMIT TRANSACTION")
            self.db.commit()

    @property
    def queries(self):
        # proxy to db property
        return self.db.queries

    @property
    def number_of_queries(self):
        return len(self.queries)


class Database(local):
    def __init__(self):
        self.active_transaction = None
        self.driver = None
        self.connected = False
        self.queries = []

    def set_connection(self):
        logger.debug(
            "Connecting to %s with user: %s",
            config.NEO4J_URI, config.NEO4J_USER
        )
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=basic_auth(config.NEO4J_USER, config.NEO4J_PASSWORD),
            encrypted=config.NEO4J_ENCRYPTED_CONNECTION,
        )
        self.active_transaction = None
        self.connected = True

    def transaction(self, access_mode=None):
        return TransactionProxy(self, access_mode)

    @ensure_connection
    def begin(self, db=None):
        """
        Begins a new transaction, raises SystemError exception if a transaction is in progress
        """
        if self.active_transaction:
            raise SystemError("Transaction in progress")
        db = db or config.NEO4J_DEFAULT_DATABASE
        self.active_transaction = self.driver.session(database=db).begin_transaction()
        self.queries = []

    @ensure_connection
    def commit(self):
        """
        Commits the current transaction
        """
        r = None
        try:
            r = self.active_transaction.commit()
        except Exception as e:
            logger.error("Transaction Rollback after exception %s", e)
            self.rollback()
        finally:
            self.active_transaction.close()
            self.active_transaction = None
            self.queries = []
        return r

    @ensure_connection
    def rollback(self):
        """
        Rolls back the current transaction
        """
        self.active_transaction.rollback()
        self.active_transaction = None
        self.queries = []

    @staticmethod
    def _format_query(query, params, one_line=True):
        if not params:
            return query
        formatted_query = query
        for p, value in params.items():
            formatted_query = formatted_query.replace(f"${p}", str(value))
        if one_line:
            return formatted_query.replace("\n", "\t")  # remove line breaks
        return formatted_query

    @ensure_connection
    def cypher(self, query, params=None, db=None):
        """
        Runs a query on the database and returns a list of results and their headers.

        :param str query: A CYPHER query
        :param dict params: Dictionary of parameters
        :param str db: database name (neo4j 4 multi db support)
        :rtype: list
        :returns: list of dict with node properties as keys
        """

        if self.active_transaction:
            session = self.active_transaction
        else:
            # create a new session
            db = db or config.NEO4J_DEFAULT_DATABASE
            session = self.driver.session(database=db)

        query_with_param_display = self._format_query(query, params)
        logger.debug(query_with_param_display)
        # logger.debug(params)

        try:
            # Retrieve the data
            response = session.run(query, params)
            keys = response.keys()
            results = []
            for r in response:
                d = dict(zip(keys, r.values()))
                results.append(d)
        except Exception as e:
            logger.error(f"Cypher query failed with exception {e}. Query was: '{query_with_param_display}'")
            raise

        self.queries.append(query_with_param_display)

        if not self.active_transaction:
            session.close()

        return results


connection = Database()
