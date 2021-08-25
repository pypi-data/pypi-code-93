
import json
import requests
import pprint
import urllib
import webbrowser

class MMClient:
    def __init__(self, server):
        self.server = server
        self.token = 'No token'

    def set_server(self, server):
        self.server = server

    def register(self, email, password, hasGroup):
        r = requests.post(self.server + '/register', 
            json={"email": email, "password": password, "hasGroup":hasGroup})

        if r.status_code==200:
            return True
        else:
            print(r.text)
            return False
            
    def login(self, email, password):
        r = requests.post(self.server + '/login', json={"email": email, "password": password})
        j = r.json()
        if 'token' in j:
            self.token = j['token']
            if 'group' in j: 
                print("Group: " + j['group'])
            return True
        else:
            print(r.text)
            return False

    def types(self):
        return requests.get(self.server + '/types', headers={'Authorization': self.token})

    """
    Example:
        filter={"doctype":"kunddokument", "kundnummer":"AAA"}
        sort: {"kundnummer": 1}
        range: {"from":100, "to:200"}
    """
    def search(self, filter=None, sort=None, range=None):
        if not filter:
            filter = {}
        if not sort:
            sort = {} 
        if not range:
            range = {}
        params = urllib.parse.urlencode({'filter': filter, 'sort': sort, 'range': range}) # json(), status_code
        print(params)
        return requests.get(self.server + '/documents?' + params, headers={'Authorization': self.token})

    def upload(self, data, path, id):
        url = self.server + '/document'
        if id: url += '/' + id
        response = requests.post(url, data=data, headers={'Authorization': self.token})
        #self.dump(response)
        response = response.json()
        if 'url' not in response: 
            return False, response
        url = response['url']
        fields = response['fields']
        id = response['id']
        with open(path, 'rb') as f:
            files = {'file': (path, f, 'applicaion/pdf'),
                 'Content-Disposition': 'form-data; name="files"',
                 'Content-Type': 'application/pdf'}
            response = requests.post(url, files=files, data=fields)
            if not response.ok:
                return False, ('Failed upload to Minio. Reason: ' +
                  response.reason + '. Text:' + response.text)

            return True, id

    def download(self, id):
        url = self.server + '/document/' + id
        response = requests.get(url, headers={'Authorization': self.token})
        if not response.ok:
            return False, ('Get document failed. Reason: ' +
                  response.reason + '. Text:' + response.text)
        webbrowser.open(response.json()['url'])
        return True, "OK"

    def metadata(self, id):
        url = self.server + '/document/' + id + '?type=metadata'
        response = requests.get(url, headers={'Authorization': self.token})
        if not response.ok:
            return False, ('Get metadata failed. Reason: ' +
                  response.reason + '. Text:' + response.text)
        pprint.pprint(response.json()['metadata'])
        return True, "OK"

    def audit(self, id):
        url = self.server + '/document/' + id + '?type=audit'
        response = requests.get(url, headers={'Authorization': self.token})
        if not response.ok:
            return False, ('Get audits failed. Reason: ' +
                  response.reason + '. Text:' + response.text)
        pprint.pprint(response.json()['audit'])
        return True, "OK"

    def update(self, id, metadata):
        data = {}
        data['metadata'] = metadata
        rsp = requests.put(self.server + "/document/" + id, json=data, headers={'Authorization': self.token});
        #self.dump(rsp)
        return rsp

    def delete(self, id):
        data = {}
        data['id'] = id
        rsp = requests.delete(self.server + "/document/" + id,headers={'Authorization': self.token})
        return rsp

    def count(self):
        url = self.server + '/count'
        return requests.get(url, headers={'Authorization': self.token})

    def dump(self, response):
        print(response.request.method)
        print(response.request.url)
        print(response.request.body)
        print(response.request.headers)

