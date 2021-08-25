import xml.etree.ElementTree as ET
import glob
import os

from geopy import distance

from firstimpression.constants import APIS, LOCAL_INTEGRATED_FOLDER, TEMP_FOLDER
from firstimpression.file import update_directories_api, write_root_to_xml_files, check_too_old, xml_to_root
from firstimpression.json import lst_dict_to_root
from firstimpression.scala import variables, Log
from firstimpression.api.request import request_json

##################################################################################################
# LOGGING
##################################################################################################

script = 'Traffic'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)


##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['traffic']

EXCLUDE_FROM_XML = 'coordinates'

XML_FILE_NAME_LONGEST = 'longest_jams.xml'
XML_TEMP_PATH_LONGEST = os.path.join(TEMP_FOLDER, NAME, XML_FILE_NAME_LONGEST)
XML_FILE_NAME_CLOSEST = 'closest_jams.xml'
XML_TEMP_PATH_CLOSEST = os.path.join(TEMP_FOLDER, NAME, XML_FILE_NAME_CLOSEST)

XML_LOCAL_LONGEST = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, 'longest_jams*.xml')
XML_LOCAL_CLOSEST = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, 'closest_jams*.xml')

MAX_FILE_AGE = 60 * 10

URL = 'https://api.rwsverkeersinfo.nl/api/traffic'

PARAMS = {
    'query_type': 'overview'
}

HEADERS = {
    'cache-control':'no-cache',
    'Accept': 'application/json'
}

TAGS = {
    'circumstances': 'obstructions'
}

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################

def run_api(jam_type, max_closest, max_longest, own_coordinates, only_highways):
    debug.log('folder name: {}'.format(NAME))
    debug.log('file paths - temp long: {} - local long: {} - temp close: {} - local close: {}'.format(XML_TEMP_PATH_LONGEST, XML_LOCAL_LONGEST, XML_TEMP_PATH_CLOSEST, XML_LOCAL_CLOSEST))
    debug.log('max_close: {} - max_long: {}'.format(max_closest, max_longest))

    update_directories_api(NAME)

    if (check_too_old(XML_TEMP_PATH_LONGEST, MAX_FILE_AGE) and max_longest > 0) or (check_too_old(XML_TEMP_PATH_CLOSEST, MAX_FILE_AGE) and max_closest > 0):
        traffic_info = request_json(URL, HEADERS, PARAMS)

        circumstances = parse_circumstances(get_circumstances(traffic_info), own_coordinates, only_highways)
        jams = get_jams(circumstances, jam_type)

        if check_too_old(XML_TEMP_PATH_LONGEST, MAX_FILE_AGE) and max_longest > 0:
            sorted_jams = sort_longest_jams(jams)
            sorted_jams = [{key: value for key, value in d.items() if key != EXCLUDE_FROM_XML} for d in sorted_jams]
            root = lst_dict_to_root(sorted_jams[:max_longest])

            ET.SubElement(root, "total_circumstances").text = str(get_total_jams(jams))
            ET.SubElement(root, "total_circumstances_string").text = get_total_jams_str(jams)
            ET.SubElement(root, "total_length").text = str(get_total_jam_length(traffic_info))
            ET.SubElement(root, "total_length_string").text = get_total_length_string(traffic_info)
            ET.SubElement(root, "total_delay_string").text = calculate_total_delay_str(jams)

            write_root_to_xml_files(root, XML_TEMP_PATH_LONGEST, NAME)
        else:
            debug.log('Longest xml does not need to be updated')

        if check_too_old(XML_TEMP_PATH_CLOSEST, MAX_FILE_AGE) and max_closest > 0:
            sorted_jams = sort_closest_jams(jams)
            sorted_jams = [{key: value for key, value in d.items() if key != EXCLUDE_FROM_XML} for d in sorted_jams]
            root = lst_dict_to_root(sorted_jams[:max_closest])

            ET.SubElement(root, "total_circumstances").text = str(get_total_jams(jams))
            ET.SubElement(root, "total_circumstances_string").text = get_total_jams_str(jams)
            ET.SubElement(root, "total_length").text = str(get_total_jam_length(traffic_info))
            ET.SubElement(root, "total_length_string").text = get_total_length_string(traffic_info)
            ET.SubElement(root, "total_delay_string").text = calculate_total_delay_str(jams)

            write_root_to_xml_files(root, XML_TEMP_PATH_CLOSEST, NAME)
        else:
            debug.log('Closest xml does not need to be updated')
    else:
        debug.log('Files are not updated')

def check_api():
    svars = variables()
    skip = False

    file_path_longest = glob.glob(XML_LOCAL_LONGEST)
    file_path_closest = glob.glob(XML_LOCAL_CLOSEST)

    if len(file_path_longest) > 0:
        file_path_longest = file_path_longest[0]
        debug.log('glob filepath: {}'.format(file_path_longest))

        if check_too_old(file_path_longest, MAX_FILE_AGE):
            skip = True
            info.log('file {} too old'.format(file_path_longest))
        else:
            if xml_to_root(file_path_longest).findtext('total_circumstances', 0) == 0:
                skip == True
                info.log('no traffic jams at the moment')
    else:
        warn.log('File {} does not exists'.format(file_path_longest))

    if len(file_path_closest) > 0:
        file_path_closest = file_path_closest[0]
        debug.log('glob filepath: {}'.format(file_path_closest))

        if check_too_old(file_path_closest, MAX_FILE_AGE):
            skip = True
            info.log('file {} too old'.format(file_path_closest))
        else:
            if xml_to_root(file_path_closest).findtext('total_circumstances', 0) == 0:
                skip == True
                info.log('no traffic jams at the moment')
    else:
        warn.log('File {} does not exists'.format(file_path_closest))
            
    svars['skipscript'] = skip

