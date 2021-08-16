import json
import logging

from google.cloud.bigquery import Client, LoadJobConfig, QueryJobConfig, Table
from google.cloud.exceptions import BadRequest, NotFound

from ..exceptions import FatalException
from .query import InsertQuery, LoadQuery, BigQueryUpdateQuery

logger = logging.getLogger(__name__)

TIMEOUT_MS = 20000


class BigQuery:

    def __init__(self, project):
        self.project = project

        self._client = None

    @property
    def client(self):
        if not self._client:
            self._client = Client(project=self.project)
        return self._client

    def create_table(self, dataset, table_name, schema, recreate=False):
        """Create the table in BigQuery.

        If the table already exists, do nothing.
        Unless recreate is set to True, in which case we drop the table first.
        """
        table_id = f'{self.project}.{dataset}.{table_name}'

        try:
            table = self.client.get_table(table_id)
        except NotFound:
            logger.info(f'Creating "{table_name}" table (BigQuery) ...')
            table = self.client.create_table(Table(table_id, schema=schema))
        else:
            # Table already exists
            if recreate:
                logger.info(f'Re-creating "{table_name}" table (BigQuery) ...')
                self.client.delete_table(table_id)
                table = self.client.create_table(Table(table_id, schema=schema))

        return table

    def insert(self, table_name, key_field, schema):
        """Run an INSERT query."""
        query = InsertQuery(table_name=table_name, key_field=key_field, schema=schema,
                            prefix='dimensions')
        logger.info(f'Inserting into "{query.table}" table (BigQuery) ...')

        job_config = QueryJobConfig()
        query_job = self.client.query(query.sql, job_config=job_config)
        query_job.result(timeout=TIMEOUT_MS)

    def load(self, dataset, table_name, schema, payload):
        """Load a payload to BigQuery."""
        logger.info(f'Loading {len(payload)} records to "{table_name}" table (BigQuery) ...')
        query = LoadQuery(payload, schema=schema)

        table_id = f'{self.project}.{dataset}.{table_name}'
        table = self.client.get_table(table_id)

        job_config = LoadJobConfig()
        job_config.schema = schema
        job_config.source_format = query.source_format
        job = self.client.load_table_from_file(query.data, table, job_config=job_config)
        try:
            job.result()
        except BadRequest:
            # The error will be set in the job.errors property, so no need to log it
            # again. We do add the requested payload to help troubleshooting.
            job.errors.append({'payload': query.data.read().decode('utf-8')})

        if job.errors:
            raise FatalException(json.dumps(job.errors))

        return table

    def update(self, table_name, key_field, schema):
        """Run an UPDATE query."""
        query = BigQueryUpdateQuery(table_name=table_name, key_field=key_field, schema=schema)
        logger.info(f'Updating "{query.table}" table (BigQuery) ...')

        job_config = QueryJobConfig()
        query_job = self.client.query(query.sql, job_config=job_config)
        query_job.result(timeout=TIMEOUT_MS)

    def update_table(self, dataset, table_name, schema):
        """Update a table schema in BigQuery.

        BigQuery schema updates only support adding columns, or editing them.
        Removing columns is not supported.
        """
        logger.info(f'Updating "{table_name}" table (BigQuery) ...')
        table_id = f'{self.project}.{dataset}.{table_name}'
        table = self.client.get_table(table_id)

        if len(table.schema) <= len(schema):
            table.schema = schema
            self.client.update_table(table, ['schema'])
