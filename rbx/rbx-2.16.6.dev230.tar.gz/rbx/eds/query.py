from io import BytesIO


class BaseQuery:
    def __init__(self, table_name, key_field, schema, prefix=None, suffix='staging'):
        self._sql = None
        self.fields = [field.name for field in schema]
        self.key_field = key_field
        self.table = '{prefix}{table}'.format(
            prefix='{}.'.format(prefix) if prefix else '',
            table=table_name)
        self.staging = '{prefix}{table}_{suffix}'.format(
            prefix='{}.'.format(prefix) if prefix else '',
            table=table_name,
            suffix=suffix)


class BigQueryUpdateQuery(BaseQuery):
    """Encapsulate the generation of SQL UPDATE queries for BigQuery.

    The query is used to update a dimension's table according to a staging table.
    """
    def __init__(self, *args, **kwargs):
        kwargs['prefix'] = 'dimensions'
        super().__init__(*args, **kwargs)

    @property
    def sql(self):
        """Generate the following SQL:

        UPDATE dimensions.<dimension> AS D
        SET D.<key> = S.<key>, D.<field> = S.<field>, ...
        FROM (
          -- Select all rows from both tables;
          -- All the columns in the rows which exist in "staging" and not in
          -- <dimension> will be NULL.
          SELECT staging.* FROM dimensions.<dimension>_staging AS staging
          LEFT OUTER JOIN dimensions.<dimension> AS dimension
          ON dimension.<key> = staging.<key>
          -- Filter out NULL rows, keeping all existing rows which must be
          -- updated.
          WHERE dimension.<key> IS NOT NULL
        ) S
        WHERE D.<key> = S.<key>;

        """
        if self._sql is None:
            field_set = ', '.join([
                'D.{field} = S.{field}'.format(field=field)
                for field in self.fields
            ])
            self._sql = (
                'UPDATE {table} AS D '
                'SET {field_set} '
                'FROM ( '
                'SELECT staging.* FROM {staging} AS staging '
                'LEFT OUTER JOIN {table} AS dimension '
                'ON dimension.{key} = staging.{key} '
                'WHERE dimension.{key} IS NOT NULL '
                ') S WHERE D.{key} = S.{key}'
            ).format(
                table=self.table,
                field_set=field_set,
                staging=self.staging,
                key=self.key_field
            )

        return self._sql


class InsertQuery(BaseQuery):
    """Encapsulate the generation of SQL INSERT queries for BigQuery and CloudSQL.

    The query is used to insert new rows from a staging table to a dimension's table.
    """
    @property
    def sql(self):
        """Generate the following SQL:

        INSERT INTO <dimension> (
          <key>, <field>, ...
        )
        -- Select all rows from both tables;
        -- All the columns in the rows which exist in "staging" and not in
        -- "dimension" will be NULL.
        SELECT staging.* FROM <dimension>_staging AS staging
        LEFT OUTER JOIN <dimension> AS dimension
        ON dimension.<key> = staging.<key>
        -- Filter only NULL rows, which are the new rows.
        WHERE dimension.<key> IS NULL;

        """
        if self._sql is None:
            field_set = ', '.join(self.fields)
            self._sql = (
                'INSERT INTO {table} ( {field_set} ) '
                'SELECT staging.* FROM {staging} AS staging '
                'LEFT OUTER JOIN {table} AS dimension '
                'ON dimension.{key} = staging.{key} '
                'WHERE dimension.{key} IS NULL'
            ).format(
                table=self.table,
                field_set=field_set,
                staging=self.staging,
                key=self.key_field
            )

        return self._sql


class CloudSQLUpdateQuery(BaseQuery):
    """Encapsulate the generation of SQL UPDATE queries for CloudSQL.

    The query is used to update a dimension's table according to a staging table.
    """
    @property
    def sql(self):
        """Generate the following SQL:

        UPDATE <dimension> as D, <dimension>_staging as S
        SET D.<key> = S.<key>, D.<field> = S.<field>, ...
        WHERE D.<key> = S.<key>;

        """
        if self._sql is None:
            field_set = ', '.join([
                'D.{field} = S.{field}'.format(field=field)
                for field in self.fields
            ])
            self._sql = (
                'UPDATE {table} AS D, {staging} AS S '
                'SET {field_set} '
                'WHERE D.{key} = S.{key}'
            ).format(
                table=self.table,
                field_set=field_set,
                staging=self.staging,
                key=self.key_field
            )

        return self._sql


class LoadQuery:
    """Encapsulate the generation of payload data for BigQuery loads.
    The payload is formatted using the CSV export format.
    """
    source_format = 'CSV'

    def __init__(self, payload, schema):
        self.fields = [field.name for field in schema]
        self.stream = BytesIO()
        if type(payload) is list:
            for item in payload:
                self._write(item)
        else:
            self._write(payload)

    @property
    def data(self):
        """Reset and return the stream object."""
        self.stream.seek(0)
        return self.stream

    def _write(self, line):
        """Write a CSV line using the same order as the schema fields.

        Some of the field values may be UTF-8 encoded already, and some not.
        We also need to keep the file content UTF-8 encoded in order for
        Big Query to load data correctly.
        We therefore need to decode UTF-8 encoded bytes, convert integers and
        booleans to unicodes, and encode the final CSV output.

        Also note that as we use the default double-quotes to enclose fields,
        a double-quote appearing inside a field must be escaped by preceding
        it with another double quote.
        """
        values = []
        for field in self.fields:
            value = line[field]
            if value is None:
                value = ''
            elif isinstance(value, (float, int, bool)):
                value = str(value).lower()
            elif isinstance(value, bytes):
                value = '"{}"'.format(value.decode('utf-8').replace('"', '""'))
            else:
                try:
                    value = '"{}"'.format(value.replace('"', '""'))
                except TypeError:
                    value = f'"{value}"'
            values.append(value)

        values = ','.join(values).encode('utf-8')
        self.stream.write(values)
        self.stream.write(b'\n')
