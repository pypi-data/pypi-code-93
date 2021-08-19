""" 
Firestore
~~~~~~~~~~~~~~~~~~~~~
use cloud firestore without using firebase Admin API
"""

import json
import requests
from requests.exceptions import HTTPError


class Firestore():
    """ 
Firestore
~~~~~~~~~~~~~~~~~~~~~
use cloud firestore without using firebase Admin API
    """
    data: dict = {}
    child = ""
    config = {}

    # docId: str = config[""]

    def setConfig(self, config):
        self.config = config
        self.projectId: str = self.config["projectId"]

    def setData(self, **args):
        self.data.update(args)

    def showData(self):

        print(self.data)

    def setChild(self, child):
        self.child = child

    def sendData(self):
        request_ref = f"https://firestore.googleapis.com/v1/projects/{str(self.projectId)}/databases/(default)/documents/{self.child}"
        headers = {"content-type": "application/json; Accept: application/json"}

        d = {}
        for i in self.data:
            if type(self.data[i]) == str:
                d[str(i)] = {"stringValue": self.data[i]}
            if type(self.data[i]) == int:
                d[str(i)] = {"integerValue": self.data[i]}
            else:
                d[str(i)] = {"stringValue": self.data[i]}
        dataToSend = json.dumps({
            "fields": d
        })
        # print(json.dumps(dataToSend, indent=1))
        self.dataToSend = dataToSend
        request_object = requests.post(
            request_ref, headers=headers, data=dataToSend)
        self.response = request_object.json()
        self.data = {}
        return request_object.json()

    def getData(self):
        request_ref = f"https://firestore.googleapis.com/v1/projects/{str(self.projectId)}/databases/(default)/documents/{self.child}"
        headers = {"content-type": "application/json; Accept: application/json"}
        request_obj = requests.get(request_ref, headers=headers)
        print(json.dumps(request_obj.json(), indent=2))


if __name__ == "__main__":
    print("Use 'import python-firestore' to use ")
