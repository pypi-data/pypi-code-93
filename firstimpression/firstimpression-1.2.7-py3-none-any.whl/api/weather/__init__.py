import xml.etree.ElementTree as ET
import glob
import os

from firstimpression.constants import APIS, TEMP_FOLDER, LOCAL_INTEGRATED_FOLDER, IMG_EXTENSIONS, VIDEO_EXTENSIONS, DUTCH_INDEX
from firstimpression.file import create_directories, write_root_to_xml_files, update_directories_api, check_too_old, list_files, download_install_media
from firstimpression.time import change_language, parse_date_to_string, parse_timestamp_to_date
from firstimpression.scala import variables, Log
from firstimpression.api.request import request_json

##################################################################################################
# LOGGING
##################################################################################################

script = 'Weather'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['weather']

XML_TEMP_PATH = os.path.join(TEMP_FOLDER, NAME, 'weather.xml')
XML_LOCAL_PATH = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, 'weather*.xml')

MAX_FILE_AGE = 60 * 60
MAX_FILE_AGE_IMAGES = 60 * 60 * 24

URL_TODAY = 'http://api.openweathermap.org/data/2.5/weather'
URL_DAYS = 'http://api.openweathermap.org/data/2.5/forecast/daily'

TEMPERATURE_DECIMALS = 1

#http://openweathermap.org/weather-conditions
VIDEOS = {
    'wvideo_cloudy': {803, 804},
    'wvideo_fog': {701, 711, 721, 731, 741, 751, 761, 762, 771, 781},
    'wvideo_pcloudy': {801, 802},
    'wvideo_rain': {300, 301, 302, 310, 311, 312, 313, 314, 321, 500, 501, 502, 503, 504, 511, 520, 521, 522, 531},
    'wvideo_snow': {600, 601, 602, 611, 612, 615, 616, 620, 621, 622},
    'wvideo_sunny': {800},
    'wvideo_tstorms': {200, 201, 202, 210, 211, 212, 221, 230, 231, 232},
    'wvideo_extreme': {900, 901, 902, 903, 904, 905, 906},
    'wvideo_additional': {951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962}
}
#icons
ICONS = {
    "01": {800, 951},
    "02": {801, 802},
    "03": {803, 804},
    "04": {301, 302, 311, 312},
    "05": {300, 310},
    "06": {313, 314, 321},
    "07": {500, 501},
    "08": {906, 511},
    "09": {},
    "10": {502, 503, 504, 521, 522, 531},
    "11": {520},
    "12": {201, 202, 211, 212, 221, 231, 232},
    "13": {200, 210, 230},
    "14": {602, 611, 612, 616, 621},
    "15": {600, 601, 615, 620},
    "16": {900, 901, 902, 905, 954, 955, 956, 957, 958, 959, 960, 961, 962},
    "17": {952, 953},
    "18": {622},
    "19": {701, 711, 721, 731, 741, 751, 761, 762, 771, 781},
    "unknown": {903, 904}
}

TAGS = {
    'location': 'name',
    'clouds': 'clouds',
    'clouds_%': 'all',
    'rain': 'rain',
    '3hours': '3h',
    'snow': 'snow',
    'wind': 'wind',
    'wind_speed': 'speed',
    'wind_angle': 'deg',
    'info': 'main',
    'humidity': 'humidity',
    'pressure': 'pressure',
    'max_temp': 'temp_max',
    'min_temp': 'temp_min',
    'current_temp': 'temp',
    'weather': 'weather',
    'status': 'main',
    'description': 'description',
    'id': 'id',
    'icon': 'icon',
    'days': 'list',
    'date': 'dt',
    'temp': 'temp',
    'temp_max': 'max',
    'temp_min': 'min'
}

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################

