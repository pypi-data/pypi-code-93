"""
Module for downloading data from s3 to vertica
"""

import logging
import sys
import json
import pandas as pd

from converter.fields_converter_oneway import FieldsConverterOneWay


def get_date_str(path):
    """get suffix to temporary table using path"""
    return (
        path.split("/")[-2]
        .replace(" ", "")
        .replace("-", "")
        .replace(":", "")
        .replace("+", "")
        .replace(".", "")
    )


class UploaderDBBase:
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
        log_format = "%(asctime)-15s %(name)s:%(levelname)s: %(message)s"
        logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.INFO)
        logging.basicConfig(format=log_format, stream=sys.stderr, level=logging.ERROR)
        logging.captureWarnings(True)
        self.logger = logging.getLogger(__class__.__name__)

        self.files_in_upload = files_in_upload
        self.sql_credentials = sql_credentials

        self.s3_client = s3_client

        self.api_version = api_version
        self.uploaded_rows = 0
        self.table_name = table_name
        self.json_columns = json_columns or []

        self.entity = entity
        self.columns = None

    def update_data(self, data, table_name, db):
        """
        Date transformation for further update
        :param data:
        :param table_name:
        :param db: type of db
        :return: transformed data
        """
        converter = FieldsConverterOneWay(sql_credentials=None, db=db)
        df_original = pd.DataFrame(data=data).drop_duplicates(subset=["id"])
        df_updated = df_original.where(pd.notnull(df_original), None).dropna(
            how="all", axis=1
        )
        for column in self.json_columns:
            if column in df_updated.columns:
                df_updated[column] = df_updated.apply(
                    lambda x: json.dumps(x[column], ensure_ascii=False)
                    if x[column] is not None
                    else None,
                    axis=1,
                )
        items = converter.update_value_type(
            table_name=table_name,
            items=df_updated.to_dict(orient="records"),
            fields=self.columns,
        )
        return items

    def process_json(self, data, entity):
        """
        :param data:
        :param entity:
        :return:
        """
        if self.api_version == 4:
            from amocrm.api.api_loader_amocrm_v4 import process_json

            return process_json(data, entity)
        elif self.api_version == 2:
            from amocrm.api.api_loader_amocrm_v2 import process_json

            return process_json(data, entity)

    def generate_table_ddl(self, file_path, db, schema):
        """
        Get approximate table ddl
        :param db:
        :param schema:
        :param file_path:
        :return:
        """
        converter = FieldsConverterOneWay(sql_credentials=None, db=db)
        cur_data = self.process_json(
            json.loads(self.s3_client.read_file(file_path)), self.entity
        )

        return converter.create_table_from_dataframe(
            dataframe=pd.DataFrame(data=cur_data),
            table_name=self.table_name,
            to_create=False,
            schema=schema,
        )

    def log_status(self, cty_upload):
        self.logger.info(
            "Loading %d rows to %s is successful,  a cumulative number is %d",
            cty_upload,
            self.table_name,
            self.uploaded_rows,
        )

    def load_s3_to_db(self):
        pass
