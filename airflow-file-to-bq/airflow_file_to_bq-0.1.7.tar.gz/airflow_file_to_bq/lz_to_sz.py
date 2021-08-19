from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

from airflow_file_to_bq.sharedmethods import SharedMethods


class LZToSZOperator(BigQueryInsertJobOperator, SharedMethods):
    def __init__(self, project: str, google_project: str, data_filename: str, table_target: str = None, table_source: str = None, task_id='LZ_to_SZ', sql_configuration: dict = None, *args, **kwargs) -> None:
        SharedMethods.__init__(self)

        self.project = project
        self.google_project = google_project
        self.data_filename = data_filename

        if not sql_configuration:
            sql_configuration = dict()

        # Get table name
        if not table_target:
            self.table_target = self._get_table(zone="SZ")
        if not table_source:
            self.table_source = self._get_table(zone="LZ")

        # Write schema
        sql_statement = self._extract_sql()

        # Call of the actual GCSToBigQueryOperator
        BigQueryInsertJobOperator.__init__(self,
                                           task_id=task_id,
                                           configuration={"query": {"query": sql_statement,
                                                                    'useLegacySql': False,
                                                                    **sql_configuration
                                                                    }
                                                          },
                                           *args, **kwargs)

    def _extract_sql(self) -> str:
        """
        writes a schema list of dicts which can then be ingested in the GoogleCloudStorageToBigQueryOperator

        :return: extracted sql which transform LZ to SZ
        """
        # get config dat from meta data table
        columns = self._get_columns()

        # ToDo PARSE_DATE ('%Y%m%d',PER_DATE) as PER_DATE,

        sql = f"CREATE OR REPLACE TABLE `{self.google_project}.{self.project}.{self.table_target}` AS SELECT * FROM `{self.google_project}.{self.project}.{self.table_target}` LIMIT 0;"
        sql = sql+f"INSERT INTO `{self.google_project}.{self.project}.{self.table_target}` SELECT "
        pk_columns = ','.join([f"{column}" for column in columns[columns['PK']]['name'].to_list()])
        sql = sql+f"FARM_FINGERPRINT(CONCAT({pk_columns})) as PK, "
        for _, column in columns.iterrows():
            if column['datatype'] == 'STRING':
                sql = sql + f"{column['name']}, "
            else:
                sql = sql + f"CAST({column['name']} as {column['datatype']}) as {column['name']}, "

        sql = sql + f"FROM `{self.google_project}.{self.project}.{self.table_source}` WHERE TRUE"

        return sql
