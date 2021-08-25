from dataclasses import dataclass
import jsons
import requests
from requests.exceptions import HTTPError
import json
import builtins
import os
from os.path import expanduser
from os.path import sep as separator
import time
from typing import Any, Dict, List, NoReturn, Tuple
import traceback

# TODO: DUPLICATED: have copies in other .py files. refactor later
def readJsonFileAndDeser(filename:str, cls) -> Tuple[str,Any]:
    """
    Reads the specified json file and deserializes it into the 'cls' that is specified.  Returns the read json(as a string) and the deserialized instance
    """
    # use empty json as the default
    filecontents = '{}'
    try:
        if os.path.isfile(filename):   # check for file existence before attempting to open() below since open() raises an exception if file not found
            with open(filename, "r") as f:
                filecontents:str = f.read()   #read the contents of the url            
    except Exception as e:
        builtins.log.error(f"Caught exception: {e}: " + traceback.format_exc())
        
    return (filecontents, jsons.loads(filecontents, cls))
    

# TODO: DUPLICATED: have copies in other .py files. refactor later
# {
#     "rclocal_shutdowndelay": 115,
#     "clientlib_verbose": false,
#     "server_extension_cognito_utils_verbose": false
# }
@dataclass
class InfinstorConfig(jsons.JsonSerializable):
    rclocal_shutdowndelay:int = 15                         # delay in minutes
    clientlib_verbose:bool = False                         
    server_extension_cognito_utils_verbose:bool = False

def set_verbose_flag():
    state_json_fname = os.path.join(os.path.expanduser("~"), ".infinstor", "config.json")
    infin_config:InfinstorConfig; jsonstr:str; (jsonstr, infin_config) = readJsonFileAndDeser(state_json_fname, InfinstorConfig)

    return infin_config.server_extension_cognito_utils_verbose

verbose = set_verbose_flag()

def read_token_file(tokfile):
    fclient_id = None
    ftoken = None
    frefresh_token = None
    ftoken_time = None
    fservice = None
    try:
        with (open(tokfile)) as fp:
            for count, line in enumerate(fp):
                if (line.startswith('ClientId=')):
                    fclient_id = line[len('ClientId='):].rstrip()
                if (line.startswith('Token=')):
                    ftoken = line[len('Token='):].rstrip()
                if (line.startswith('RefreshToken=')):
                    frefresh_token = line[len('RefreshToken='):].rstrip()
                if (line.startswith('TokenTimeEpochSeconds=')):
                    ftoken_time = int(line[len('TokenTimeEpochSeconds='):].rstrip())
                if (line.startswith('Service=')):
                    fservice = line[len('Service='):].rstrip()
    except FileNotFoundError as ferr:
        # tokenfile does not exist
        builtins.log.info('tokenfile does not exist')
    except Exception as err:
        builtins.log.error('while opening token file, caught ' + str(err))

    return ftoken, frefresh_token, ftoken_time, fclient_id, fservice

def write_token_file(tokfile, token_time, token, refresh_token, client_id, service):
    os.makedirs(os.path.dirname(tokfile), exist_ok=True)
    with open(tokfile, 'w') as wfile:
        wfile.write("Token=" + token + "\n")
        wfile.write("RefreshToken=" + refresh_token + "\n")
        wfile.write("ClientId=" + client_id + "\n")
        wfile.write("TokenTimeEpochSeconds=" + str(token_time) + "\n")
        wfile.write("Service=" + service + "\n")
        wfile.close()

def renew_token(tokfile, refresh_token, client_id, service):
    payload = "{\n"
    payload += "    \"AuthParameters\" : {\n"
    payload += "        \"REFRESH_TOKEN\" : \"" + refresh_token + "\"\n"
    payload += "    },\n"
    payload += "    \"AuthFlow\" : \"REFRESH_TOKEN_AUTH\",\n"
    payload += "    \"ClientId\" : \"" + client_id + "\"\n"
    payload += "}\n"

    url = 'https://cognito-idp.us-east-1.amazonaws.com:443/'

    headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
            }

    if (verbose):
        builtins.log.info("Calling renew_token with payload=" + payload)

    try:
        response = requests.post(url, data=payload, headers=headers)
    except Exception as err:
        builtins.log.error("renew_token: Caught " + str(err))
        raise
    else:
        if (response.status_code != 200):
            builtins.log.error("renew_token: Error. http status_code is " + str(response.status_code)
                    + ", response=" + str(response.text))
        else:
            authres = response.json()['AuthenticationResult']
            token = authres['AccessToken']
            token_time = int(time.time())
            write_token_file(tokfile, token_time, token, refresh_token, client_id, service)

def token_renewer():
    # read and set verbose flag everytime we are called..
    global verbose; verbose = set_verbose_flag()
    
    if (verbose):
        builtins.log.info('token_renewer(): called')
    home = expanduser("~")
    if (home[len(home) - 1] == '/'):
        dotinfinstor = home + ".infinstor"
    else:
        dotinfinstor = home + separator + ".infinstor"
    tokfile = dotinfinstor + separator + "token"

    token = None
    refresh_token = None
    token_time = None
    client_id = None
    service = None
    token, refresh_token, token_time, client_id, service = read_token_file(tokfile)
    if (token_time == None):
        if (verbose):
            builtins.log.info('token_renewer: token_time is None. Possibly custom token')
        return
    time_now = int(time.time())
    if ((token_time + (30 * 60)) < time_now):
        if (verbose):
            builtins.log.info('InfinStor token has expired. Calling renew ' + str(token_time)\
                + ', ' + str(time_now))

        renew_token(tokfile, refresh_token, client_id, service)
        token, refresh_token, token_time, client_id, service = read_token_file(tokfile)
        builtins.idtoken = token
        builtins.refreshtoken = refresh_token
    else:
        if (verbose):
            builtins.log.info('InfinStor token has not expired ' + str(token_time) + ', ' + str(time_now))

