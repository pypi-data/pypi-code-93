import os
import requests
import array

from dotenv import load_dotenv
load_dotenv()


API_KEY = os.getenv('ARKESEL_API_KEY')


class APIKeyMissingError(Exception):
    pass


if API_KEY is None:
    raise APIKeyMissingError(
        "All methods require an API key. See "
        "https://sms.arkesel.com/user/sms-api/info "
        "for how to retrieve an API key from Arkesel "
    )


session = requests.Session()
session.params = {}
session.params['api_key'] = API_KEY


class Contacts(object):
    def __init__(self) :
        pass


    def create_contact_group(self, group_name:str):
        URL = "https://sms.arkesel.com/api/v2/contacts/groups"
        header = {"api-key":API_KEY , 'Content-Type': 'application/json', 'Accept':'application/json'}
        
        payload ={
            "group_name":group_name   
        }
        response =  requests.post(URL , headers=header , json=payload)
        return response.json()
        # print (response.text)
    # create_contact_group("TEST GROUP")
    
    def add_contact_to_group(self ,group_name:str , contacts:array.array):
        URL = "https://sms.arkesel.com/api/v2/contacts" 
        header = {"api-key":API_KEY , 'Content-Type':'application/json', 'Accept':'application/json'}

        payload ={
            "group_name":group_name,
            "contacts":contacts
        }
        response = requests.post(URL,headers=header,json=payload)
        return response.json()
        # print (response.text)
    # add_contact_to_group("TEST GROUP" , [{
    #                         "phone_number": "233248649732"
    #                         },
    #                         {
    #                         "phone_number": "233202087572"
    #                         } ])
