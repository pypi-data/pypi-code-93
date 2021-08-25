from __future__ import absolute_import
from __future__ import unicode_literals

import requests
from laipvt.sysutil.util import to_json

class HarborModel():
    def __init__(self, host: str, username: str, password: str, scheme="http"):
        self.harbor = requests
        self.base_url = "%s://%s:%s@%s/api/v2.0" % (scheme, username, password, host)

    def _parse_image(self, image: str) -> dict:
        i = image.split("/")
        return {
            "project": i[0],
            "image": i[1]
        }

    def list_project(self) -> dict:
        url = self.base_url + "/projects"
        return self.harbor.get(url).json()

    def list_project_name(self) -> list:
        l = []
        data = self.list_project()
        for p in data:
            l.append(p["name"])
        return l

    def get_project_id(self, name: str) -> int:
        data = self.list_project()
        for p in data:
            if p["name"] == name:
                return p["project_id"]

    def create_project(self, name, count_limit=100, storage_limit=-1) -> bool:
        url = self.base_url + "/projects"
        data = {
            "count_limit": count_limit,
            "storage_limit": storage_limit,
            "project_name": name,
            "metadata": {
                "public": "true"
            }
        }
        self.harbor.post(url, data=to_json(data))
        if name in self.list_project_name():
            return True
        return False

    def delete_project(self, name: str) -> bool:
        id = self.get_project_id(name)
        url = self.base_url + "/projects/{}".format(id)
        self.harbor.delete(url)
        if name not in self.list_project_name():
            return True
        return False

    def list_images(self, project: str) -> dict:
        url = self.base_url + "/projects/{}/repositories".format(project)
        return self.harbor.get(url).json()

    def list_images_name(self, project: str) -> list:
        l = []
        data = self.list_images(project)
        for p in data:
            l.append(self._parse_image(p["name"])["image"])
        return l