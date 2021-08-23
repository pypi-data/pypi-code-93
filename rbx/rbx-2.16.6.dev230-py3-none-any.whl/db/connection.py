import warnings

from sqlalchemy import create_engine, text


class Database:
    """A SQLAlchemy Engine with useful convenience methods.

    A single connection should be created for a thread, so it can manage its own pool of
    connections more efficiently.
    """

    def __init__(self, db_engine_url, clear=False):
        """Create a connection engine with default connection pooling."""
        self.engine = create_engine(
            db_engine_url,
            max_overflow=2,
            pool_pre_ping=True,
            pool_recycle=1800,  # 30 minutes
            pool_size=5,
            pool_timeout=30
        )

    @property
    def dialect(self):
        return self.engine.dialect

    def connect(self, **kwargs):
        """Proxy to the Engine.connect() method.

        Returns:
            Connection: the connection object.
        """
        return self.engine.connect(**kwargs)

    def execute(self, *args, **kwargs):
        """Convenience method to execute a single statement or expression.

        The call arguments are passed on to the SqlAlchemy execute() method unaltered, all wrapped
        within a single connection transaction block.

        For full UTF-8 support with MySQL, the NAMES collation must be set prior to making the
        request. Failing to do this would not decode non-ascii characters properly.
        """
        with self.engine.connect() as connection:
            if self.dialect.name == 'mysql':
                connection.execute('SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci')
            return connection.execute(*args, **kwargs)

    def has_table(self, table_name):
        return self.engine.dialect.has_table(self.engine, table_name)

    def query(self, statement, connection=None, scalar=False):
        """Run a SQL statement and return the results.

        Parameters:
            statement (str):
                The raw SQL statement to execute.
            connection (Connection):
                When a Connection object is provided, use that and do not attempt to connect.
                This allows multiple statements to be executed using the same connection, or to
                use a transactional connection.
            scalar (bool):
                Fetch the first column of the first row.
        """
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', '.*Division by 0.*', category=Warning)
            if connection:
                cursor = connection.execute(text(statement))
            else:
                with self.engine.connect() as connection:
                    cursor = connection.execute(text(statement))

            return cursor.scalar() if scalar else cursor.fetchall()
