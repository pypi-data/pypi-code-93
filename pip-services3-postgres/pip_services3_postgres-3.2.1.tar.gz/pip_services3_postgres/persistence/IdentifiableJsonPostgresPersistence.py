# -*- coding: utf-8 -*-
import json
from typing import Any, List, Optional, TypeVar

from pip_services3_commons.data import AnyValueMap

from pip_services3_postgres.persistence.IdentifiablePostgresPersistence import IdentifiablePostgresPersistence

T = TypeVar('T')  # Declare type variable


class IdentifiableJsonPostgresPersistence(IdentifiablePostgresPersistence):
    """
    Abstract persistence component that stores data in PostgreSQL in JSON or JSONB fields
    and implements a number of CRUD operations over data items with unique ids.
    The data items must implement :class:`IIdentifiable <pip_services3_commons.data.IIdentifiable.IIdentifiable>` interface.

    The JSON table has only two fields: id and data.

    In basic scenarios child classes shall only override :func:`get_page_by_filter <pip_services3_postgres.persistence.IdentifiableJsonPostgresPersistence.get_page_by_filter>`,
    :func:`get_list_by_filter <pip_services3_postgres.persistence.IdentifiableJsonPostgresPersistence.get_list_by_filter>` or :func:`delete_by_filter <pip_services3_postgres.persistence.IdentifiableJsonPostgresPersistence.delete_by_filter>`
    operations with specific filter function.
    All other operations can be used out of the box.

    In complex scenarios child classes can implement additional operations by
    accessing **self._collection** and **self._model** properties.

    ### Configuration parameters ###
        - table:                      (optional) PostgreSQL table name
        - schema:                     (optional) PostgreSQL schema name
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

    Example:

    .. code-block:: python

        class MyPostgresPersistence(IdentifiablePostgresJsonPersistence):

            def __init__(self):
                super(MyPostgresPersistence, self).__init__('mydata', MyDataPostgresSchema())

            def __compose_filter(self, filter):
                filter = filter or FilterParams()
                criteria = []

                name = filter.get_as_nullable_string('name')
                if name is not None:
                    criteria.append({'name':name})

                return { '$and': criteria } if len(criteria) > 0 else None

            def get_page_by_filter(self, correlation_id, filter, paging):
                return super().get_page_by_filter(correlation_id, self.__compose_filter(filter), paging, None, None)

        persistence = MyPostgresPersistence()
        persistence.configure(ConfigParams.from_tuples(
            "host", "localhost",
            "port", 27017
        ))

        persistence.open("123")

        persistence.create("123", {'id': "1", 'name': "ABC"})
        page = persistence.get_page_by_filter('123', FilterParams.from_tuples('name', 'ABC'), None)
        print(page.data)  # Result: { id: "1", name: "ABC" }

        persistence.delete_by_id("123", "1")
        # ...
    """

    def __init__(self, table_name: str = None, schema_name: str = None):
        """
        Creates a new instance of the persistence component.

        :param table_name: (optional) a table name.
        :param schema_name: (optional) a schema name.
        """
        super(IdentifiableJsonPostgresPersistence, self).__init__(table_name, schema_name)

    def _ensure_table(self, id_type: str = 'TEXT', data_type: str = 'JSONB'):
        """
        Adds DML statement to automatically create JSON(B) table

        :param id_type: type of the id column (default: TEXT)
        :param data_type: type of the data column (default: JSONB)
        """
        if self._schema_name is not None:
            query = "CREATE SCHEMA IF NOT EXISTS " + self._quote_identifier(self._schema_name)
            self._ensure_schema(query)

        query = "CREATE TABLE IF NOT EXISTS " + self._quote_identifier(self._table_name) \
                + " (\"id\" " + id_type + " PRIMARY KEY, \"data\" " + data_type + ")"
        self._ensure_schema(query)

    def _convert_to_public(self, value: Any) -> Any:
        """
        Converts object value from internal to public format.

        :param value: an object in internal format to convert.
        :return: converted object in public format.
        """
        if value is None:
            return None
        try:
            return super()._convert_to_public(value['data'])
        except KeyError:
            return super()._convert_to_public(value)

    def _convert_from_public(self, value: Any) -> Any:
        """
        Convert object value from public to internal format.

        :param value: an object in public format to convert.
        :return: converted object in internal format.
        """
        if value is None:
            return None

        value = super()._convert_from_public(value)

        result = {
            'id': value['id'],
            'data': json.dumps(value)
        }
        return result

    def _generate_values(self, values: dict) -> List[str]:
        """
        Generates a list of column parameters

        :param values: a key-value map with columns and values
        :return: a generated list of column values
        """
        result = []
        for val in values.values():
            if not isinstance(val, str):
                result.append(json.dumps(val))
            else:
                result.append(val)
        return result

    def update_partially(self, correlation_id: Optional[str], id: Any, data: AnyValueMap) -> Optional[T]:
        """
        Updates only few selected fields in a data item.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param id: an id of data item to be updated.
        :param data: a map with fields to be updated.
        :return: updated item
        """
        if data is None or id is None:
            return

        query = "UPDATE " + self._quoted_table_name() + " SET \"data\"=\"data\"||%s WHERE \"id\"=%s RETURNING *"

        values = [json.dumps(data.get_as_object()), id]

        result = self._request(query, values)

        self._logger.trace(correlation_id, "Updated partially in %s with id = %s", self._table_name, id)

        new_item = self._convert_to_public(result['items'][0]) if result['items'] and len(
            result['items']) == 1 else None

        return new_item
