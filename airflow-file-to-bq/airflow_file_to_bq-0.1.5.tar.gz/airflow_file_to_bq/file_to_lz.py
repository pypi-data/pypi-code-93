from typing import List, Dict

from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from smart_open import open

from airflow_file_to_bq.sharedmethods import SharedMethods

# global settings for metadata tables
meta_google_project = "rd-ap-master-data-dev"
meta_dataset = "metadata_import"
meta_file2table = "FILE2INFO"
meta_tables = "INFO4TABLES"
meta_columns = "INFO4COLUMNS"


class FileToLZOperator(GCSToBigQueryOperator, SharedMethods):
    def __init__(self, project: str, google_project: str, data_bucket: str, data_filename: str, data_filename_prefix: str, table: str = None, task_id='File_to_LZ', *args, **kwargs) -> None:
        SharedMethods.__init__(self)

        self.project = project
        self.google_project = google_project

        self.data_bucket = data_bucket
        self.data_filename_prefix = data_filename_prefix
        self.data_filename = data_filename

        # Get table name
        if not table:
            self.table = self._get_table(zone="LZ")

        # Write schema
        schema = self._extract_schema(separator=kwargs['field_delimiter'])

        # Call of the actual GCSToBigQueryOperator
        GCSToBigQueryOperator.__init__(self,
                                       task_id=task_id,
                                       bucket=self.data_bucket,
                                       source_objects=[f"{self.data_filename_prefix}/{self.data_filename}"],
                                       destination_project_dataset_table=f"{self.google_project}:{self.project}.{self.table}",
                                       schema_fields=schema,
                                       *args, **kwargs)

    def _extract_schema(self, separator) -> List[Dict[str, str]]:
        """
        writes a schema list of dicts which can then be ingested in the GoogleCloudStorageToBigQueryOperator

        :param separator: parameter dict
        :return: extracted schema
        """
        # stream header from column names
        print('Extract header from:', f'gs://{self.data_bucket}/{self.data_filename_prefix}/{self.data_filename}')
        header = next(open(f'gs://{self.data_bucket}/{self.data_filename_prefix}/{self.data_filename}'))

        columns = self._get_columns()

        schema = []
        for headeritem in header.strip().split(separator):
            # get fitting column from result
            row = columns[columns['nameinfile'] == headeritem.strip()].iloc[0]
            schema.append({'name': row['name'], 'type': 'STRING', 'mode': 'NULLABLE'})

        return schema
