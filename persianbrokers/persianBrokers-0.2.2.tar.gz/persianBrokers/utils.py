import requests
import os
from persianBrokers import  exception


def request(method, url,headers=None,data=None):
    response = requests.request(method, url,headers=headers, data=data)
    return response
    

def convert_json(response):
    res=response.json()
    return res

def give_token():
    try:
        return os.environ["token"]
    except:
        raise exception.TokenException("you didn't enter token, please use take_token" )


def take_token(token):
    os.environ["token"] = token
    