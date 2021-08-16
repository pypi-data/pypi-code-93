import requests
import pandas as pd


class Client():
    """
    Description: 

    Attributes:
        attr_a username : string -> Authentication
        attr_b : string -> Authentication
    """

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.url = f'http://147.182.201.104/messages/package_authentication/{self.email}/{self.password}/'
        

    @property
    def authenticated(self):
        url = self.url
        print()
        response = requests.get(url=url)
        print(response)
        if response.status_code == 200:
            print('Authencated')
            return True
        else:
            return False
        
    def send_bulk_sms(self, message, csv, title):
        print(self.authenticated)
        contacts = ''
        df = pd.read_csv(csv)
        msg = 0
        for index, row in df.iterrows():
            initial_number = row['numbers']
            
            contacts += str(initial_number) + ','
            msg += 1
        print(contacts, )
        if self.authenticated:
            url = f'http://147.182.201.104/messages/intelli_gateway_package_api/{self.email}/0/{contacts}/True/{title}/{message}/{msg}/'
            response = requests.get(url)
            print(url)
            print(response)
            return response
        else:
            raise Exception('Your are not authenticated')

    def send_single_sms(self, message, receiver, title):
        if self.authenticated:
            url = f'http://147.182.201.104/messages/intelli_gateway_package_api/{self.email}/{receiver}/0/False/{title}/{message}/0/'
            response = requests.get(url)
            print(url)
            print(response)
            return response
        else:
            raise Exception('Your are not authenticated')
