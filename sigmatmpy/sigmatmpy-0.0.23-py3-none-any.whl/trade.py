name = "sigmatmpy"
import requests
import json



class trade(object):
    def __init__(self,token):
        self.username = username
        self.password = password
        self.refresh_token(username,password)

    def refresh_token(self,username,password):

        login_url = 'https://api-pk-data.sigmatm.com.au/api/v1/auth/login'
        token = requests.post(login_url, json = {
            "email": username,
            "password": password
        })
        self.token = token.json()['access_token']

    
    def get_alert_data(self,alert):

        link = f'https://api-pk-data.sigmatm.com.au/api/v1/alert/data?broker_id=2&alert={alert}'
        response = requests.get(link , headers={'Authorization': f'Bearer {self.token}'})
        return response.json()
