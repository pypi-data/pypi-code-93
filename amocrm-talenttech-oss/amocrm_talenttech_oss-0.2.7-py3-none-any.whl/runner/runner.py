"""
Class for running all the system using lot's of params
"""
import json
import datetime
from amocrm.config_reader.read_config import get_config_list
from s3.client import Client as S3Client


def check_keys_compatibility(dict_to_update, dict_additional):
    """
    Check for keys need to run
    :param dict_to_update:
    :param dict_additional:
    :return: True if values in dicts are compatible
    """
    keys_exists = [key for key in dict_to_update if key in dict_additional]
    for key in keys_exists:
        if dict_to_update[key] != dict_additional[key]:
            return False
    return True


def run_from_config(
        file_dir,
        **args_additional
):
    """

    :param file_dir: file.json to run
    :param args_additional: additional arguments to AmocrmRunner
    :return:
    """
    config_list = get_config_list(file_dir)
    for config_entity in config_list:
        extract_params, db_params_list = config_entity
        if check_keys_compatibility(extract_params, args_additional):
            extract_params.update(args_additional)
        else:
            continue
        AmocrmRunner(**extract_params).run()
        for db_params in db_params_list:
            if check_keys_compatibility(db_params, args_additional):
                db_params.update(args_additional)
            AmocrmRunner(**db_params).run()
            if "parser" in db_params:
                parse_params = db_params.copy()
                parse_params["action"] = "parse"
                if check_keys_compatibility(parse_params, args_additional):
                    parse_params.update(args_additional)
                else:
                    continue
                AmocrmRunner(**parse_params).run()

        AmocrmRunner(**extract_params).clean_s3()


class AmocrmRunner:
    """
    Run amocrm library retrieving parameters
    """

    def __init__(
            self,
            action,
            etl_name_no_version,
            execution_date,
            config_name,
            entity,
            args_s3,
            sql_credentials,
            hours_to_modify=1,
            db=None,
            table_name=None,
            table_to_optimize=None,
            json_columns=None,
            amocrm_secrets=None,
            amocrm_api_url=None,
            if_modified_since=None,
            parser=None,
            api_version=4,
            batch_api=500,
            is_oauth2=True
    ):

        self.entity = entity
        task_id = f"{config_name}_extract_{self.entity}"

        self.args_s3 = args_s3
        self.s3_client = S3Client(**args_s3)
        self.s3_client.init_root_dir(
            etl_name_no_version=etl_name_no_version,
            task_id=task_id,
            execution_date=execution_date,
        )

        self.sql_credentials = sql_credentials
        self.db = db

        self.action = action

        self.api_version = api_version
        self.batch_api = batch_api
        self.is_oauth2 = is_oauth2
        self.amocrm_secrets = amocrm_secrets
        self.amocrm_api_url = amocrm_api_url

        self.table_name = table_name
        self.table_to_optimize = table_to_optimize

        self.json_columns = (json_columns or "").split(",")

        self.date_modified_from = None
        if bool(int(if_modified_since or 0)):
            self.date_modified_from = execution_date - datetime.timedelta(
                hours=hours_to_modify
            )

        # parser params
        self.tables_to_parse = self.get_tables_to_parse(parser)

    def get_tables_to_parse(self, parser):
        """
        Generate list of tables parse params to parse
        :param parser:
        :return: list of tables
        """
        tables_to_parse = []
        if parser is not None:
            for parse_table in json.loads(parser):
                insert_table = parse_table["insert_table"]
                if "from_table" in parse_table:
                    from_table = parse_table["from_table"]
                else:
                    from_table = self.table_name
                tables_to_parse.append(
                    {
                        "from_table": from_table,
                        "insert_table": insert_table,
                        "script": parse_table["script"],
                    }
                )
        return tables_to_parse

    def run(self):
        """
        chose method to run by action name
        :return:
        """
        if self.action == "extract":
            self.extract()
        elif self.action == "load":
            self.load_to_db(db=self.db)
        elif self.action == "parse":
            for table_parse in self.tables_to_parse:
                self.parse(db=self.db, table_parse=table_parse)
        elif self.action == "clean_s3":
            self.clean_s3()

    def regenerate_file_secret(self, code_auth):
        """
        If file secrete doesn't exist call this mide
        :param code_auth: get it from amocrm UI -> integration API
        :return: Nothing
        """
        from amocrm.api.api_loader_amocrm_v4 import AmocrmApiLoader as ApiLoader
        args_api = {"amocrm_api_url": self.amocrm_api_url}
        args_api.update(self.amocrm_secrets)
        api_loader = ApiLoader(
            self.entity,
            self.s3_client,
            args_api,
            date_modified_from=self.date_modified_from,
            batch_api=self.batch_api
        )
        api_loader.auth(code_auth=code_auth)

    def extract(self):
        """
        1. step to run. Extract from amocrm.api
        :return:
        """
        if self.api_version == 4:
            from amocrm.api.api_loader_amocrm_v4 import AmocrmApiLoader as ApiLoader
        elif self.api_version == 2:
            from amocrm.api.api_loader_amocrm_v2 import AmocrmApiLoader as ApiLoader

        args_api = {"amocrm_api_url": self.amocrm_api_url}
        args_api.update(self.amocrm_secrets)
        api_loader = ApiLoader(
            self.entity,
            self.s3_client,
            args_api,
            date_modified_from=self.date_modified_from,
            batch_api=self.batch_api,
            is_oauth2=self.is_oauth2
        )
        api_loader.extract()

    def load_to_db(self, db):
        """
        2 step. Load data from s3 to amocrm.db
        :param db: vertica or clickhouse
        :return:
        """
        args = {
            "s3_client": self.s3_client,
            "sql_credentials": self.sql_credentials[db],
            "entity": self.entity,
            "table_name": self.table_name,
            "json_columns": self.json_columns,
            "api_version": self.api_version
        }
        if db == "vertica":
            from amocrm.db.vertica_uploader import UploaderDB
        elif db == "ch":
            from amocrm.db.clickhouse_uploader import UploaderDB
            if self.date_modified_from is None:
                args['full_copy'] = True

            args["table_to_optimize"] = self.table_to_optimize

        db_uploader = UploaderDB(**args)
        db_uploader.load_s3_to_db()

    def parse(self, db, table_parse):
        """
        Parse columns in source data and insert data to vertica or clickhouse
        :param db:
        :param table_parse:
        :return: Nothing
        """
        if self.db == "vertica":
            from inserter.vertica_swap_inserter import (
                VerticaSwapInserter as SwapInserter,
            )

            database = self.sql_credentials[db]["schema"]
        elif self.db == "ch":
            from inserter.ch_swap_inserter import CHSwapInserter as SwapInserter

            database = self.sql_credentials[self.db]["database"]

        swap_inserter = SwapInserter(
            script=table_parse["script"],
            sql_credentials=self.sql_credentials[self.db],
            insert_table=table_parse["from_table"] + "_" + table_parse["insert_table"],
            add_args={
                "database": database,
                "from_table": table_parse["from_table"],
            },
        )
        swap_inserter.run()

    def clean_s3(self):
        if self.api_version == 4:
            from amocrm.api.api_loader_amocrm_v4 import AmocrmApiLoader as ApiLoader
        elif self.api_version == 2:
            from amocrm.api.api_loader_amocrm_v2 import AmocrmApiLoader as ApiLoader

        args_api = None
        api_loader = ApiLoader(
            entity=self.entity, s3_client=self.s3_client, args_api=args_api
        )
        api_loader.clear_s3_folder()
