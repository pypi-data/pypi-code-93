import logging
import sys

from amocrm.api.auth.oauth_client import AmoOAuthClient


class AmocrmApiLoaderBase:
    """
    The base class for API loader
    """

    def __init__(
            self,
            entity,
            s3_client,
            args_api,
            date_modified_from=None,
            batch_api=250,
            is_oauth2=True,
    ):
        """
        :param entity:   amocrm entities contacts/users/accounts e.t.c
        :param s3_client: s3 client from talenttech-oss library
        :param args_api: dict with AMO_USER_LOGIN/AMO_USER_HASH/AMO_AUTH_URL
        :param date_modified_from:
        :param  batch_api: size of batch to upload
        :param: is_oauth2 if new system authorization
        """
        log_format = "%(asctime)-15s %(name)s:%(levelname)s: %(message)s"
        logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.INFO)
        logging.basicConfig(format=log_format, stream=sys.stderr, level=logging.ERROR)
        logging.captureWarnings(True)
        self.logger = logging.getLogger(__class__.__name__)

        self.entity = entity

        self.args_api = args_api
        self.batch_api = batch_api
        self.date_modified_from = date_modified_from

        self.s3_client = s3_client

        self.rows_to_upload = 0

        self.is_auth2 = is_oauth2
        self.oath_client = None

    def auth(self, code_auth=None):
        """API authorization auth2"""
        self.oath_client = AmoOAuthClient(self.args_api, self.s3_client, self.logger, self.is_auth2)
        self.oath_client.auth(code_auth)

    def create_s3_folder(self):
        if not self.s3_client.path_exists(self.s3_client.root_dir):
            self.s3_client.create_dir(self.s3_client.root_dir)

    def clear_s3_folder(self):
        """Clear all data from s3 folder"""
        if self.s3_client.path_exists(self.s3_client.root_dir):
            for file in self.s3_client.get_file_list(self.s3_client.root_dir):
                self.logger.info("Delete %s from s3", file)
                self.s3_client.delete_file(path=file)
            self.s3_client.delete_dir(self.s3_client.root_dir)  # remove directory

    def get_file_name(self, offset, batch, add_arg=None):
        """
        Returns: s3 file name
        """
        return "{dir_path}/{entity}_{offset}_{batch}_{add_arg}.json".format(
            dir_path=self.s3_client.root_dir,
            entity=self.entity,
            offset=offset,
            batch=batch,
            add_arg=add_arg
        )

    def extract(self):
        """load table from amocrm.api"""
        pass
