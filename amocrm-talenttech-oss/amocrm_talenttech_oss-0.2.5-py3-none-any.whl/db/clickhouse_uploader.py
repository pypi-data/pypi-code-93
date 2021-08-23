"""
Module for downloading data from s3 to clickhouse
"""
import logging
import json
from abc import ABC

from clickhouse_balanced import Client
from amocrm.db.base.uploader import UploaderDBBase


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
        table_to_optimize=None,
        files_in_upload=5,
        full_copy=False,
        json_columns=None,
        api_version=4,
    ):
        """
        Constructor
        :param s3_client: s3 client from talenttech-oss library
        :param sql_credentials clickhouse variable dict
        :param entity:
        :param table_name:
        :param table_to_optimize: in a few cases
        :param files_in_upload: a number of files in upload
        :param full_copy: if True will make truncate and insert
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

        self.table_to_optimize = table_to_optimize
        self.full_copy = full_copy
        self.db = "ch"

    def __get_columns(self, table_name, ch_client):
        column_stat = """select name, type
            from  system.columns
            where table = '{table}'
                  and database = '{database}'
                  """.format(
            table=table_name, database=self.sql_credentials["database"]
        )
        rows = ch_client.execute(column_stat)
        res = dict(zip([row[0] for row in rows], [row[1] for row in rows]))
        return res

    def __delete_from_db(
        self, table_name, ch_client, to_delete_values=None, delete_column="id"
    ):
        """
        To delete already existed items from table
        Args:
            table_name:
            to_delete_values:  ids of deleted values
            delete_column: fields of ids

        Returns: Nothing
        """
        logging.info(
            "Deleting custom fields from %s, for %d leads",
            table_name,
            len(to_delete_values),
        )
        to_delete_values = to_delete_values or []
        columns = self.__get_columns(table_name, ch_client)
        columns_str = ",".join(columns)
        columns_changed_str = ",".join(
            ["-1" if c == "sign" else str(c) for c in columns]
        )

        if "sign" not in columns:
            logging.info("No sign for deleting in columns")
            return

        index = 0
        len_update = 1000
        row_deleted_count = len(to_delete_values)
        while index < len(to_delete_values):
            cur_deleted_values = ",".join(
                [str(r) for r in to_delete_values[index : index + len_update]]
            )
            select_st = (
                f"select {columns_changed_str} from {table_name} where sign = 1 "
                f"and {delete_column} in ({cur_deleted_values}) "
            )
            insert_st = f"insert into {table_name} ({columns_str}) {select_st} "
            ch_client.execute(insert_st)
            index += len_update

        logging.info(
            "Deleting custom fields from %s success, %d deleted leads",
            table_name,
            row_deleted_count,
        )

    def upload_data_to_db(self, data, ch_client, table_name=None):
        """
        Row uploading data to table
        Args:
            data:
            table_name:
        Returns: Nothing
        :param data:
        :param table_name:
        :param ch_client:
        """
        table_name = table_name or self.table_name
        columns = ",".join([c for c in self.columns if c in data[0].keys()])
        logging.info("Insert values to %s, a number is %d", table_name, len(data))
        logging.info("INSERT INTO %s (%s) VALUES", table_name, columns)
        ch_client.execute(
            f"INSERT INTO {table_name} ({columns}) VALUES", data, types_check=True
        )

    def __optimize_table_ch(self, table, ch_client, add=""):
        """optimize table, set only for clickhouse"""
        sql_cf_optimize = "Optimize table {database}.{table}  {add} ".format(
            database=self.sql_credentials["database"],
            table=table,
            add=add,
            cluster="{cluster}",
        )
        logging.info(sql_cf_optimize)
        ch_client.execute(sql_cf_optimize)

    def load_s3_to_db(self):
        """the main method for running class"""
        ch_client = Client(**self.sql_credentials)
        cur_file = 1
        data = []
        paths = self.s3_client.get_file_list(self.s3_client.root_dir)
        total_files = len(paths)
        self.columns = self.__get_columns(self.table_name, ch_client)
        if len(self.columns) == 0:
            self.logger.error(
                "You should create the table %s.%s",
                self.sql_credentials["database"],
                self.table_name,
            )
            if total_files > 0:
                self.logger.info(
                    "You can try to create the table like that %s",
                    self.generate_table_ddl(
                        paths[0], self.db, self.sql_credentials["database"]
                    ),
                )
            raise ModuleNotFoundError("Table not found exception")

        if self.full_copy:
            sql_truncate = f"truncate table {self.table_name}"
            logging.info(sql_truncate)
            ch_client.execute(sql_truncate)

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
                self.upload_data_to_db(data=data, ch_client=ch_client)
                self.uploaded_rows += len(data)
                self.log_status(cty_upload=len(data))
                data = []
            cur_file += 1

        if self.table_to_optimize is not None:
            self.__optimize_table_ch(table=self.table_to_optimize, ch_client=ch_client)