def run_api(api_key, icon_set, location='', units='metric', lang='nl', coordinates=None):
    params = {
        'q': location,
        'appid': api_key, 
        'units': units,
        'lang': lang
    }

    if not coordinates is None:
        del params['q']
        params['lon'] = coordinates['longitude']
        params['lat'] = coordinates['latitude']

    url_icons = 'http://37.97.211.104/narrowcasting/weather/weather_{}'.format(icon_set)

    extensions = IMG_EXTENSIONS + VIDEO_EXTENSIONS
    
    temp_folder_icons = os.path.join(TEMP_FOLDER, NAME, 'icons', icon_set)
    local_folder_icons = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, 'icons', icon_set)

    debug.log('folder name: {}'.format(NAME))
    debug.log('params: {} - url icons: {} - extensions: {}'.format(params, url_icons, extensions))
    debug.log('folder icons temp: {} - local: {}'.format(temp_folder_icons, local_folder_icons))

    create_directories([temp_folder_icons, local_folder_icons])
    update_directories_api(NAME)
    change_language(DUTCH_INDEX)

    if check_too_old(XML_TEMP_PATH, MAX_FILE_AGE):

        download_icons(url_icons, extensions, temp_folder_icons, icon_set)
        
        root = ET.Element("root")

        current_weather = request_json(URL_TODAY, params=params)

        item = ET.SubElement(root, 'currentWeather')
        ET.SubElement(item, "location").text = get_location(current_weather)
        ET.SubElement(item, "clouds").text = get_clouds(current_weather)
        ET.SubElement(item, "rain").text = get_rain(current_weather)
        ET.SubElement(item, "snow").text = get_snow(current_weather)
        ET.SubElement(item, "wind_speed").text = get_wind_speed(current_weather)
        ET.SubElement(item, "wind_deg").text = get_wind_angle(current_weather)
        ET.SubElement(item, "humidity").text = get_humidity(current_weather)
        ET.SubElement(item, "pressure_press").text = get_pressure(current_weather)
        ET.SubElement(item, "temperature_max").text = get_max_temperature(current_weather)
        ET.SubElement(item, "temperature_min").text = get_min_temperature(current_weather)
        ET.SubElement(item, "temperature_current").text = get_current_temperature(current_weather)
        ET.SubElement(item, "status").text = get_status(current_weather)
        ET.SubElement(item, "detailed_status").text = get_detailed_status(current_weather)
        ET.SubElement(item, "code").text = str(get_code(current_weather))
        ET.SubElement(item, "day").text = get_isday(current_weather)
        ET.SubElement(item, "video").text = get_video(current_weather, icon_set)
        ET.SubElement(item, "icon").text = get_icon(current_weather, icon_set)

        params['cnt'] = 6

        days_weather = request_json(URL_DAYS, params=params)

        days = ET.SubElement(root, "days")

        for day in get_days(days_weather):
            item = ET.SubElement(days, "day")
            ET.SubElement(item, "date").text = get_date_formated(day)
            ET.SubElement(item, "weekday").text = get_weekday(day)
            ET.SubElement(item, "detailed_status").text = get_detailed_status(day)
            ET.SubElement(item, "rain").text = get_rain(day)
            ET.SubElement(item, "snow").text = get_snow(day)
            ET.SubElement(item, "temperature_max").text = get_max_temperature(day)
            ET.SubElement(item, "temperature_min").text = get_min_temperature(day)
            ET.SubElement(item, "video").text = get_video(day, icon_set)
            ET.SubElement(item, "icon").text = get_icon(day, icon_set)

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

def download_icons(url_icons, extensions, temp_folder_icons, icon_set):
    icons = list_files(url_icons, extensions)

    for icon in icons:
        debug.log('icon: {}'.format(icon))
        if check_too_old(os.path.join(temp_folder_icons, icon), MAX_FILE_AGE_IMAGES):
            download_install_media(url_icons + '/{}'.format(icon), TEMP_FOLDER, '{}\\icons\\{}'.format(NAME, icon_set))


##################################################################################################
# GET FUNCTIONS
##################################################################################################

def get_location(current_weather):
    return current_weather.get(TAGS['location'], '')

def get_clouds(current_weather):
    percentage = current_weather.get(TAGS['clouds'], {}).get(TAGS['clouds_%'], '?')
    return '{}%'.format(percentage)

def get_rain(weather):
    rain = weather.get(TAGS['rain'], 0)

    if rain == 0:
        return '0 mm'
    elif isinstance(rain, dict):
        return '{} mm'.format(rain.get(TAGS['3hours'], 0))
    else:
        return '{} mm'.format(rain)