##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


##################################################################################################
# GET FUNCTIONS
##################################################################################################

def get_circumstances(traffic_info):
    return traffic_info.get(TAGS['circumstances'], {})


def get_reason(circumstance):
    return circumstance.get('cause', '')


def get_area_detail(circumstance):
    return circumstance.get('locationText', '')


def get_event(circumstance):
    return circumstance.get('title', '')


def get_description(circumstance):
    return circumstance.get('description', '')


def get_type(circumstance):
    return circumstance.get('obstructionType', 0)

def get_direction_text(circumstance):
    return circumstance.get('directionText', None)


def get_from(circumstance):
    text = get_direction_text(circumstance)
    if text is None:
        return ''
    else:
        return text.split(' - ')[0]


def get_to(circumstance):
    text = get_direction_text(circumstance)
    if text is None:
        return ''
    else:
        return text.split(' - ')[1]

def get_total_jams(jams):
    return len(jams)

def get_total_jams_str(jams):
    total = get_total_jams(jams)

    temp = '{} file'.format(total)

    if total != 1:
        temp += 's'
    
    return temp

def get_road_type(circumstance):
    road = get_road(circumstance)

    if road is None:
        return ''
    else:
        return road[0]


def get_road(circumstance):
    return circumstance.get('roadNumber', None)


def get_road_number(circumstance):
    road = get_road(circumstance)

    if road is None:
        return ''
    else:
        return road[1:]


def get_length(circumstance):
    total_length = circumstance.get('total_length', None)
    if total_length is None:
        return ''
    else:
        return int(total_length)


def get_length_string(circumstance):
    length = get_length(circumstance)
    if length != '':
        return '{} km'.format(length/1000)
    else:
        return 'onbekend'

def get_delay(circumstance):
    total_length = circumstance.get('delay', None)

    if total_length is None:
        return ''
    else:
        return int(total_length)

def get_delay_string(circumstance):
    delay = get_delay(circumstance)

    if delay is None:
        return ''
    else:
        return '+{} min'.format(delay)

def get_jams(circumstances, jam_type):
    jams = list()
    for circumstance in circumstances:
        if circumstance.get('type', 1) == jam_type:
            jams.append(circumstance)
    return jams

def get_longitude(circumstance):
    return circumstance.get('longitude', '')

def get_latitude(circumstance):
    return circumstance.get('latitude', '')

def get_coordinates(circumstance):
    return {'longitude': get_longitude(circumstance), 'latitude': get_latitude(circumstance)}


def get_total_jam_length(traffic_info):
    return traffic_info.get('totalLengthOfJams', 0) / 1000


def get_total_length_string(traffic_info):
    return '{} km'.format(get_total_jam_length(traffic_info))

def get_only_highways(parsed_circumstances):
    specific_circumstances = list()
    for circumstance in parsed_circumstances:
        if circumstance['road_type'] == 'A':
            specific_circumstances.append(circumstance)
    return specific_circumstances


##################################################################################################
# PARSE FUNCTIONS
##################################################################################################


def parse_circumstances(circumstances, own_coordinates, only_highways):
    parsed_circumstances = list()
    for circumstance in circumstances:
        parsed_circumstances.append(
            parse_circumstance(circumstance, own_coordinates))

    if only_highways:
        return get_only_highways(parsed_circumstances)
    else:
        return parsed_circumstances


def parse_circumstance(circumstance, own_coordinates):
    # Parses JSON from API to own format. Junk data is removed.
    parsed_circumstance = dict()

    parsed_circumstance['road_type'] = get_road_type(circumstance)
    parsed_circumstance['road'] = get_road(circumstance)
    parsed_circumstance['road_number'] = get_road_number(circumstance)
    parsed_circumstance['from'] = get_from(circumstance)
    parsed_circumstance['to'] = get_to(circumstance)
    parsed_circumstance['length'] = get_length(circumstance)
    parsed_circumstance['length_string'] = ''
    parsed_circumstance['reason'] = get_reason(circumstance)
    parsed_circumstance['area_detail'] = get_area_detail(circumstance)
    parsed_circumstance['event'] = get_event(circumstance)
    parsed_circumstance['description'] = get_description(circumstance)
    parsed_circumstance['type'] = get_type(circumstance)
    parsed_circumstance['total_delay'] = get_delay_string(circumstance)
    parsed_circumstance['coordinates'] = get_coordinates(circumstance)

    parsed_circumstance['distance_to_circumstance'] = calculate_distance_to_circumstance(
        own_coordinates, parsed_circumstance['coordinates'])

    return parsed_circumstance

def sort_longest_jams(jams):
    # Sorts longest jams starting with longest to shortest
    return sorted(jams, key=lambda i: i['length'], reverse=True)


def sort_closest_jams(jams):
    # Sorts jams that are closest to own location
    return sorted(jams, key=lambda i: i['distance_to_circumstance'])


def calculate_distance_to_circumstance(from_coordinates, to_coordinates):
    # Calculates distance from one coordinate to another (WATCH OUT: straight line, so no roads taken into account)
    if not from_coordinates or not to_coordinates:
        return ''

    coords_1 = (from_coordinates['latitude'], from_coordinates['longitude'])
    coords_2 = (to_coordinates['latitude'], to_coordinates['longitude'])

    return distance.distance(coords_1, coords_2).km


def calculate_total_delay_str(jams):
    total_delay = 0
    for jam in jams:
        delay = jam.get('total_delay', '')
        if delay == '':
            continue
        else:
            total_delay += int(delay.split(' ').pop(0))

    if total_delay > 60:
        return '{}+ uur'.format(int(total_delay / 60))
    else:
        return '{} min'.format(int(total_delay))
