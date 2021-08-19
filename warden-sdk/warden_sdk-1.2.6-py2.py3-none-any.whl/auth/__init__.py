"""Auth folder initializer.

Here we initialize the functions we want to make available to the sdk, making them easily accessible. On top of that, we setup a function to verify the client.
"""
import requests
import json

from warden_sdk.utils import (get_options)


def verify_client(options: dict) -> None:
   """
   Verify API Key module is used to verify and activate Warden to be used internally. If the key is invalid or expired, Warden returns an error is raised by the SDK. 

   Args::
      options: A dictionary containing all of the values that were used to initialize the `warden_sdk` 

   Raises::
      InvalidKey: --
   """
   options = get_options(options)

   resp: dict = requests.post(
       'https://api.warden_sdk.ferant.io/credentials/v1/validate/' +
       options['creds']['client_id'] + '/' + options['service'] + '/' +
       options['api'],
       headers={'Authorization': 'Bearer ' + options['creds']['client_secret']},
       data=json.dumps({'scopes': options['scopes']}))
   resp = json.loads(resp.text)

   if 'error' in resp.keys():
      # Create custom error or get Custom error from Warden API
      raise Exception(resp['error'])