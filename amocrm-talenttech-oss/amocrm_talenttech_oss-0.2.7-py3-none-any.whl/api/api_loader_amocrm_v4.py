"""
    CLASS API LOADER to S3 Directory
    https://www.amocrm.com/developers/content/api_v4/leads-2/
"""

import logging
from abc import ABC

from amocrm.api.base.api_loader_base import AmocrmApiLoaderBase

PAGE_NUMBER_MAX = 1e6


def get_limit_from_url(objects):
    """
    get page limit form response
    :param objects:
    :return:
    """
    import urllib.parse as urlparse

    try:
        url = objects.json()["_links"]["self"]["href"]
        par = urlparse.parse_qs(urlparse.urlparse(url).query)
        return int(par["limit"][0])
    except KeyError:
        return 50


def process_json(data, entity):
    """
    update data after retrieving from s3
    Args:
        data: row data json
    Returns: list
    :param data:
    :param entity:
    """
    return data["_embedded"][entity]


class AmocrmApiLoader(AmocrmApiLoaderBase, ABC):
    """
    The main class
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
        :param args_api: dict with
        :param date_modified_from:
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

        url_bases = self.args_api["amocrm_api_url"].split(";")
        num_url = 0
        for url_base in url_bases:
            cur_page = 1

            params = {}
            if self.date_modified_from is not None:
                self.logger.info("Uploading data with after %s ", self.date_modified_from)
                if url_base.find('only_deleted') == -1:
                    params["filter[updated_at][from]"] = int(
                        self.date_modified_from.timestamp()
                    )
            has_next = True
            while has_next and cur_page < PAGE_NUMBER_MAX:
                self.logger.info("Extracting page №%d", cur_page)

                file_path = self.get_file_name(cur_page, self.batch_api, str(num_url))

                url = url_base.format(limit=self.batch_api, page=cur_page)

                try:
                    objects = self.oath_client.get_response_objects(url, params)
                except:
                    import time
                    time.sleep(3)
                    objects = self.oath_client.get_response_objects(url, params)

                self.logger.info(objects.url)
                if objects.status_code != 200:
                    self.logger.warning(
                        "Warning! API sent no result %d,\n %s", objects.status_code, str(objects.content)
                    )
                    break

                limit_from_url = get_limit_from_url(objects)
                if "next" not in objects.json()["_links"]:
                    has_next = False

                if limit_from_url != self.batch_api:
                    logging.warning(
                        "Batch API: %d is too large, changing to default value %d",
                        self.batch_api,
                        limit_from_url,
                    )
                    self.batch_api = limit_from_url

                count_uploaded = len(process_json(objects.json(), self.entity))
                self.rows_to_upload += count_uploaded
                self.logger.info(
                    "Saving data to the file %s, a number of rows %d, total number: %d",
                    file_path,
                    count_uploaded,
                    self.rows_to_upload,
                )
                self.s3_client.create_file(file_path, objects.content)
                if count_uploaded < self.batch_api:
                    logging.warning(
                        "A number of rows %d in response less then size of batch %d. Make a return",
                        count_uploaded,
                        self.batch_api,
                    )
                    break

                cur_page += 1
            self.logger.info(
                "Total number of rows received from API is %d", self.rows_to_upload
            )
            num_url += 1
