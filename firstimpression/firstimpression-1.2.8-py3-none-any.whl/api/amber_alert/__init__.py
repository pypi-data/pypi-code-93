import os
import glob
import xml.etree.ElementTree as ET

from firstimpression.constants import TEMP_FOLDER, APIS, LOCAL_INTEGRATED_FOLDER, NAMELEVEL
from firstimpression.file import download_install_media, update_directories_api, check_too_old, write_root_to_xml_files, xml_to_root
from firstimpression.xml import get_xml
from firstimpression.scala import Log, variables


##################################################################################################
# LOGGING
##################################################################################################

script = 'Amber Alert'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['amber']

XML_FILENAME = 'amber_alert.xml'
XML_FILENAME_CONTENT = 'amber_alert*.xml'

URL = 'https://media.amberalert.nl/xml/combined/index.xml'

XML_TEMP_PATH = os.path.join(TEMP_FOLDER, NAME, XML_FILENAME)
XML_LOCAL_PATH = os.path.join(
    LOCAL_INTEGRATED_FOLDER,
    NAME,
    XML_FILENAME_CONTENT
)

URL_LOGO = 'http://fimp.nl/narrowcasting/amberalert.png'

MAX_FILE_AGE = 60 * 10

NAMESPACE_XML = {
    'NP': 'http://www.netpresenter.com'
}

TAGS = {
    'alert': 'NP:Alert',
    'soort': 'NP:AlertLevel',
    'status': 'NP:Status',
    'type': 'NP:Type',
    'message': 'NP:Message/NP:Common/NP:ISource',
    'name': 'NP:Title',
    'description': 'NP:Description',
    'readmore': 'NP:Readmore_URL',
    'amberlink': 'NP:Media_URL',
    'image': 'NP:Media/NP:Image'
}

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():
    debug.log('folder name: {}'.format(NAME))
    debug.log(
        'File locations: temp -> {} & local -> {}'.format(XML_TEMP_PATH, XML_LOCAL_PATH))
    update_directories_api(NAME)

    if check_too_old(XML_TEMP_PATH, MAX_FILE_AGE):
        root = get_xml(URL)
        new_root = ET.Element("root")
        counter = 0

        download_install_logo()

        for alert in get_alerts(root):
            counter += 1
            new_root.append(parse_alert(alert))

        ET.SubElement(new_root, "alerts").text = str(counter)

        if counter == 0:
            info.log('No alerts to show')

        debug.log(new_root)

        write_root_to_xml_files(new_root, XML_TEMP_PATH, NAME)

    else:
        debug.log('File not old enough to update')


def check_api():
    svars = variables()
    file_path = glob.glob(XML_LOCAL_PATH)

    if len(file_path > 0):
        file_path = file_path[0]
        debug.log('glob filepath: {}'.format(file_path))

        if check_too_old(file_path, MAX_FILE_AGE):
            svars['skipscript'] = True
            debug.log('file too old')
        else:
            svars['skipscript'] = False

            amount_items = int(xml_to_root(file_path).get('alerts', '0'))

            svars['total_items'] = amount_items

            if amount_items == 0:
                svars['skipscript'] = True
                info.log('No alerts to show')
    else:
        warn.log('File does not exists')
        svars['skipscript'] = True

##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


def download_install_logo():
    download_install_media(URL_LOGO, TEMP_FOLDER, NAME)


def download_photo_child(url):
    return download_install_media(url, TEMP_FOLDER, NAME)

##################################################################################################
# GET FUNCTIONS
##################################################################################################


def get_alerts(root):
    return root.findall(TAGS['alert'], NAMESPACE_XML)


def get_alert_soort(alert):
    if alert.findtext(TAGS['soort'], '0', NAMESPACE_XML) == '10':
        return 'Amber Alert'
    else:
        return 'Vermist kind'


def get_alert_status(alert):
    return alert.findtext(TAGS['status'], 'Onbekend', NAMESPACE_XML)


def get_alert_type(alert):
    return alert.findtext(TAGS['type'], 'Onbekend', NAMESPACE_XML)


def get_alert_message(alert):
    return alert.find(TAGS['message'], NAMESPACE_XML)


def get_name_child(message):
    return message.findtext(TAGS['name'], 'Onbekend', NAMESPACE_XML)


def get_message_description(message):
    return message.findtext(TAGS['description'], '', NAMESPACE_XML)


def get_more_info_url(message):
    return message.findtext(TAGS['readmore'], '', NAMESPACE_XML)


def get_amber_url(message):
    return message.findtext(TAGS['amberlink'], '', NAMESPACE_XML)


def get_photo_child(message):
    media_url = message.findtext(TAGS['image'], None, NAMESPACE_XML)

    if media_url is None:
        return 'Content:\\placeholders\\img.png'
    else:
        return download_photo_child(media_url)

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################


def parse_alert(alert):
    item = ET.Element("item")
    ET.SubElement(item, "soort").text = get_alert_soort(alert)
    ET.SubElement(item, "status").text = get_alert_status(alert)
    ET.SubElement(item, "type").text = get_alert_type(alert)

    message = get_alert_message(alert)

    ET.SubElement(item, "naam").text = get_name_child(message)
    ET.SubElement(item, "description").text = get_message_description(message)
    ET.SubElement(item, "readmore").text = get_more_info_url(message)
    ET.SubElement(item, "amberlink").text = get_amber_url(message)
    ET.SubElement(item, "image").text = get_photo_child(message)

    return item