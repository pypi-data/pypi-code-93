from tyba_client.models import PVModelTypes, PVStorageModel, StandaloneStorageModel
import requests
from urllib.parse import urljoin


class Client(object):
    """Tyba client class"""

    DEFAULT_OPTIONS = {
        'version': '0.1'
    }

    def __init__(self, personal_access_token, host="https://dev.tybaenergy.com"):
        """A :class:`Client` object for interacting with Tyba's API.
        """
        self.personal_access_token = personal_access_token
        self.host = host

    def _auth_header(self):
        return self.personal_access_token

    def _base_url(self):
        return self.host + "/public/" + self.DEFAULT_OPTIONS["version"] + "/"

    def schedule_pv(self, pv_model: PVModelTypes):
        model_json_dict = pv_model.to_dict()
        url = urljoin(self._base_url(), "schedule-pv")
        return requests.post(url,
                             json=model_json_dict,
                             headers={"Authorization": self._auth_header()})

    def schedule_storage(self, storage_model: StandaloneStorageModel):
        model_json_dict = storage_model.to_dict()
        url = urljoin(self._base_url(), "schedule-storage")
        return requests.post(url,
                             json=model_json_dict,
                             headers={"Authorization": self._auth_header()})

    def schedule_pv_storage(self, pv_storage_model: PVStorageModel):
        model_json_dict = pv_storage_model.to_dict()
        url = urljoin(self._base_url(), "schedule-pv-storage")
        return requests.post(url,
                             json=model_json_dict,
                             headers={"Authorization": self._auth_header()})

    def get_status(self, run_id: str):
        url = urljoin(self._base_url(), "get-status/" + run_id)
        return requests.get(url,
                            headers={"Authorization": self._auth_header()})

