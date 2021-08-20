import requests
import os

urlGet = "https://api.transferhub.eu"
urlGetToken = "Token_url"



requests.get(urlGet, 
    auth=(os.getenv('API_USER'), 
    os.environ.get('API_PASSWORD'))
)



def models():
    """
    Returns list of all the currently available models on Transferhub.
    """
    try:
        response = requests.get(urlGet + "/models", timeout=5, allow_redirects=True)
        response.raise_for_status()
        json = response.json()
        for key in json:
            print(key , json[key])     
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)


def list_categories():
    """
    Returns list of all the currently available categories on Transferhub.
    """
    try:
        response = requests.get(urlGet + "/categories", timeout=5, allow_redirects=True)
        response.raise_for_status()
        json = response.json()
        for key in json:
            print(key , json[key])
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)


from typing import Optional
import requests


urlGet = "https://api.transferhub.eu"
urlGetToken = "Token_url"

#Gets Token to download model from s3
def _getTokenForDownload():
    try:
        response = requests.get(urlGetToken, timeout=5, allow_redirects= True)
        response.raise_for_status()
        return response.content()
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)  



def download_model(model_name: str, version: Optional[str], save_dir: str):
    """
    Downloads model from AWS s3 bucket with the given model_id. Only works if the AWS access_key and access_id are stored 
    as an environment variable. Also dependant on valid Transferhub-API authentification details stored as an environment variable.
    """
    response_content = _getTokenForDownload()
    with open(save_dir / model_name, 'wb') as f:
        f.write(response_content)
    return None

import logging
import requests
import os
import boto3
from botocore.exceptions import ClientError

urlPost = "API_url"
urlGet = "API_url"
urlGetToken = "Token_url"


requests.get(urlGet, 
    auth=(os.getenv('API_USER'), 
    os.environ.get('API_PASSWORD'))
)


#Gets Token to upload to s3
def _getTokenForUpload():
    try:
        response = requests.get(urlGetToken, timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)  




def upload_file(s3, file_name, bucket, object_name=None):
    """
    Uploads model to AWS s3 bucket with the given file_name. Only works if the AWS access_key and access_id are stored 
    as an environment variable. Also dependant on valid Transferhub-API authentification details stored as an environment variable.
    """

    #create the client
    s3 = boto3.client(
        's3',
        region_name = 'eu-central-1',
        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY'),
        aws_session_token = _getTokenForUpload(),
    )

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    try:
        response = s3.upload_file(file_name, bucket, object_name)
        print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True
    







