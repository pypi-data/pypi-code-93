import os
import glob
import xml.etree.ElementTree as ET

from firstimpression.constants import APIS, TEMP_FOLDER, DUTCH_INDEX, LOCAL_INTEGRATED_FOLDER
from firstimpression.file import update_directories_api, check_too_old, download_install_media, write_root_to_xml_files
from firstimpression.time import parse_string_to_string, change_language
from firstimpression.scala import variables, Log
from firstimpression.text import remove_emoji
from firstimpression.api.request import request_json

##################################################################################################
# LOGGING
##################################################################################################

script = 'Facebook'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['facebook']

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DATETIME_FORMAT_NEW = '%d %B %Y'

URL = 'https://fi-api.io/facebook_post/'
BASE_URL_IMAGES = 'https://socials-bucket.s3.eu-central-1.amazonaws.com'

XML_FILENAME = 'facebook.xml'


##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################

def run_api(api_key, max_minutes, max_characters, max_items):
    debug.log('folder name: {}'.format(NAME))
    max_file_age = 60 * max_minutes
    xml_temp_path = os.path.join(TEMP_FOLDER, NAME, XML_FILENAME)
    
    debug.log('max_file_age: {} - temp path: {}'.format(max_file_age, xml_temp_path))

    headers = {
        'Authorization': 'Token {}'.format(api_key)
    }

    params = {
        'number_of_posts': max_items
    }

    update_directories_api(NAME)
    change_language(DUTCH_INDEX)

    if check_too_old(xml_temp_path, max_file_age):
        response_json = request_json(URL, headers, params, False)

        root = ET.Element("root")

        for post in response_json:
            item = ET.SubElement(root, "item")
            ET.SubElement(item, "likes").text = str(get_reactions(post)['likes'])
            ET.SubElement(item, "message").text = crop_message(remove_emoji(get_message(post)), max_characters)
            ET.SubElement(item, "created_time").text = parse_string_to_string(get_creation_date(post), DATETIME_FORMAT, DATETIME_FORMAT_NEW)

            thumbnail_url = get_image(post)
            if thumbnail_url is None:
                debug.log('image not found using placeholder')
                media_link = 'Content:\\placeholders\\img.png'
            else:
                debug.log(thumbnail_url)
                media_link = download_install_media(thumbnail_url, TEMP_FOLDER, NAME)
            
            ET.SubElement(item, "image").text = media_link

        write_root_to_xml_files(root, xml_temp_path, NAME)        
    else:
        debug.log('File not old enough to download new info')

def check_api(max_minutes):
    svars = variables()

    max_file_age = 60 * max_minutes

    debug.log('max_file_age: {}'.format(max_file_age))

    file_name = 'facebook*.xml'
    file_path = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, file_name)

    debug.log('local path: {}'.format(file_path))

    file_path = glob.glob(file_path)

    if len(file_path) > 0:
        file_path = file_path[0]
        debug.log('glob filepath: {}'.format(file_path))

        if check_too_old(file_path, max_file_age):
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

def get_image(post):
    return post.get('image', None)

def get_reactions(post):
    return post.get('reactions', {})

def get_message(post):
    return post.get('message', '')

def get_creation_date(post):
    creation_date = post.get('created_at', None)
    if creation_date is None:
        return None
    else:
        return creation_date[:19]

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################

def crop_message(text, max_length):
    if len(text) > max_length:
        return text[:max_length-3] + "...\nLees verder op Facebook"
    else:
        return text
