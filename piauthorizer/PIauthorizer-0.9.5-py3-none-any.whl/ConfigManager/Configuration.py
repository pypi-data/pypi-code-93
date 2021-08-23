import logging
import os
import re
from ast import literal_eval
from typing import Dict

import requests

logger = logging.getLogger("Configuration")
logger.setLevel(os.environ.get("LOG_LEVEL"))


class Configuration:
    """A class that dealt with configuration from the STS API for a specific config and tenant"""

    def __init__(
        self,
        json_dict: dict,
        tenant_id: str,
        tenant_name: str,
        config_name: str,
        sts_application_config_url: str,
    ) -> None:
        logger.info(
            f"Creating a {config_name} config object for tenant id: {tenant_id} - {tenant_name}"
        )
        self.config_name = config_name
        self.tenant_name = tenant_name
        self.tenant_id = tenant_id
        self.etag = json_dict["@meta.ETag"]
        self.configuration = json_dict
        self.configuration["configurations"] = self.extract_config(
            self.configuration["configurations"]
        )
        self.sts_application_config_url = sts_application_config_url
        self.configuration["has_changed"] = True

    def get_configuration(self) -> dict:
        """get the most recent configuration for this specifc tenant and application

        Args:
            json_dict (dict): STS ApplicationConfiguration dictionary
        """

        return self.configuration

    def update_configuration(self, json_dict: dict) -> None:
        """Update configuration for this specifc tenant and application based on a STS ApplicationConfiguration dictionary

        Args:
            json_dict (dict): STS ApplicationConfiguration dictionary
        """

        self.etag = json_dict["@meta.ETag"]
        logger.info(
            f"New etag: {self.etag} for tenant {self.tenant_name} and config {self.config_name}"
        )
        self.configuration = json_dict
        self.configuration["configurations"] = self.extract_config(
            self.configuration["configurations"]
        )

    def update_config_if_changed(self, delegated_token: str) -> None:
        """Check if configuration from STS are changed, and if so - update and load them

        Args:
            tenant_id (str): ID of the tenant
            token (str): bearer token of the tenant user

        Returns:
            Tuple[bool, str]: A tuple consisting of a flag (whether the operation was successful) and a message
        """
        result_message = ""

        headers = {
            "Authorization": f"Bearer {delegated_token}",
            "If-None-Match": self.etag,
        }

        response = requests.get(
            self.sts_application_config_url.format(
                name=self.config_name, tenant_id=self.tenant_id
            ),
            headers=headers,
        )

        has_changed = False
        if response.status_code == 304:
            result_message = f"The {self.config_name} configuration for the tenant {self.tenant_name} has not changed"
            # logger.info(result_message)
        elif response.status_code == 200:
            # The configuration for the tenant has changed, therefore update it
            result_message = f"The {self.config_name} configuration for the tenant {self.tenant_name} has changed, therefore updating it"
            logger.info(result_message)
            self.update_configuration(json_dict=response.json())
            has_changed = True
        else:
            result_message = f"The {self.config_name} configuration not available - Error when making request to sts: {response.text}"
            logger.warning(result_message)
        self.configuration["has_changed"] = has_changed

    @staticmethod
    def extract_config(json_dict: dict) -> Dict[str, str]:
        """Extract credentials from a 'configurations' key from an STS ApplicationConfiguration dictionary

        Args:
            json_dict (dict): STS ApplicationConfiguration dictionary

        Returns:
            Dict[str, str]: Credentials in a dictionary format
        """
        d = {}
        for field in json_dict:
            if json_dict[field]["$type"] == "MultiselectConfigurationValue":
                l = [x["value"] for x in json_dict[field]["values"]]
            else:
                l = json_dict[field]["value"]

            d[re.sub(r"\s+", "", field)] = l

        formatted_d = {}
        for field in d:
            try:
                formatted_d[field] = literal_eval(
                    literal_eval(f'"""{d[field]}"""'))
            except:
                formatted_d[field] = literal_eval(f'"""{d[field]}"""')

        return formatted_d
