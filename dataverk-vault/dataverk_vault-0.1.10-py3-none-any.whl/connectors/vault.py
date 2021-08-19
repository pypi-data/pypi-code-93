from dataverk_vault.utils import request_wrappers


class VaultConnector:

    def __init__(self, settings):
        self._settings = settings
        self._client_token = None

    def __enter__(self):
        self.authenticate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def authenticate(self):
        res = request_wrappers.request_post_wrapper(self._settings["auth_url"],
                                                    json={"jwt": self._settings["token"], "role": self._get_role()})
        res.raise_for_status()
        self._client_token = res.json()["auth"]["client_token"]

    def read_secrets(self):
        """ Fetch secrets from vault and return dict

        :return: dict: secrets
        """
        res = request_wrappers.request_get_wrapper(self._settings["secrets_url"],
                                                   headers={"X-Vault-Token": self._client_token})
        res.raise_for_status()
        return res.json()["data"]

    def get_db_credentials(self, vault_path):
        """ Get new database credentials

        :param vault_path: str
        :return: string with username and password
        """
        res = request_wrappers.request_get_wrapper(f"{self._settings['vault_address']}/v1/{vault_path}",
                                                   headers={"X-Vault-Token": self._client_token})

        res.raise_for_status()
        credentials = res.json()["data"]
        return f"{credentials['username']}:{credentials['password']}"

    def _get_role(self):
        if self._settings.get("app_name"):
            return self._settings["app_name"]
        else:
            return self._settings["namespace"]
