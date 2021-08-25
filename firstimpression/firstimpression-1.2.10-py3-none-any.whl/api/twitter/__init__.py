import xml.etree.ElementTree as ET
import os
import glob

from firstimpression.api.request import request_json
from firstimpression.constants import APIS, DUTCH_INDEX, LOCAL_INTEGRATED_FOLDER, TEMP_FOLDER
from firstimpression.file import check_too_old, download_install_media, update_directories_api, write_root_to_xml_files
from firstimpression.scala import variables, Log
from firstimpression.text import remove_emoji
from firstimpression.time import change_language, parse_string_to_string

##################################################################################################
# LOGGING
##################################################################################################

script = 'Twitter'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['twitter']

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
DATETIME_FORMAT_NEW = '%d %B %Y'

URL = 'https://fi-api.io/twitter_post/'

XML_FILENAME = 'twitter.xml'
XML_FILENAME_CONTENT = 'twitter*.xml'
XML_TEMP_PATH = os.path.join(TEMP_FOLDER, NAME, XML_FILENAME)
XML_LOCAL_PATH = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, XML_FILENAME_CONTENT)

MAX_FILE_AGE = 60 * 5

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################

def run_api(api_key, max_items):
    debug.log('folder name: {}'.format(NAME))
    debug.log('file path temp: {} - local: {}'.format(XML_TEMP_PATH, XML_LOCAL_PATH))

    headers = {
        'Authorization': 'Token {}'.format(api_key)
    }

    params = {
        'number_of_posts': max_items
    }

    update_directories_api(NAME)
    change_language(DUTCH_INDEX)

    if check_too_old(XML_TEMP_PATH, MAX_FILE_AGE):
        response_json = request_json(URL, headers, params, False)

        root = ET.Element("root")

        for post in response_json:
            root.append(parse_post(post))
        
        write_root_to_xml_files(root, XML_TEMP_PATH, NAME)
    else:
        debug.log('File not old enough to update')

def check_api():
    svars = variables()

    file_path = glob.glob(XML_LOCAL_PATH)

    if len(file_path) > 0:
        file_path = file_path[0]
        debug.log('glob filepath: {}'.format(file_path))

        if check_too_old(file_path, MAX_FILE_AGE):
            svars['skipscript'] = True
            info.log('file too old')
        else:
            svars['skipscript'] = False
    else:
        warn.log('File does not exists')
        svars['skipscript'] = True


##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


##################################################################################################
# GET FUNCTIONS
##################################################################################################

def get_likes(post):
    return post.get('likes', 0)

def get_message(post):
    return post.get('message', '')

def get_creation_date(post):
    return post.get('created_at', '')

def get_image(post):
    url = post.get('image', None)
    if url is None:
        debug.log('No image found using placeholder instead')
        return 'Content:\\placeholders\\img.png'
    else:
        return download_install_media(url, TEMP_FOLDER, NAME)


##################################################################################################
# PARSE FUNCTIONS
##################################################################################################

def parse_post(post):
    item = ET.Element("item")
    ET.SubElement(item, "likes").text = str(get_likes(post))
    ET.SubElement(item, "message").text = remove_emoji(get_message(post))
    ET.SubElement(item, "created_time").text = parse_string_to_string(get_creation_date(post), DATETIME_FORMAT, DATETIME_FORMAT_NEW)
    ET.SubElement(item, "image").text = get_image(post)
    return item