'''
Created on 3 Nov 2020

@author: jacklok
'''
from cryptography.fernet import Fernet
from trexlib.conf import CRYPTO_SECRET_KEY
from six import string_types
import json, logging

logger = logging.getLogger('utils')

def encrypt(value):
    
    if value:
        f = Fernet(CRYPTO_SECRET_KEY)
        return f.encrypt(value.encode()).decode('utf-8')
    
def encrypt_json(json_value):
    
    if json_value:
        f = Fernet(CRYPTO_SECRET_KEY)
        return f.encrypt(json.dumps(json_value).encode()).decode('utf-8')
    
def decrypt(value):
    if value:
        value = str.encode(value)
            
        f = Fernet(CRYPTO_SECRET_KEY)
        return f.decrypt(value).decode('utf-8')
    
def decrypt_json(value):
    json_value_in_str = decrypt(value)
    if json_value_in_str:
        return json.loads(json_value_in_str)     
