"""
Module for downloading data from s3 to vertica
"""

import logging
import json

from vconnector.vertica_connector import VerticaConnector
from amocrm.db.base.uploader import UploaderDBBase, get_date_str
from abc import ABC


class UploaderDB(UploaderDBBase, ABC):
    """
    Class to put the data from s3 into vertica
    """

    def __init__(
        self,
        s3_client,
        sql_credentials,
        entity,
        table_name,
        files_in_upload=5,
        json_columns=None,
        api_version=4,
    ):
        """
        :param s3_client: s3 client from talenttech-oss library
        :param sql_credentials: vertica variable dict
        :param entity:
        :param table_name:
        :param files_in_upload: a number of files in upload
        :param json_columns: list of columns need to beatify as json
        """
        UploaderDBBase.__init__(
            self,
            entity=entity,
            s3_client=s3_client,
            sql_credentials=sql_credentials,
            table_name=table_name,
            json_columns=json_columns,
            files_in_upload=files_in_upload,
            api_version=api_version,
        )

        self.logger = logging.getLogger(__class__.__name__)
        self.db = "vertica"

    def load_s3_to_db(self):
        """the main method for running class"""
        with VerticaConnector(
            user=self.sql_credentials["user"],
            password=self.sql_credentials["password"],
            database=self.sql_credentials["database"],
            vertica_configs=self.sql_credentials["vertica_configs"],
            sec_to_recconect=2,
            count_retries=1,
        ) as v_connector:
            data = []
            cur_file = 1
            paths = self.s3_client.get_file_list(self.s3_client.root_dir)
            total_files = len(paths)
            try:
                self.columns = v_connector.get_columns(
                    table_name=self.table_name, schema=self.sql_credentials["schema"]
                )
            except ModuleNotFoundError as exc:
                self.logger.warning(exc)
                self.logger.error(
                    "You should create table %s.%s",
                    self.sql_credentials["schema"],
                    self.table_name,
                )
                if total_files > 0:
                    self.logger.info(
                        "You can try to create table like that %s",
                        self.generate_table_ddl(
                            paths[0], self.db, self.sql_credentials["schema"]
                        ),
                    )
                raise ModuleNotFoundError("Table not found exception") from exc

            for file_path in paths:
                self.logger.info("Loading data from the file %s", file_path)

                cur_data = self.process_json(
                    json.loads(self.s3_client.read_file(file_path)), self.entity
                )
                data += cur_data
                if cur_file % self.files_in_upload == 0 or cur_file == total_files:
                    data = self.update_data(
                        data=data, table_name=self.table_name, db=self.db
                    )
                    v_connector.insert_merge_vertica(
                        table_name=self.table_name,
                        schema=self.sql_credentials["schema"],
                        staging_schema=self.sql_credentials["staging_schema"],
                        data=data,
                        staging_table_suffix=get_date_str(file_path),
                    )
                    self.uploaded_rows += len(data)
                    self.log_status(cty_upload=len(data))
                    data = []
                cur_file += 1
