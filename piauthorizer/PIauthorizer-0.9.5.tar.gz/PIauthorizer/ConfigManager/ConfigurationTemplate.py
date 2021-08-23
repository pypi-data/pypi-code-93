import json
import logging
import os

import requests
from fastapi.exceptions import HTTPException

logger = logging.getLogger("ConfigurationTemplate")
logger.setLevel(os.environ.get("LOG_LEVEL"))


class ConfigurationTemplate:
    """An Application template for a specific Application Conigguration from the STS API"""

    def __init__(self, config_dict: dict, sts_application_url: str) -> None:

        self.sts_application_url = sts_application_url
        self.application = config_dict
        self.etag = config_dict["@meta.ETag"]
        self.config_name = config_dict['name']
        self.tenants = []
        
        for field in self.application['configurations']:
            if field['tenants']:
                self.tenants = field['tenants']
                break

    def add_tenant(self, tenant_name: str, token: str) -> None:
        """Add a tenant to the Application template.

        Args:
            tenant_name (str): tenant name
        """
        
        self.reset(token)
        
        logger.info(
            f"Adding tenant {tenant_name} to the template {self.config_name}.")
        if tenant_name not in self.tenants:
            self.tenants.append(tenant_name)
            for field in self.application['configurations']:
                if tenant_name not in field['tenants']:
                    field['tenants'].append(tenant_name)

        self.update_template(tenant_name, token)

    def remove_tenant(self, tenant_name: str) -> None:
        """Remove a tenant from the Application template.

        Args:
            tenant_name (str): tenant name
        """
        if tenant_name in self.tenants:
            self.tenants.remove(tenant_name)
            for field in self.application['configurations']:
                if tenant_name in field['tenants']:
                    field['tenants'].remove(tenant_name)

    def get_template(self) -> str:
        """Obtain the Application template in a string representation

        Returns:
            str: the application template
        """
        return json.dumps(self.application)

    def set_template(self, template: str) -> None:
        """Set the Application template from a string representation

        Args:
            template (str): string representation of the Application template
        """
        self.application = json.loads(template)

    def update_template(self, tenant_name: str, token: str) -> None:
        """Updates the template in the Application Configuraiton admin server

        Args:
            token (str): the bearer token
            tenant_name (str): tenant _name

        Raises:
            HTTPException: If there was an error editing
        """
        logger.info(
            f"Updating template for the template {self.config_name}.")
        headers = {'Authorization': f'Bearer {token}',
                   'content-type': 'application/json'}
        
        response = requests.put(self.sts_application_url,
                                headers=headers,
                                data=self.get_template())
        
        if response.status_code != 200:
            self.remove_tenant(tenant_name)
            msg = f"There was an error editing the {self.config_name} configuration template for tenant {tenant_name}. "
            if response.status_code == 409:
                msg += "Someone else was already editing the template."
            raise HTTPException(status_code=response.status_code, detail=msg)

    def reset(self, token: str) -> None:
        """resets the ConfigurationTemplate if changed
        Args:
            token (str): A delegated token to make requests

        Raises:
            HTTPException: if getting the new template isn't an option.
        """
        headers = {'Authorization': f'Bearer {token}',
                   'content-type': 'application/json',
                   "If-None-Match": self.etag}
        response = requests.get(
            self.sts_application_url,
            headers=headers
        )
        if response.status_code == 304:
            pass
        elif response.status_code == 200:
            config_dict = response.json()
            self.__init__(config_dict, self.sts_application_url)
        else:
            msg = f"There was an error editing the {self.config_name} configuration template."
            raise HTTPException(status_code=response.status_code, detail=msg)

            
