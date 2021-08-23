import glob
import json
import logging
import os
import sys
from ast import literal_eval
from pathlib import Path
from typing import Any, Dict

import jwt
import requests
from fastapi import Depends, HTTPException, status
from jwt import PyJWKClient

from .Configuration import *
from .ConfigurationTemplate import *
from .Forms import *


logger = logging.getLogger("ConfigManager")
logger.setLevel(os.environ.get("LOG_LEVEL"))

AUTH_SCOPE = os.environ.get("AUTH_SCOPE")
LOGIN_URL = os.environ.get("AUTH_LOGIN_URL")
oauth2_scheme = OAuth2ImplicitCodeBearer(
    authorizationUrl=LOGIN_URL,
    tokenUrl="token",
    scopes={AUTH_SCOPE: "Full Control"},
)


class ConfigManager:
    """A class that dealt with configuration and configuration templates from the STS API for a specific config and tenant.

    Currenly supports: 
     - ModelManager
     - NerAnnotation
     - NerLabelOntologyMapping
     - GoogleTranslateCredentials

    Creates ConfigurationTemplate() for a specific application and Configuration() for its representation for the tenant.
    """

    def __init__(self, available_configurations: list = [
        Path(template_name).stem
        for template_name in glob.glob(f"{os.path.dirname(__file__)}/credential_templates/*.json")
    ]) -> None:
        self.available_configurations = available_configurations
        self.jwks_client = None
        self.set_sts_jwks_client()
        self.oauth2_scheme = None
        self.sts_credentials = {}
        self.set_sts_credentials()
        self.sts_application_url_dict = {}
        self.set_sts_application_urls()
        self.config_template_dict = {}
        self.set_config_templates()
        self.config_dict = {
            key: {} for key in available_configurations}
        self.get_default_tenant_config()

    def set_sts_jwks_client(self):
        """set the jwks client for connecting to the sts server and verifying the token
        Raises:
            KeyError: if the environment variable is not present
        """
        JWKS_URL = os.environ.get("AUTH_JWKS_URL")
        self.jwks_client = PyJWKClient(JWKS_URL)

    def get_default_tenant_config(self) -> None:
        """ Initialize configuration for default tenant and return its token_info """
        self.default_tenant_id = os.environ.get(
            "STS_APPLICATION_DEFAULT_TENANT_ID")
        self.default_tenant_name = os.environ.get(
            "STS_APPLICATION_DEFAULT_TENANT_NAME")
        token = self.get_authentication_token()
        delegated_token = self.get_delegated_token(token)
        tenant_config = self.get_config_for_tenant(
            delegated_token, self.default_tenant_name, self.default_tenant_id)
        token_info = Token(
            token=token, tenant_name=self.default_tenant_name, tenant_id=self.default_tenant_id, tenant_config=tenant_config)

        return token_info

    def set_config_templates(self) -> None:
        """ Sets the configuration template classes for each template name and available tenant """
        token = self.get_authentication_token()

        headers = {'Authorization': f'Bearer {token}',
                   'content-type': 'application/json'}

        for config_name in self.available_configurations:
            response = requests.get(
                self.sts_application_url_dict[config_name],
                headers=headers
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                    detail=f"There was an error editing the {config_name} template: {response.text}")

            config_dict = response.json()
            self.config_template_dict[config_name] = ConfigurationTemplate(
                config_dict, self.sts_application_url_dict[config_name])

    def get_config_for_tenant(self, delegated_token: str, tenant_name: str, tenant_id: str) -> dict:
        """derives the config using  delegated token by loading it or updating it based on the availability.

        Args:
            delegated_token (str): a token which was delegated to the correct config acces credentials.
            tenant_name (str): name for the tenant
            tenant_id (str): id for the tenant

        Returns:
            dict: a dictionary with config info for each of the templatess
        """
        for config_name in self.config_template_dict:
            if tenant_name not in self.config_template_dict[config_name].tenants:
                logger.info(
                    f"Create {config_name} configuration template for tenant {tenant_name} - {tenant_id}")
                self.config_template_dict[config_name].add_tenant(
                    tenant_name, delegated_token)

            if tenant_name not in self.config_dict[config_name]:
                logger.info(
                    f"Retrieve {config_name} configuration from sts for tenant {tenant_name} - {tenant_id}")
                self.create_config(config_name, tenant_id,
                                   tenant_name, delegated_token)

            # logger.debug(
            #     f"Update if change in {config_name} configuration for tenant {tenant_name} - {tenant_id}")
            self.config_dict[config_name][tenant_name].update_config_if_changed(
                delegated_token)

        # filter for tenant specific configs
        tenant_specific_configs = {}
        for config_name in self.config_dict:

            tenant_specific_configs[config_name] = self.config_dict[config_name][tenant_name].get_configuration(
            )

        # check for empty configs
        empty_configs = []
        for config_name in self.config_dict:
            if not tenant_specific_configs[config_name]['configurations']:
                empty_configs.append(config_name)
                default_config = self.config_dict[config_name][self.default_tenant_name].get_configuration()
                if not default_config.get('configurations', None):
                    logger.warning(
                        f"Application {config_name} is empty for default tenant {self.default_tenant_name} - {self.default_tenant_id}")
                tenant_specific_configs[config_name] = default_config

        if empty_configs:
            logger.warning(
                f"Application(s) {', '.join(empty_configs)} are empty for tenant {tenant_name} - {tenant_id}, defaulting to tenant {self.default_tenant_name} - {self.default_tenant_id}")

        return tenant_specific_configs

    def create_config(self, config_name: str, tenant_id: str, tenant_name: str, token: str) -> None:
        """Create a local copy of the configuration for a specifc tenant from the sts profile API
        Args:
            config_name (str): name of the configuration 
            tenant_id (str): id of the tenant
            tenant_name (str): name of te tenant
            token (str): a delegated token
        """
        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = requests.get(
            self.sts_application_config_url.format(
                name=config_name, tenant_id=tenant_id),
            headers=headers
        )

        if response.ok:
            response_dict = response.json()
            result_message = f"{config_name} configuration is available in sts, creating a configuration for tenant {tenant_name} - {tenant_id}"
            logger.info(result_message)
            self.config_dict[config_name][tenant_name] = Configuration(
                response_dict, tenant_id, tenant_name, config_name, self.sts_application_config_url)
        else:
            result_message = f"{config_name} configuration for tenant {tenant_name} - {tenant_id} is not available in sts"
            logger.info(result_message)

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode an authentication jwt token

        Args:
            token (str): the encoded token string

        Returns:
            Dict[str, Any]: a decoded token dictionary
        """
        ALGORITHM = os.environ.get("AUTH_ALGORITHM")
        AUDIENCE = os.environ.get("AUTH_AUDIENCE")

        signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        decoded_token = jwt.decode(
            token, signing_key.key, audience=AUDIENCE, algorithms=[ALGORITHM]
        )

        return decoded_token

    def get_dependencies(self) -> list:
        """return the basic PI authorization dependencies for FastAPI

        Returns:
            [list]: basic dependency list
        """
        dependencies = []

        if "--reload" not in sys.argv:
            dependencies = [Depends(self.get_current_user_no_config)]

        return dependencies

    async def get_current_user_no_config(self, token: str = Depends(oauth2_scheme)):
        """get the curren user info from the token oauth2 scheme.

        Args:
            token (str, optional): a token model containing tenant name, id. Defaults to Depends(oauth2_scheme).

        Raises:
            credentials_exception: if the token could not be decoded.

        Returns:
            Token: tokenname, tokenid, token
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            decoded_token = self.decode_token(token)
            tenant_name = decoded_token.get('tenantname')
            tenant_id = decoded_token.get('tenantid')
            token_info = Token(
                token=token, tenant_name=tenant_name, tenant_id=tenant_id)
        except Exception as _:
            raise credentials_exception

        return token_info

    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        """get the curren user info from the token oauth2 scheme.

        Args:
            token (str, optional): a token model containing tenant name, id and user app config. Defaults to Depends(oauth2_scheme).

        Raises:
            credentials_exception: if the token could not be decoded.

        Returns:
            Token: tokenname, tokenid, token, condfig
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            decoded_token = self.decode_token(token)
            tenant_name = decoded_token.get('tenantname')
            tenant_id = decoded_token.get('tenantid')
            delegated_token = self.get_delegated_token(token)
        except Exception as _:
            raise credentials_exception
        tenant_config = self.get_config_for_tenant(
            delegated_token, tenant_name, tenant_id)
        token_info = Token(
            token=token, tenant_name=tenant_name, tenant_id=tenant_id, tenant_config=tenant_config)

        return token_info

    def set_sts_application_urls(self):
        """Set the STS credentials for obtaining profile applications

        Raises:
            Exception: if any of the required environmental variables are not present
        """
        self.sts_basic_url = os.environ.get("STS_APPLICATION_BASIC_URL")
        self.sts_application_config_url = os.environ.get(
            "STS_APPLICATION_CONFIG_URL")

        for config_name in self.available_configurations:
            self.sts_application_url_dict[config_name] = self.sts_basic_url + \
                f"/{config_name}"

    def set_sts_credentials(self):
        """Setting the STS credentials for basic authentication

        Raises:
            HTTPException: if some of the credential environment variables are missing
        """
        self.grant_type = os.environ.get(
            "MODEL_MANAGER_GRANT_TYPE", "client_credentials")
        self.client_id = os.environ.get("MODEL_MANAGER_CLIENT_ID")
        self.client_secret = os.environ.get(
            "MODEL_MANAGER_CLIENT_SECRET")
        self.scope = os.environ.get("MODEL_MANAGER_SCOPE")
        self.login_url = os.environ.get("MODEL_MANAGER_LOGIN_URL")

        self.sts_credentials = {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
        }

    def get_delegated_token(self, token: str) -> str:
        """Delegate a tenant-specific user token

        Args:
            token (str): bearer token

        Returns:
            str: delegated bearer token
        """
        sts_delegation_credentials = self.sts_credentials.copy()
        if "identityserverprofile.fullcontrol" not in sts_delegation_credentials['scope']:
            sts_delegation_credentials['scope'] += " identityserverprofile.fullcontrol"

        sts_delegation_credentials['token'] = token
        sts_delegation_credentials['grant_type'] = "delegation"

        response = requests.post(
            self.login_url, data=sts_delegation_credentials)
        result = json.loads(response.text)
        token = result["access_token"]

        return token

    def get_authentication_token(self) -> str:
        """Authenticate and receive a bearer token from STS

        Returns:
            str: bearer token
        """
        response = requests.post(self.login_url, data=self.sts_credentials)
        result = json.loads(response.text)
        token = result["access_token"]

        return token
