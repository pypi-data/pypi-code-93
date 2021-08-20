import json
import os
import random

from firstimpression.constants import APIS, LOCAL_INTEGRATED_FOLDER
from firstimpression.file import update_directories_api, check_too_old
from firstimpression.scala import variables, Log
from firstimpression.api.request import request_json

##################################################################################################
# LOGGING
##################################################################################################

script = 'Chuck Norris (Jokes)'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)

##################################################################################################
# CONSTANTS
##################################################################################################

PARAMS = {
    'firstName': 'firstname',
    'lastName': 'lastname',
    'exclude': ['explicit']
}

NAME = APIS['jokes']

JSON_FILENAME = 'jokes.json'
JSON_FILE_PATH = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, JSON_FILENAME)

URL = 'http://api.icndb.com/jokes/'

MAX_FILE_AGE = 60 * 60 * 24

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():
    debug.log('folder name: {}'.format(NAME))
    debug.log('file path: {}'.format(JSON_FILE_PATH))
    update_directories_api(NAME)

    if check_too_old(JSON_FILE_PATH, MAX_FILE_AGE):
        with open(JSON_FILE_PATH, 'w') as file:
            response = request_json(URL, params=PARAMS).get('value', None)
            if response is None:
                warn.log('response is empty')
            else:
                debug.log(response)
                json.dump(response, file)
    else:
        debug.log('File not old enough to update')


def check_api(firstname, lastname):
    svars = variables()

    if check_too_old(JSON_FILE_PATH, MAX_FILE_AGE):
        svars['skipscript'] = True
        debug.log('File to old to run chuck_norris')
    else:
        svars['skipscript'] = False
        svars['joke'] = get_random_joke(firstname, lastname)


##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


##################################################################################################
# GET FUNCTIONS
##################################################################################################

def get_random_joke(firstname, lastname):
    jokes = [elem['joke'] for elem in json.load(open(JSON_FILE_PATH, 'r'))]

    return random.SystemRandom().choice(jokes).replace(PARAMS['firstName'], firstname).replace(PARAMS['lastName'], lastname)

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################
