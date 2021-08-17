import pandas as pd
from google.cloud import bigquery


# global settings for metadata tables
meta_google_project = "rd-ap-master-data-dev"
meta_dataset = "metadata_import"
meta_file2table = "FILE2INFO"
meta_tables = "INFO4TABLES"
meta_columns = "INFO4COLUMNS"


class SharedMethods:
    def __init__(self):
        self.bq_client = bigquery.Client()
        self.project = None
        self.data_filename = None

    def _get_table(self, zone: str) -> pd.DataFrame:
        sql_query = f'''
                SELECT
                  TABLES.tablename
                FROM
                  `{meta_google_project}.{meta_dataset}.{meta_file2table}` AS FILE2TABLE
                JOIN
                  `{meta_google_project}.{meta_dataset}.{meta_tables}` AS TABLES
                ON
                  FILE2TABLE.FK = TABLES.FK
                WHERE
                  FILE2TABLE.projectname ="{self.project}"
                  AND FILE2TABLE.filename="{self.data_filename}"
                  AND TABLES.zone = "{zone}"
                '''
        query_job = self.bq_client.query(sql_query)

        return query_job.result().to_dataframe().at[0, "tablename"]

    def _get_columns(self) -> pd.DataFrame:
        sql_query = f'''
                        SELECT
                          COLUMNS.*
                        FROM
                          `{meta_google_project}.{meta_dataset}.{meta_file2table}` AS FILE2TABLE
                        JOIN
                          `{meta_google_project}.{meta_dataset}.{meta_columns}` AS COLUMNS
                        ON
                          FILE2TABLE.FK = COLUMNS.FK
                        WHERE
                          FILE2TABLE.projectname ="{self.project}"
                          AND FILE2TABLE.filename="{self.data_filename}"
                        '''
        query_job = self.bq_client.query(sql_query)

        return query_job.result().to_dataframe()
