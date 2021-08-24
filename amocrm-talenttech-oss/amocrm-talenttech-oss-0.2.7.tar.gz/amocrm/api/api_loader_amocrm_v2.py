"""
    CLASS LOADER from API TO S3, v2
    https://www.amocrm.com/developers/content/digital_pipeline/site_visit/
"""

import logging
from abc import ABC

from amocrm.api.base.api_loader_base import AmocrmApiLoaderBase

PAGE_NUMBER_MAX = 1e6


def process_json(data, entity):
    """
    update data after retrieving from s3
    Args:
        data: row data json
    Returns: list
    :param data:
    :param entity:
    """
    if entity in ("leads", "companies", "contacts", "tasks"):
        items = data["_embedded"]["items"]
    elif entity in "funnels":
        items = [item for key, item in data["_embedded"]["items"].items()]
    elif entity in "users":
        items = [item for key, item in data["_embedded"]["users"].items()]
    return items


class AmocrmApiLoader(AmocrmApiLoaderBase, ABC):
    """
    main class
    """

    def __init__(
        self,
        entity,
        s3_client,
        args_api,
        date_modified_from=None,
        batch_api=500,
        is_oauth2=True,
    ):
        """
        :param entity:   amocrm entities contacts/users/accounts e.t.c
        :param s3_client: s3 client from talenttech-oss library
        :param args_api: dict with AMO_USER_LOGIN/AMO_USER_HASH/AMO_AUTH_URL keys required
        :param date_modified_from: date update from where we are loading data
        :param batch_api: size of batch to upload
        """
        AmocrmApiLoaderBase.__init__(
            self,
            entity=entity,
            s3_client=s3_client,
            args_api=args_api,
            date_modified_from=date_modified_from,
            batch_api=batch_api,
            is_oauth2=is_oauth2,
        )

        self.logger = logging.getLogger(__class__.__name__)

    def extract(self):
        """load table from amocrm.api"""
        self.auth()
        self.create_s3_folder()
        self.clear_s3_folder()  # clear old before loading

        url_base = self.args_api["amocrm_api_url"]
        cur_offset = 0
        count_uploaded = self.batch_api

        params = {}
        headers = {}
        while cur_offset < PAGE_NUMBER_MAX and count_uploaded == self.batch_api:
            file_path = self.get_file_name(cur_offset, self.batch_api, 0)
            self.logger.info("Extracting page number %d ", cur_offset)
            if self.date_modified_from is not None:
                self.logger.info(
                    "Uploading data with after %s ", self.date_modified_from
                )
                url = url_base.format(batch_size_api=self.batch_api, offset=cur_offset)
                headers["IF-MODIFIED-SINCE"] = self.date_modified_from.strftime(
                    "%a, %d %b %Y %H:%M:%S UTC"
                )
            else:
                url = url_base
            self.logger.info(url)
            objects = self.oath_client.get_response_objects(url, params, headers)
            try:
                count_uploaded = len(process_json(objects.json(), self.entity))
                self.logger.info(
                    "Saving data to the file %s, count rows %d, total: %d",
                    file_path,
                    count_uploaded,
                    self.rows_to_upload,
                )
                self.s3_client.create_file(file_path, objects.content)
                self.rows_to_upload += count_uploaded
            except Exception as exc:
                self.logger.info("Can't load objects.content, exception: %s ", exc)
                self.logger.info("Objects.content: %s ", objects.content)
                return
            cur_offset += self.batch_api
        self.logger.info(
            "Total number of rows received from API is %d", self.rows_to_upload
        )
