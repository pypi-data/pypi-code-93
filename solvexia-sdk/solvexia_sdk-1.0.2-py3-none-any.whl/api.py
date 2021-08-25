import requests
import json
import sys

class solvexiaClient: 
    def __init__(self, auth_file):
        with open(auth_file) as json_auth_file:
            payload = json.load(json_auth_file)
        self.env = payload['env']
        self.client_id = payload['client_id']
        self.client_secret = payload['client_secret']
        global base_url
        base_url = f"https://{self.env}.solvexia.com/api/v1/"

    def get_access_token(self):
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"https://{self.env}.solvexia.com/oauth/token", data=json.dumps(payload), headers=headers)
        if response.status_code != 200:
            print("Error generating an Access Token via Client Credential Flow")
            sys.exit()
        self.access_token = response.json()['access_token']
        self.authorisation = {'Authorization': 'Bearer ' + self.access_token}
        global access_token 
        access_token = self.authorisation

def status_code_check(response, error_message):
    if response.status_code != 200:
        print(error_message)
        print(response.json()['message'])
        sys.exit()

def api_post(url_path, payload):
    headers = access_token.copy()
    headers['Content-Type'] = 'application/json'
    response = requests.post(base_url + url_path, data=json.dumps(payload), headers=headers)
    return response

def api_post_no_payload(url_path):
    response = requests.post(base_url + url_path, headers=access_token)
    return response

def api_get(url_path):
    response = requests.get(base_url + url_path, headers=access_token)
    return response