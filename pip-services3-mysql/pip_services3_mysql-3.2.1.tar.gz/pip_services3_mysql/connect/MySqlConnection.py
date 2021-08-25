# -*- coding: utf-8 -*-

import urllib.parse as urlparse
from typing import Any, Union, Optional

import mysql.connector
from mysql.connector import pooling
from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.errors import ConnectionException
from pip_services3_commons.refer import IReferenceable, IReferences
from pip_services3_commons.run import IOpenable
from pip_services3_components.log import CompositeLogger

from pip_services3_mysql.connect.MySqlConnectionResolver import MySqlConnectionResolver


class MySqlConnection(IReferenceable, IConfigurable, IOpenable):
    """
    MySQL connection using plain driver.

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
            - username:                  user name
            - password:                  user password
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
        self.__default_config = ConfigParams.from_tuples(
            "options.connect_timeout", 0,
            "options.idle_timeout", 10000,
            "options.max_pool_size", 3
        )

        # The logger.
        self._logger: CompositeLogger = CompositeLogger()
        # The connection resolver.
        self._connection_resolver: MySqlConnectionResolver = MySqlConnectionResolver()
        # The configuration options.
        self._options: ConfigParams = ConfigParams()
        # The MySQL connection pool object.
        self._connection: Any = None
        # The MySQL database name.
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

    def __compose_uri_settings(self, uri: str, return_uri=False) -> Union[dict, str]:
        max_pool_size = self._options.get_as_nullable_integer('max_pool_size')
        connection_timeout_ms = self._options.get_as_nullable_integer('connect_timeout')

        settings = {
            'pool_size': max_pool_size,
            'connection_timeout': int(connection_timeout_ms / 1000) if connection_timeout_ms > 0 else 0,
        }
        if not return_uri:
            parsed_url = urlparse.urlparse(uri)
            settings.update({'database': parsed_url.path[1:],
                             'user': parsed_url.username,
                             'password': parsed_url.password,
                             'host': parsed_url.hostname,
                             'port': parsed_url.port,
                             })
            return settings

        params = ''
        for key in settings:
            if len(params) > 0:
                params += '&'

            params += key

            value = settings.get(key)
            if value is not None:
                params += '=' + str(value)

        if uri.find('?') < 0:
            uri += '?' + params
        else:
            uri += '&' + params

        return uri

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """

        uri = self._connection_resolver.resolve(correlation_id)
        self._logger.debug(correlation_id, "Connecting to MySQL...")

        try:
            config = self.__compose_uri_settings(uri)
            pool = mysql.connector.pooling.MySQLConnectionPool(pool_size=config.pop('pool_size'),
                                                               **config)
            # Try to connect
            connection_obj = pool.get_connection()

            # set timeout
            idle_timeout_ms = self._options.get_as_nullable_integer('idle_timeout')
            if idle_timeout_ms:
                cursor = connection_obj.cursor()
                cursor.execute(f"SET SESSION MAX_EXECUTION_TIME={idle_timeout_ms}")
                connection_obj.commit()
                cursor.close()

            self._connection = pool
            self._database_name = pool.pool_name.split('_')[-1]

            connection_obj.close()

        except Exception as err:
            raise ConnectionException(correlation_id, "CONNECT_FAILED", "Connection to MySQL failed").with_cause(
                err)

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :return: raise error or None no errors occured.
        """
        if self._connection is None:
            return
        try:
            self._connection._remove_connections()
            self._connection = None
            self._logger.debug(correlation_id, "Disconnected from mysql database %s", self._database_name)
        except Exception as err:
            ConnectionException(correlation_id, 'DISCONNECT_FAILED', 'Disconnect from mysql failed: ').with_cause(err)

        self._connection = None
        self._database_name = None

    def get_connection(self) -> Any:
        return self._connection

    def get_database_name(self) -> str:
        return self._database_name
