import glob
import os
import xml.etree.ElementTree as ET

from firstimpression.constants import APIS, TEMP_FOLDER, LOCAL_INTEGRATED_FOLDER, DUTCH_INDEX
from firstimpression.file import update_directories_api, check_too_old, write_root_to_xml_files, download_install_media
from firstimpression.time import change_language, parse_string_to_string
from firstimpression.scala import variables, Log
from firstimpression.api.request import request

##################################################################################################
# LOGGING
##################################################################################################

script = 'Songkick'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['concerts']

MAX_FILE_AGE = 60 * 30

DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT_NEW = '%a %d %b'
TIME_FORMAT = '%H:%M:%S'
TIME_FORMAT_NEW = '%H:%M'

TAGS = {
    'event': 'results/event',
    'name': 'displayName',
    'type': 'type',
    'age_restriction': 'ageRestriction',
    'start_date': 'start',
    'date': 'date',
    'time': 'time',
    'performance': 'performance/artist',
    'id': 'id',
    'venue': 'venue',
    'location': 'location',
    'city': 'city'
}

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################

def run_api(api_key, area, max_items):
    debug.log('folder name: {}'.format(NAME))
    url = 'http://api.songkick.com/api/3.0/metro_areas/{}/calendar.xml'.format(area)

    params = {
        'apikey': api_key
    }

    xml_temp_path = os.path.join(TEMP_FOLDER, NAME, '{}.xml'.format(area))

    debug.log('url: {} - temp path: {}'.format(url, xml_temp_path))

    update_directories_api(NAME)
    change_language(DUTCH_INDEX)

    if check_too_old(xml_temp_path, MAX_FILE_AGE):
        response = request(url, params=params)
        root = ET.fromstring(response.content)
        new_root = ET.Element("root")

        for event in root.findall(TAGS['event']):
            item = ET.SubElement(new_root, "event")
            ET.SubElement(item, "name").text = get_name(event)
            ET.SubElement(item, "type").text = get_type(event)
            ET.SubElement(item, "age_restriction").text = get_age_restriction(event)
            ET.SubElement(item, "date").text = parse_string_to_string(get_date(event), DATE_FORMAT, DATE_FORMAT_NEW)
            ET.SubElement(item, "time").text = parse_string_to_string(get_time(event), TIME_FORMAT, TIME_FORMAT_NEW)
            ET.SubElement(item, "performers").text = get_performers(event)
            ET.SubElement(item, "photo").text = get_photo(event)
            ET.SubElement(item, "venue").text = get_venue(event)
            ET.SubElement(item, "location").text = get_location(event)

            if len(new_root) == max_items:
                debug.log('max amount of items breaking')
                break
        
        write_root_to_xml_files(new_root, xml_temp_path, NAME)
    else:
        debug.log('File not old enough to update')

def check_api(area):
    svars = variables()

    file_path = glob.glob(os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, '{}*.xml'.format(area)))

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

def get_photo(event):
    performance = get_performances(event)[0]

    artist_id = get_artist_id(performance)
    link = 'http://images.sk-static.com/images/media/profile_images/artists/{}/large_avatar'.format(artist_id)
    media_link = download_install_media(link, TEMP_FOLDER, NAME, '{}.jpg'.format(artist_id))

    if media_link is None:
        debug.log('No image found using placeholder instead')
        return 'Content:\\placeholders\\img.png'
    else:
        return media_link

##################################################################################################
# GET FUNCTIONS
##################################################################################################

def get_name(event):
    return event.get(TAGS['name'], '')

def get_type(event):
    return event.get(TAGS['type'], '')

def get_age_restriction(event):
    return event.get(TAGS['age_restriction'], '')

def get_start_date(event):
    return event.find(TAGS['start_date'])

def get_date(event):
    start_date = get_start_date(event)

    if not start_date is None:
        return start_date.get(TAGS['date'], '')
    else:
        return ''

def get_time(event):
    start_date = get_start_date(event)

    if not start_date is None:
        return start_date.get(TAGS['time'], '')
    else:
        return ''

def get_performances(event):
    return event.findall(TAGS['performance'])

def get_artist_id(performance):
    return performance.get(TAGS['id'], None)

def get_artist_name(performance):
    return performance.get(TAGS['name'], None)

def get_performers(event):
    performances = get_performances(event)
    performers = list()

    for performance in performances:
        artist_id = get_artist_id(performance)

        if not artist_id is None:
            performers.append(get_artist_name(performance))
    
    return ' + '.join(performers)

def get_venue(event):
    return event.find(TAGS['venue']).get(TAGS['name'], '')

def get_location(event):
    return event.find(TAGS['location']).get(TAGS['city'], '').split(',').pop(0)

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################
