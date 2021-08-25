import json
import glob
import os

from firstimpression.constants import APIS, TEMP_FOLDER, LOCAL_INTEGRATED_FOLDER
from firstimpression.file import update_directories_api, write_root_to_xml_files, check_too_old
from firstimpression.time import parse_string_to_date, parse_string_time_to_minutes, parse_date_to_string, parse_string_to_string
from firstimpression.json import lst_dict_to_root
from firstimpression.scala import variables, Log
from firstimpression.api.request import request_json

##################################################################################################
# LOGGING
##################################################################################################

script = 'NS'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['ns']

LANGUAGE = 'nl'

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

URL_STATIONS = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/stations'
URL_DEPARTURES = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/departures'

MAX_FILE_AGE_DEPARTURES = 60 * 3
MAX_FILE_AGE_STATIONS = 60 * 60 * 24 * 60

STATIONS_JSON_FILENAME = 'stations.json'
STATIONS_JSON_PATH = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, STATIONS_JSON_FILENAME)


##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################

def run_api(api_key, station, max_journeys):
    
    debug.log('folder name: {}'.format(NAME))

    xml_temp_path = os.path.join(TEMP_FOLDER, NAME, 'departures_{}.xml'.format(station))
    
    debug.log('temp path: {}'.format(xml_temp_path))

    params = {
        'maxJourneys': str(max_journeys),
        'lang': LANGUAGE,
        'station': station
    }

    headers = {
        'Ocp-Apim-Subscription-Key': api_key
    }

    update_directories_api(NAME)

    if check_too_old(STATIONS_JSON_PATH, MAX_FILE_AGE_STATIONS):
        with open(STATIONS_JSON_PATH, 'w') as file:
            json.dump(request_json(URL_STATIONS, headers), file)
    else:
        debug.log('Stations JSON not old enough to update')

    if check_too_old(xml_temp_path, MAX_FILE_AGE_DEPARTURES):
        write_root_to_xml_files(lst_dict_to_root(get_parsed_departures(get_response(URL_DEPARTURES, headers, params), DATETIME_FORMAT)), xml_temp_path, NAME)
    else:
        debug.log('Departures file is not old enough to update')

def check_api(station):
    stations = json.load(open(STATIONS_JSON_PATH, 'r'))
    svars = variables()

    debug.log('station: {}'.format(station))

    for stat in stations.get('payload', {}):
        if stat.get('code', None) == station:
            svars['station_name'] = stat.get('namen', {}).get('lang', 'Onbekend')
            break
    
    file_path = glob.glob(os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, 'departures_{}*.xml'.format(station)))
    
    if len(file_path) > 0:
        file_path = file_path[0]
        debug.log('glob filepath: {}'.format(file_path))

        if check_too_old(file_path, MAX_FILE_AGE_DEPARTURES):
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

def get_response(url, headers, params):
    response_json = request_json(url, headers, params)

    if response_json.get('statusCode', None) == 429:
        error.log('Rate limit exceeded')
        raise Exception('Rate limit exceeded')

    return response_json


def get_departures(response_json):
    return response_json.get('payload',{}).get('departures', '')


def get_departure_time(departure):
    time = departure.get('plannedDateTime', None)
    if time is None:
        return ''
    else:
        return time[:-5]


def get_actual_departure_time(departure):
    time = departure.get('actualDateTime', None)
    if time is None:
        return ''
    else:
        return time[:-5]


def get_departure_number(departure):
    return departure.get('product', {}).get('number', '')


def get_destination(departure):
    return departure.get('direction', '')


def get_train_category(departure):
    return departure.get('product', {}).get('longCategoryName', '')


def get_route_text(departure):
    # Returns string with stations on route in this format: '{station}, {station}, {station}'
    return ', '.join([station.get('mediumName', 'station') for station in departure.get('routeStations', {})])


def get_operator(departure):
    return departure.get('product', {}).get('operatorName', '')


def get_planned_track(departure):
    if get_actual_track(departure) == '':
        return departure.get('plannedTrack', '')
    else:
        return get_actual_track(departure)


def get_actual_track(departure):
    return departure.get('actualTrack', '')


def get_delay(departure, date_format):
    try:
        if departure.get('cancelled', False) == True:
            return 'Rijdt niet'
    except KeyError:
        pass

    planned_departure_time = parse_string_to_date(get_departure_time(departure), date_format)
    actual_departure_time = parse_string_to_date(get_actual_departure_time(departure), date_format)

    if planned_departure_time < actual_departure_time:
        delayed_time = actual_departure_time - planned_departure_time
        delayed_minutes = parse_string_time_to_minutes(str(delayed_time))
        return ''.join(['+', str(delayed_minutes), ' min'])
    else:
        return ''


def get_message(departure):
    try:
        message = departure.get('messages', False)
        if message:
            msg = message[0].get('message', '')
        else:
            msg = ''
    except KeyError:
        msg = ''
    return msg

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################

def get_parsed_departures(response_json, date_format):
    departures = get_departures(response_json)
    parsed_departures = list()
    for departure in departures:
        parsed_departure = dict()
        parsed_departure['departure_number'] = get_departure_number(departure)
        parsed_departure['departure_time'] = parse_string_to_string(get_departure_time(departure), date_format, '%H:%M')
        parsed_departure['destination'] = get_destination(departure)
        parsed_departure['train_category'] = get_train_category(departure)
        parsed_departure['route_text'] = get_route_text(departure)
        parsed_departure['operator'] = get_operator(departure)
        parsed_departure['planned_track'] = get_planned_track(departure)
        parsed_departure['delay'] = get_delay(departure, date_format)
        parsed_departure['message'] = get_message(departure)
        parsed_departures.append(parsed_departure)

    return parsed_departures
