from typing import Dict

import requests

from dataverk_publisher.utils.logger import Logger


class ElasticSearchWriter(Logger):
    def __init__(self, es_host: str, datapackage_metadata: Dict, es_token: str = None):
        super().__init__()
        self._host = es_host
        self._dp_meta = datapackage_metadata
        self._es_token = es_token

    def _create_es_doc(self) -> tuple:

        dp_id = self._dp_meta["id"]
        title = self._dp_meta.get("title", "title missing")
        desc = self._dp_meta.get("description", "description missing")
        doc = {
            "id": dp_id,
            "type": "datapackage",
            "format": "datapackage",
            "suggest": title + " " + desc,
            "description": desc,
            "title": title,
            "license": self._dp_meta.get(
                "license",
                {
                    "name": "CC BY 4.0",
                    "url": "http://creativecommons.org/licenses/by/4.0/deed.no",
                },
            ),
            "language": self._dp_meta.get("language", "Norsk"),
            "periodicity": self._dp_meta.get("accrualPeriodicity", ""),
            "temporal": self._dp_meta.get("temporal", {}),
            "rights": self._dp_meta.get("rights", ""),
            "provenance": self._dp_meta.get("provenance", ""),
            "issued": self._dp_meta.get("issued"),
            "modified": self._dp_meta.get("modified"),
            "keyword": self._dp_meta.get("keywords", []),
            "theme": self._dp_meta.get("theme", []),
            "accessRights": self._dp_meta.get("accessRights", "internal").lower(),
            "publisher": self._dp_meta.get(
                "publisher",
                {
                    "name": "Arbeids- og velferdsetaten (NAV)",
                    "publisher_url": "https://www.nav.no",
                },
            ),
            "creator": self._dp_meta.get("creator", {}),
            "contactPoint": self._dp_meta.get("contactPoint", []),
            "spatial": self._dp_meta.get("spatial", ""),
            "url": f"{self._dp_meta.get('path', '')}/datapackage.json",
            "uri": f"{self._dp_meta.get('path', '')}/datapackage.json",
            "repo": self._dp_meta.get("repo", ""),
            "resources": self._dp_meta.get("resources", []),
            "views": self._dp_meta.get("views", []),
        }

        return dp_id, doc

    def write_metadata(self):
        dp_id, doc = self._create_es_doc()

        headers = {"Content-Type": "application/json"}
        if self._es_token:
            headers["Authorization"] = f"bearer {self._es_token}"

        try:
            res = requests.put(
                f"{self._host}/v1/datapackage/{self._dp_meta['id']}",
                json=doc,
                headers=headers,
            )
            res.raise_for_status()
        except requests.exceptions.HTTPError as err:
            self.logger.error(
                f"Unable to write es doc to metadata api {self._host}: {str(err)}"
            )
            self.logger.error(f"{res.text}")
            raise
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Connection error {self._host}: {str(err)}")
            raise
        else:
            self.logger.info(
                f"ES doc for datapackage {res.json()['id']} written successfully to data catalog"
            )
            return res.json()
