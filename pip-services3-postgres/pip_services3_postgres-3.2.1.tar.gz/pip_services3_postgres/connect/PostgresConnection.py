# -*- coding: utf-8 -*-
from typing import Any, Optional

from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.errors import ConnectionException
from pip_services3_commons.refer import IReferenceable, IReferences
from pip_services3_commons.run import IOpenable
from pip_services3_components.log import CompositeLogger
from psycopg2 import pool

from pip_services3_postgres.connect.PostgresConnectionResolver import PostgresConnectionResolver


class PostgresConnection(IReferenceable, IConfigurable, IOpenable):
    """
    PostgreSQL connection using plain driver.

    By defining a connection and sharing it through multiple persistence components
    you can reduce number of used database connections.

    ### Configuration parameters ###
        - connection(s):
            - discovery_key:             (optional) a key to retrieve the connection from :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`
            - host:                      host name or IP address
            - port:                      port number (default: 27017)
            - uri:                       resource URI or connection string with all parameters in it
        - credential(s):
            - store_key:                 (optional) a key to retrieve the credentials from :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>`
            - username:                  (optional) user name
            - password:                  (optional) user password
        - options:
            - connect_timeout:      (optional) number of milliseconds to wait before timing out when connecting a new client (default: 0)
            - idle_timeout:         (optional) number of milliseconds a client must sit idle in the pool and not be checked out (default: 10000)
            - max_pool_size:        (optional) maximum number of clients the pool should contain (default: 10)

    ### References ###
        - `*:logger:*:*:1.0`           (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages components to pass log messages
        - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services
        - `*:credential-store:*:*:1.0` (optional) :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>` stores to resolve credentials

    """

    def __init__(self):

        self.__default_config: ConfigParams = ConfigParams.from_tuples(
            # connections. *
            # credential. *

            "options.connect_timeout", 0,
            "options.idle_timeout", 10000,
            "options.max_pool_size", 3
        )

        # The logger.
        self._logger: CompositeLogger = CompositeLogger()

        # The connection resolver.
        self._connection_resolver: PostgresConnectionResolver = PostgresConnectionResolver()

        # The configuration options.
        self._options: ConfigParams = ConfigParams()

        # The PostgreSQL connection pool object.
        self._connection: Any = None

        # The PostgreSQL database name.
        self._database_name: str = None

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        config = config.set_defaults(self.__default_config)

        self._connection_resolver.configure(config)

        self._options = self._options.override(config.get_section('options'))

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._logger.set_references(references)
        self._connection_resolver.set_references(references)

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self._connection is not None

    def __compose_settings(self) -> Any:
        max_pool_size = self._options.get_as_nullable_integer('max_pool_size')
        connection_timeout_ms = self._options.get_as_nullable_integer('connect_timeout')
        idle_timeout_ms = self._options.get_as_nullable_integer('idle_timeout')

        settings = {
            # 'multi': True,
            'maxConnection': max_pool_size,
            'connect_timeout': connection_timeout_ms if connection_timeout_ms > 0 else 1000,
            'idle_timeout_millis': idle_timeout_ms
        }

        return settings

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :return: error or None no errors occured.
        """
        try:
            config = self._connection_resolver.resolve(correlation_id)
            self._logger.debug(correlation_id, "Connecting to postgres")

            try:
                config.update(self.__compose_settings())

                idle_timeout_millis = config.pop('idle_timeout_millis')

                # Try to connect
                self._connection = pool.ThreadedConnectionPool(1, config.pop('maxConnection'), **config)

                # set idle timeout
                if idle_timeout_millis:
                    conn = self._connection.getconn()
                    cursor = conn.cursor()
                    cursor.execute(f"SET SESSION idle_in_transaction_session_timeout = '{idle_timeout_millis}';")
                    conn.commit()
                    cursor.close()
                    self._connection.putconn(conn)

                self._database_name = config['dbname']

            except Exception as err:
                raise ConnectionException(correlation_id, "CONNECT_FAILED", "Connection to postgres failed").with_cause(
                    err)

        except Exception as err:
            self._logger.error(correlation_id, err, 'Failed to resolve Postgres connection')

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """

        if self._connection is None:
            return

        try:
            self._connection.closeall()
            self._logger.debug(correlation_id, "Disconnected from postgres database %s", self._database_name)
            self._connection = None
            self._database_name = None

        except Exception as err:
            ConnectionException(correlation_id, 'DISCONNECT_FAILED', 'Disconnect from postgres failed: ').with_cause(
                err)

    def get_connection(self) -> Any:
        return self._connection

    def get_database_name(self) -> str:
        return self._database_name
