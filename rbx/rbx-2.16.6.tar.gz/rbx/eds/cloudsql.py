from copy import deepcopy as copy
import logging
import re

from sqlalchemy import text, MetaData, Table

from .query import CloudSQLUpdateQuery, InsertQuery

logger = logging.getLogger(__name__)


def _format_for_mysql(item):
    """Format payload data in a MySQL-friendly format.

    This involves:

      - Stripping any UTC ZONED ISO Format field from its timezone value (Z|+00:00).
        (The field is expected to be in ISO 8601 format.)

      - Decoding all previously-encoded bytes back to unicode.

    """

    # Regex to determine if a value is an ISO Format timestamp with zone.
    # Supports both +00:00 and Z. e.g.
    # 2019-04-04T15:13:53.801759+00:00
    # 2019-04-04T15:13:53.801759Z
    iso_format_regex = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+(?:Z|\+00:00)')

    for key, value in item.items():
        if key.endswith('_name') and type(value) is bytes:
            item[key] = value.decode('utf-8')

        if value is not None and iso_format_regex.match(str(value)) is not None:
            # Handle the Z case.
            if value.endswith('Z'):
                item[key] = value[:-1]
                continue

            # Handle the +00:00 case.
            item[key] = value.split('+')[0]

    return item


class CloudSQL:
    def __init__(self, db):
        self.db = db
        self.metadata = MetaData()

    def create_table(self, table, recreate=False):
        """Create the table in CloudSQL.

        By default, will not attempt to recreate the table already present.
        Unless recreate is set to True.
        """
        assert type(table) is Table

        logger.info('{} "{}" table (CloudSQL) ...'.format(
            {True: 'Re-creating', False: 'Creating'}[recreate],
            table.name))

        self.metadata.create_all(self.db.engine, tables=[table])
        if recreate:
            self.db.execute(text('TRUNCATE TABLE {}'.format(table.name)))

    def insert(self, table_name, key_field, schema):
        """Run an INSERT query."""
        query = InsertQuery(table_name=table_name, key_field=key_field, schema=schema)
        logger.info('Inserting into "{}" table (CloudSQL) ...'.format(table_name))

        self.db.execute(text(query.sql))

    def load(self, table, payload):
        """Load a payload to CloudSQL.

        MySQL doesn't support custom timezones in the TIMESTAMP type, so we
        must manually remove all of the timezones from the 'timestamp' field.
        """
        assert type(table) is Table

        logger.info('Loading {} records to "{}" table (CloudSQL) ...'.format(
            len(payload), table.name))

        statement = table.insert()
        data = copy(payload)
        data[:] = list(map(_format_for_mysql, data))

        self.db.execute(statement, data)

    def update(self, table_name, key_field, schema):
        """Run an UPDATE query."""
        query = CloudSQLUpdateQuery(table_name=table_name, key_field=key_field, schema=schema)
        logger.debug('Updating "{}" table (CloudSQL) ...'.format(query.table))

        self.db.execute(text(query.sql))
