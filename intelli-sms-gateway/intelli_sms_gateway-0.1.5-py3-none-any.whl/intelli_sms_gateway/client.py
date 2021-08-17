import requests
import pandas as pd
import json


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

        if response.status_code == 200:
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
        
        if self.authenticated:

            try:
                url = f'http://147.182.201.104/messages/intelli_gateway_package_api/{self.email}/0/{contacts}/True/{title}/{message}/{msg}/'
                requests.get(url)
                dict_response = {
                    "status":"200",
                    "sent": True,
                    "description":"Your message has been sent"
                }
                json_response = json.dumps(dict_response)

                print(json_response)
                
                return json_response
            except:
                resposne = {
                    "status":"Failed",
                    "description":"Something went wrong."
                }

                print(resposne)

                return resposne
        else:
            dict_response = {
                    "status":"401",
                    "sent": False,
                    "description":"unauthorized"
                }
            json_response = json.dumps(dict_response)

            print(json_response)

            return json_response

    def send_single_sms(self, message, receiver, title):
        if self.authenticated:
            try:
                url = f'http://147.182.201.104/messages/intelli_gateway_package_api/{self.email}/{receiver}/0/False/{title}/{message}/0/'

                requests.get(url)

                dict_response = {
                    "status":"200",
                    "sent": True,
                    "description":"Your message has been sent"
                }
                json_response = json.dumps(dict_response)

                print(json_response)

                return json_response

            except:
                resposne = {
                    "status":"Failed",
                    "description":"Something went wrong."
                }

                print(resposne)

                return resposne

        else:
            dict_response = {
                    "status":"401",
                    "sent": False,
                    "description":"unauthorized"
                }
            json_response = json.dumps(dict_response)

            print(json_response)

            return json_response



s = Client('mgunityrone@gmai.com', '123abc!!!')

s.send_single_sms('Hello world', '263777606983', 'Sup')