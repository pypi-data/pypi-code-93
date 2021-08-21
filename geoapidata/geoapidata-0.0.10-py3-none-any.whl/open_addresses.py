import requests
import gzip
import urllib.request
from requests import exceptions
import json
import os

sources = [
           ("br/sc/joinville", "joinville"), 
           #("br/sc/statewide", "SC-state"), 
           #("br/pr/statewide", "PR-state"), 
           #("br/sp/statewide", "SP-state"), 
           #("br/rs/statewide", "RS-state"), 
           #("br/pr/curitiba", "curitiba"), 
           ]

def removeprefix(self: str, prefix: str) -> str:
    """
    Remove string prefix

    Parameters:
    ----------
    self: str
        original string
    prefix: str
        prefix to be removed

    Return: 
    ------
    str:
        prefix removed string
    """
    
    if self.startswith(prefix):
        return self[len(prefix):]
    else:
        return self[:]

def requestDataOpenAddresses(url: str, file_name: str) -> json:
    """
    This function requests location-based address databases directly from the open addresses API.
    
    
    Parameters:
    ----------
    url: str
        address dataset path, for example, br/sc/joinville.
    file_name: str
        name of dataset, for example, joinville


    Return:
    ------
    geojson:
        returns a geojson with information referring to addresses in a given location.

    Exceptions:
    ----------
    
    HTTPError:
        - system exit.
    Timeout:
        - system exit.
    ConnectionError:
        - system exit.
    """
    
    ORIGINAL_PREFIX = "s3://"
    REQUEST_PREFIX = "https://"

    END_POINT = 'https://batch.openaddresses.io/api/data/?source='
    response = requests.get(END_POINT+ '{}'.format(url))

    try:
        if response.status_code == 200: 
            temp_json = response.json()  
            response = temp_json[0] 

            DOWNLOAD_PATH = removeprefix(response['s3'], ORIGINAL_PREFIX) #Prefix remove
            
    
            with urllib.request.urlopen(REQUEST_PREFIX+DOWNLOAD_PATH) as r:
                with gzip.GzipFile(fileobj=r) as uncompressed:
                    file_content = uncompressed.read()
        
            return file_content
            
    
    except requests.exceptions.HTTPError as err: 
        raise SystemExit(err)
    except requests.exceptions.Timeout:
	    raise SystemExit()
    except requests.exceptions.ConnectionError():
        raise SystemExit()  



def save(json_response: json, file_name, directory_path: str = "Data/openaddresses/"):
    """
	This function will save the result of the request made to Open Addresses. 

	Parameters:
	-----------
	json_response: json
		response to the request to Open Addresses.
	file_name: str
		name for json file.
	directory_path: str
		path to save json. 

	"""
    try:
        os.makedirs(directory_path, exist_ok = True)
    except OSError as error:
        raise SystemError()

    with open(directory_path+ "{}.geojson".format(file_name), "wb") as f:
                f.write(json_response)


for f in sources:
  response = requestDataOpenAddresses(f[0], f[1]) # [0]: url; [1]: file_name
  save(response, f[1])