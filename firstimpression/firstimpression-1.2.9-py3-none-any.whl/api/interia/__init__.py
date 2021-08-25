import xml.etree.ElementTree as ET
import os
import glob

from firstimpression.constants import APIS, TEMP_FOLDER, LOCAL_INTEGRATED_FOLDER, PICTURE_FORMATS, TAGS_TO_REMOVE, REPLACE_DICT
from firstimpression.file import update_directories_api, create_directories, check_too_old, write_root_to_xml_files, list_files_dir, download_media, xml_to_root
from firstimpression.rss import get_feed
from firstimpression.text import remove_tags_from_string
from firstimpression.xml import get_attrib_from_element
from firstimpression.scala import variables, Log, install_content

##################################################################################################
# LOGGING
##################################################################################################

script = 'Interia'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['news_polish']

RSSFEED_URL = {
    'sport': 'https://sport.interia.pl/feed',
    'polska': 'https://wydarzenia.interia.pl/polska/feed',
    'kultura': 'https://wydarzenia.interia.pl/kultura/feed'
}

TAGS = {
    'item': 'channel/item',
    'title': 'title',
    'description': 'description'
}

LOCAL_PATH = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME)

MAX_ITEMS = 4
MAX_FILE_AGE = 60 * 10

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api(news_categories, minimal_items):

    debug.log('folder name: {}'.format(NAME))

    update_directories_api(NAME)

    minimal_items = MAX_ITEMS if minimal_items > MAX_ITEMS else minimal_items

    debug.log('minimal_items: {}'.format(minimal_items))

    for news_category in news_categories:
        if news_category == '' or news_category is None:
            warn.log('news category is empty')
            continue

        category = news_category.lower()
        url = RSSFEED_URL[category]
        xml_temp_path = os.path.join(
            TEMP_FOLDER, NAME, '{}.xml'.format(category))

        debug.log(
            'category: {} - url: {} - temp path: {}'.format(category, url, xml_temp_path))

        create_directories([
            os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, category),
            os.path.join(TEMP_FOLDER, NAME, category)])

        if check_too_old(xml_temp_path, MAX_FILE_AGE):
            root = ET.Element("root")
            feed = get_feed(url)

            for news_item in feed.findall(TAGS['item']):
                item = ET.SubElement(root, "item")
                ET.SubElement(item, "title").text = get_title(news_item)
                ET.SubElement(
                    item, "description").text = get_description(news_item)

                media_link = install_picture_content_wrap('square', os.path.join(
                    NAME, category), TEMP_FOLDER, news_item, 'enclosure', 'url')

                if not media_link:
                    debug.log('image not found using placeholder')
                    media_link = 'Content:\\placeholders\\img.png'

                ET.SubElement(item, "picsqr").text = media_link

                if len(root) == MAX_ITEMS:
                    debug.log('max amount of items reached')
                    break

            if len(root) >= minimal_items:
                write_root_to_xml_files(root, xml_temp_path, NAME)
            else:
                warn.log('not enough news items found to store to xml file')


def check_api(news_categories):
    svars = variables()

    for category in news_categories:
        debug.log('category: {}'.format(category))
        file_path = glob.glob(os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, '{}*.xml'.format(category.lower())))
        
        if len(file_path) > 0:
            file_path = file_path[0]
            debug.log('glob filepath: {}'.format(file_path))

            if check_too_old(file_path, MAX_FILE_AGE):
                svars['skipscript'] = True
                info.log('file too old')
                break
            else:
                svars['skipscript'] = False

                svars['total_items'] = len(xml_to_root(file_path))
                svars['total_categories'] = len(news_categories)

                if svars['total_items'] == 0 or svars['total_categories'] == 0:
                    svars['skipscript'] = True
                    warn.log('total_items or total_categories is empty')
                    break
        else:
            warn.log('File does not exists')
            svars['skipscript'] = True


##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################

def install_picture_content_wrap(picture_format, subdirectory, temp_folder, element, tag, attrib):
    # Installs content to LocalIntegratedContent folder and returns mediapath
    if not picture_format in PICTURE_FORMATS:
        return None

    media_link = get_attrib_from_element(
        element, tag, attrib).replace("_sqr256", "")

    media_path = download_media(
        PICTURE_FORMATS[picture_format] + media_link, subdirectory, temp_folder)

    install_content(media_path, subdirectory)

    media_filename = media_path.split('\\').pop()

    return os.path.join('Content:\\', subdirectory, media_filename)

##################################################################################################
# GET FUNCTIONS
##################################################################################################


def get_title(news_item):
    return news_item.findtext(TAGS['title'], '')


def get_description(news_item):
    return remove_tags_from_string(TAGS_TO_REMOVE, news_item.findtext(TAGS['description'], ''))

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################