def get_snow(weather):
    snow = weather.get(TAGS['snow'], 0)

    if snow == 0:
        return '0 mm'
    elif isinstance(snow, dict):
        return '{} mm'.format(snow.get(TAGS['3hours'], '0'))
    else:
        return '{} mm'.format(snow)

def get_wind(current_weather):
    return current_weather.get(TAGS['wind'], {})

def get_wind_speed(current_weather):
    wind = get_wind(current_weather)
    return '{} m/s'.format(wind.get(TAGS['wind_speed'], '?'))

def get_wind_angle(current_weather):
    wind = get_wind(current_weather)
    return '{}'.format(wind.get(TAGS['wind_angle'], '?'))

def get_weather_info(current_weather):
    return current_weather.get(TAGS['info'], {})

def get_humidity(current_weather):
    info = get_weather_info(current_weather)
    return '{}%'.format(info.get(TAGS['humidity'], '?'))

def get_pressure(current_weather):
    info = get_weather_info(current_weather)
    return '{} hpa'.format(info.get(TAGS['pressure'], '?'))

def get_temperature(day):
    return day.get(TAGS['temp'], {})


def get_max_temperature(weather):
    info = get_weather_info(weather)

    if not bool(info):
        #if the info is empty
        temp = get_temperature(weather)
        return '{}'.format(round_temperature(temp.get(TAGS['temp_max'], '?')))
    else:
        return '{}'.format(round_temperature(info.get(TAGS['max_temp'], '?')))
        

def get_min_temperature(weather):
    info = get_weather_info(weather)

    if not bool(info):
        #if the info is empty
        temp = get_temperature(weather)
        return '{}'.format(round_temperature(temp.get(TAGS['temp_min'], '?')))
    else:
        return '{}'.format(round_temperature(info.get(TAGS['min_temp'], '?')))

def get_current_temperature(current_weather):
    info = get_weather_info(current_weather)
    return '{}'.format(round_temperature(info.get(TAGS['current_temp'], '?')))

def get_weather(current_weather):
    return current_weather.get(TAGS['weather'], [{}])[0]

def get_status(current_weather):
    weather = get_weather(current_weather)
    return weather.get(TAGS['status'], '')

def get_detailed_status(weather_):
    weather = get_weather(weather_)
    return weather.get(TAGS['description'], '')

def get_code(weather_):
    weather = get_weather(weather_)
    return weather.get(TAGS['id'], 0)

def get_icon_name(weather_):
    weather = get_weather(weather_)
    return weather.get(TAGS['icon'], '')

def get_isday(weather):
    icon_name = get_icon_name(weather)
    if 'd' in icon_name:
        return 'True'
    elif 'n' in icon_name:
        return 'False'
    else:
        return 'True'

def get_day_letter(weather):
    if get_isday(weather) == 'True':
        return 'd'
    else:
        return 'n'

    
def get_video(weather, icon_set):
    code = get_code(weather)
    letter = get_day_letter(weather)

    if code == 0:
        return 'Content:\\placeholders\\video.png'
    else:
        for key,value in VIDEOS.items():
            if code in value:
                return 'Content:\\{}\\icons\\{}\\{}{}.mp4'.format(NAME, icon_set, key, letter)

def get_icon(weather, icon_set):
    code = get_code(weather)
    letter = get_day_letter(weather)

    if code == 0:
        return 'Content:\\placeholders\\img.png'
    else:
        for key,value in ICONS.items():
            if code in value:
                return 'Content:\\{}\\icons\\{}\\{}{}.png'.format(NAME, icon_set, key, letter)

def get_days(days_weather):
    return days_weather.get(TAGS['days'], [])

def get_date(day):
    return parse_timestamp_to_date(day.get(TAGS['date'], 0))

def get_date_formated(day):
    return parse_date_to_string(get_date(day), '%d-%b-%Y')

def get_weekday(day):
    return parse_date_to_string(get_date(day), '%A')


##################################################################################################
# PARSE FUNCTIONS
##################################################################################################

def round_temperature(temp):
    if isinstance(temp, str):
        return temp
    else:
        return round(temp, TEMPERATURE_DECIMALS)
