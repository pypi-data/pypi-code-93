import xml.etree.ElementTree as ET
import glob
import os

from firstimpression.constants import APIS, LOCAL_INTEGRATED_FOLDER, TEMP_FOLDER, DUTCH_INDEX, ENGLISH_INDEX, PICTURE_FORMATS, TAGS_TO_REMOVE, REPLACE_DICT
from firstimpression.file import create_directories, update_directories_api, check_too_old, write_root_to_xml_files, download_media, list_files_dir, xml_to_root
from firstimpression.time import change_language, parse_string_to_string, parse_date_to_string, parse_string_to_date
from firstimpression.rss import get_feed
from firstimpression.xml import get_attrib_from_element
from firstimpression.scala import install_content, variables, Log
from firstimpression.text import replace_html_entities, remove_tags_from_string

##################################################################################################
# LOGGING
##################################################################################################

script = 'Nu_nl'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)


##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['nu']

DATETIME_FORMAT = "%a, %d %b %Y %H:%M:%S "
DATETIME_ABREVIATION_FORMAT = '%d %b %Y %H:%M'
DATETIME_FULL_FORMAT = '%d %B %Y %H:%M'

MAX_ITEMS = 10
MAX_FILE_AGE = 60 * 10

LOCAL_PATH = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME)

BASE_URL = 'http://www.nu.nl/rss/'

TAGS = {
    'item': 'channel/item',
    'title': 'title',
    'descr': 'description',
    'pubDate': 'pubDate'
}

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################

def run_api(news_categories, minimal_items):
    debug.log('folder name: {}'.format(NAME))
    minimal_items = MAX_ITEMS if minimal_items > MAX_ITEMS else minimal_items

    debug.log('local path: {}'.format(LOCAL_PATH))
    debug.log('minimal_items: {}'.format(minimal_items))
    
    update_directories_api(NAME)

    for news_category in news_categories:
        if news_category == '' or news_category is None:
            warn.log('category is empty')
            continue

        category = news_category.lower()

        url = BASE_URL + category

        create_directories([os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, category), os.path.join(TEMP_FOLDER, NAME, category)])

        xml_temp_path = os.path.join(TEMP_FOLDER, NAME, '{}.xml'.format(category))

        debug.log('category: {} - url: {} - temp path: {}'.format(category, url, xml_temp_path))

        if check_too_old(xml_temp_path, MAX_FILE_AGE):
            root = ET.Element("root")

            feed = get_feed(url)

            for news_item in feed.findall(TAGS['item']):
                item = ET.SubElement(root, "item")
                ET.SubElement(item, "title").text = replace_html_entities(REPLACE_DICT, get_title(news_item))
                ET.SubElement(item, "descr").text = remove_tags_from_string(TAGS_TO_REMOVE, get_description(news_item))
                ET.SubElement(item, "pubDate").text = parse_date_to_string(get_publication_date(news_item), DATETIME_ABREVIATION_FORMAT)
                ET.SubElement(item, "fullMonthPubDate").text = parse_date_to_string(get_publication_date(news_item), DATETIME_FULL_FORMAT)

                media_link_full = install_picture_content_wrap('fullscreen', os.path.join(NAME, category), TEMP_FOLDER, news_item, 'enclosure', 'url')
                media_link_sqr = install_picture_content_wrap('square', os.path.join(NAME, category), TEMP_FOLDER, news_item, 'enclosure', 'url')

                if media_link_full is None and media_link_sqr is None:
                    debug.log('No image found using placeholder instead')
                    media_link_full = media_link_sqr = 'Content:\\placeholders\\img.png'
                elif media_link_sqr is None:
                    media_link_sqr = media_link_full
                elif media_link_full is None:
                    media_link_full = media_link_sqr
                
                ET.SubElement(item, "picorg").text = media_link_full
                ET.SubElement(item, "picsqr").text = media_link_sqr

                if len(root) == MAX_ITEMS:
                    debug.log('max amount of items reached')
                    break

            if len(root) >= minimal_items:
                write_root_to_xml_files(root, xml_temp_path, NAME)
            else:
                warn.log('not enough news items to store to xml file')
        else:
            debug.log('File not old enough to update')

def check_api(news_categories):
    svars = variables()

    count_categories = 0

    for elem in news_categories:
        if elem != '':
            count_categories += 1

    svars['total_categories'] = count_categories

    for file in list_files_dir(LOCAL_PATH):
        debug.log('file: {}'.format(file))
        if 'xml' in file:
            file_path = os.path.join(LOCAL_PATH, file)
            debug.log('file path: {}'.format(file_path))
            if check_too_old(file_path, MAX_FILE_AGE):
                svars['skipscript'] = True
                info.log('file too old')
                break
            else:
                svars['skipscript'] = False

                amount_items = len(xml_to_root(file_path))

                if amount_items == 0:
                    svars['skipscript'] = True
                    warn.log('file has no news items')
                    break
                
                svars['total_items'] = amount_items


##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################

def install_picture_content_wrap(picture_format, subdirectory, temp_folder, element, tag, attrib):
    # Installs content to LocalIntegratedContent folder and returns mediapath
    if not picture_format in PICTURE_FORMATS:
        warn.log('picture format is not in PICTURE_FORMATS')
        return None

    media_link = get_attrib_from_element(element, tag, attrib).replace("_sqr256", "")

    if picture_format == 'square':
        media_link = media_link.replace('.jpg', '_sqr512.jpg')

    media_path = download_media(PICTURE_FORMATS[picture_format] + media_link, subdirectory, temp_folder)

    install_content(media_path, subdirectory)

    media_filename = media_path.split('\\').pop()

    return os.path.join('Content:\\', subdirectory, media_filename)

##################################################################################################
# GET FUNCTIONS
##################################################################################################

def get_title(news_item):
    return news_item.findtext(TAGS['title'], '')

def get_description(news_item):
    return news_item.findtext(TAGS['descr'], '')

def get_publication_date(news_item):
    time = news_item.findtext(TAGS['pubDate'], None)
    change_language(ENGLISH_INDEX)
    if time is None:
        return ''
    else:
        date = parse_string_to_date(time[:-5], DATETIME_FORMAT)
        change_language(DUTCH_INDEX)
        return date

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################