def perform_infinstor_login(username, password):
    payload = "{\n"
    payload += "    \"AuthParameters\" : {\n"
    payload += "        \"USERNAME\" : \"" + username + "\",\n"
    payload += "        \"PASSWORD\" : \"" + password + "\"\n"
    payload += "    },\n"
    payload += "    \"AuthFlow\" : \"USER_PASSWORD_AUTH\",\n"
    payload += "    \"ClientId\" : \"" + builtins.clientid + "\"\n"
    payload += "}\n"

    url = 'https://cognito-idp.us-east-1.amazonaws.com:443/'

    headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
            }

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        builtins.log.error(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        builtins.log.error(f'Other error occurred: {err}')
        raise
    else:
        builtins.log.info('Authorization success!')
        challenge = response.json().get('ChallengeName')
        if challenge == "NEW_PASSWORD_REQUIRED":
            return response.json()
        else:
            authres = response.json()['AuthenticationResult']
            builtins.idtoken = authres['IdToken']
            builtins.refreshtoken = authres['RefreshToken']

    # Call cognito REST API getUser to get custom:serviceName
    url = 'https://cognito-idp.us-east-1.amazonaws.com:443/'
    body = dict()
    body['AccessToken'] = authres['AccessToken']
    body_s = json.dumps(body)
    headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target' : 'AWSCognitoIdentityProviderService.GetUser'
            }
    try:
        response = requests.post(url, data=body_s, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        builtins.log.error(f'HTTP error occurred in getUser: {http_err}')
        raise
    except Exception as err:
        builtins.log.error(f'Other error occurred in getUser: {err}')
        raise
    else:
        builtins.log.info('cognito getUser success')
        user = response.json()
        useratt = user['UserAttributes']
        for oneattr in useratt:
            if (oneattr['Name'] == 'custom:serviceName'):
                srvc = oneattr['Value']
                builtins.log.info('Found serviceName ' + srvc + ' in cognito user')
                if (srvc != builtins.service):
                    estr = 'Error. Service mismatch. cognito says service is '\
                            + str(srvc) + ', while user wants ' + str(builtins.service)
                    builtins.log.info(estr)
                    raise Exception('login', estr)
                break
    if (builtins.service == None):
        builtins.log.error('Could not determine service')
        raise Exception('login', 'Could not determine service')

    setup_token_for_mlflow()

    payload = ("ProductCode=" + builtins.prodcode)
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': builtins.idtoken
            }

    url = 'https://api.' + builtins.service + '/customerinfo'

    try:
        response = requests.post(url, data=payload+'&clientType=browser', headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        builtins.log.error(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        builtins.log.error(f'Other error occurred: {err}')
        raise
    else:
        builtins.log.info('customerinfo success!')
        return response.json()

def setup_token_for_mlflow():
    home = expanduser("~")
    if (home[len(home) - 1] == '/'):
        dotinfinstor = home + ".infinstor"
    else:
        dotinfinstor = home + separator + ".infinstor"
    builtins.log.info("Setting up token for mlflow in " + dotinfinstor)
    if (not os.path.exists(dotinfinstor)):
        try:
            os.mkdir(dotinfinstor, mode=0o755)
        except Exception as err:
            builtins.log.error('Error creating dir ' + dotinfinstor)
    tokfile = dotinfinstor + separator + "token"
    with open(tokfile, 'w') as wfile:
        wfile.write("Token=" + builtins.idtoken + "\n")
        wfile.write("RefreshToken=" + builtins.refreshtoken + "\n")
        wfile.write("ClientId=" + builtins.clientid + "\n")
        wfile.write("TokenTimeEpochSeconds=" + str(int(time.time())) + "\n")
        wfile.write("Service=" + builtins.service + "\n")
        wfile.close()

def check_for_custom_token():
    home = expanduser("~")
    if (home[len(home) - 1] == '/'):
        dotinfinstor = home + ".infinstor"
    else:
        dotinfinstor = home + separator + ".infinstor"
    builtins.log.info("Checking for custom token in " + dotinfinstor)
    if (not os.path.exists(dotinfinstor)):
        builtins.log.info('check_for_custom_token: dir ' + str(dotinfinstor)
                + ' does not exist. No custom token')
        return False
    tokfile = dotinfinstor + separator + "token"
    if (not os.path.exists(tokfile)):
        builtins.log.info('check_for_custom_token: file ' + str(tokfile)
                + ' does not exist. No custom token')
        return False
    ftoken, frefresh_token, ftoken_time, fclient_id, fservice = read_token_file(tokfile)
    if (ftoken and ftoken.startswith('Custom ')):
        builtins.idtoken = ftoken
        builtins.service = fservice
        builtins.log.info('check_for_custom_token: success. found custom token')
        return True
    else:
        return False

def get_customerinfo():
    payload = ("ProductCode=" + builtins.prodcode)
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': builtins.idtoken
            }

    url = 'https://api.' + builtins.service + '/customerinfo'

    try:
        response = requests.post(url, data=payload+'&clientType=browser', headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        builtins.log.error(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        builtins.log.error(f'Other error occurred: {err}')
        raise
    else:
        builtins.log.info('customerinfo success!')
        return response.json()

