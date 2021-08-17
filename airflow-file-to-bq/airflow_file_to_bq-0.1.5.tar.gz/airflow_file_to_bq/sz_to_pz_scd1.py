from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

from airflow_file_to_bq.sharedmethods import SharedMethods


class SZToPZOperatorSCD1(BigQueryInsertJobOperator, SharedMethods):
    def __init__(self, project: str, google_project: str, data_filename: str, table_target: str = None, table_source: str = None, task_id='SZ_to_PZ', sql_configuration: dict = None, *args, **kwargs) -> None:
        SharedMethods.__init__(self)

        self.project = project
        self.google_project = google_project
        self.data_filename = data_filename

        if not sql_configuration:
            sql_configuration = dict()

        # Get table name
        if not table_target:
            self.table_target = self._get_table(zone="PZ")
        if not table_source:
            self.table_source = self._get_table(zone="SZ")

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

        sql = (f"MERGE INTO `{self.google_project}.{self.project}.{self.table_target}` AS DST "
               f"USING `{self.google_project}.{self.project}.{self.table_source}` AS SRC ON (SRC.PK = DST.PK) "
               f"WHEN NOT MATCHED THEN "
               f"INSERT (PK,{','.join(columns['name'].to_list())})"
               f"VALUES (SRC.PK,{','.join(['SRC.'+item for item in columns['name'].to_list()])})"
               f"WHEN MATCHED THEN UPDATE SET "
               f"{','.join(['DST.'+item+'=SRC.'+item for item in columns['name'].to_list()])}")

        return sql
