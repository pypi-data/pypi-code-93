import os
import ujson as json
from google.cloud import logging as cloud_logging
from google.oauth2 import service_account


class CloudLogger(object):

    __client = None

    __logger = None

    def setup(self, **kwargs):
        """Setup cloud logging credential

        Keyword Args:
            name (str): logger name, format: projects/{project_id}/logs/{name}
            credential_path (str): service account key json file path
            credential_json (str or dict): service account key json string
        """

        if "credential_path" in kwargs:
            self.__setup_with_path(kwargs.get("credential_path"))

        elif "credential_json" in kwargs:
            self.__setup_with_json(kwargs.get("credential_json"))

        else:
            self.__setup_with_path(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

        self.__logger = self.__client.logger(kwargs.get("name", "gcp_cloud_logger"))

    def __setup_with_path(self, credential_path: str):
        if not os.path.isfile(credential_path):
            raise Exception(
                "credential_path or GOOGLE_APPLICATION_CREDENTIALS is not exists"
            )

        self.__client = cloud_logging.Client.from_service_account_json(credential_path)

    def __setup_with_json(self, credential_json):
        if type(credential_json) == str:
            cred = json.loads(credential_json)

        elif type(credential_json) == dict:
            cred = credential_json

        else:
            raise Exception(f"Type {type(credential_json)} is not support")

        credentials = service_account.Credentials.from_service_account_info(cred)
        self.__client = cloud_logging.Client(credentials=credentials)

    def info(self, content):
        self.log_text(content, severity="INFO")

    def warn(self, content):
        self.log_text(content, severity="WARNING")

    def error(self, content):
        self.log_text(content, severity="ERROR")

    def critical(self, content):
        self.log_text(content, severity="CRITICAL")

    def log_text(self, content, **kwargs):
        if self.__logger is None:
            raise Exception("Please setup credential info before use cloud logger")

        if type(content) in (dict, list):
            content = json.dumps(content)

        self.__logger.log_text(content, severity=kwargs.get("severity", "INFO"))
