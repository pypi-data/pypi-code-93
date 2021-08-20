import xml.etree.ElementTree as ET
import os

from firstimpression.constants import APIS, TEMP_FOLDER, ENGLISH_INDEX, REPLACE_DICT, TAGS_TO_REMOVE, LOCAL_INTEGRATED_FOLDER
from firstimpression.file import update_directories_api, xml_to_root, check_too_old, write_root_to_xml_files, list_files_dir
from firstimpression.text import replace_html_entities, remove_tags_from_string
from firstimpression.rss import get_feed
from firstimpression.time import change_language, parse_string_to_string
from firstimpression.scala import variables, Log


##################################################################################################
# LOGGING
##################################################################################################

script = 'BBC'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['bbc']

LOCAL_PATH = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME)

DATETIME_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
DATETIME_ABREVIATION_FORMAT = '%b %d %Y %H:%M'
DATETIME_FULL_FORMAT = '%B %d %Y %H:%M'

MAX_ITEMS = 10
MAX_FILE_AGE = 60 * 10

TAGS = {
    'item': 'channel/item',
    'title': 'title',
    'descr': 'description',
    'pubDate': 'pubDate'
}

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api(news_category, minimal_items):
    debug.log('folder name: {}'.format(NAME))
    xml_temp_path = os.path.join(TEMP_FOLDER,
                                 NAME,
                                 '{}.xml'.format(news_category))
    
    debug.log('file path {}: {}'.format(news_category, xml_temp_path))

    url = 'http://feeds.bbci.co.uk/news/{}/rss.xml'.format(news_category)
    minimal_items = MAX_ITEMS if minimal_items > MAX_ITEMS else minimal_items

    debug.log('url: {}'.format(url))
    debug.log('minimal_items: {}'.format(minimal_items))

    update_directories_api(NAME)
    change_language(ENGLISH_INDEX)

    if check_too_old(xml_temp_path, MAX_FILE_AGE):
        root = ET.Element("root")
        feed = get_feed(url)

        for news_item in get_news_items(feed):
            root.append(parse_news_item(news_item))

            if len(root) == MAX_ITEMS:
                debug.log('max amount of items reached')
                break

        if len(root) >= minimal_items:
            write_root_to_xml_files(root, xml_temp_path, NAME)
        else:
            warn.log('root consist out of less than minimal items.')
    else:
        debug.log('file not old enough to update')


def check_api():
    svars = variables()

    for file in list_files_dir(LOCAL_PATH):
        debug.log('file: {}'.format(file))
        if 'xml' in file:
            file_path = os.path.join(LOCAL_PATH, file)
            debug.log('xml file: {}'.format(file_path))
            if check_too_old(file_path, MAX_FILE_AGE):
                svars['skipscript'] = True
                warn.log('file too old to show')
                break
            else:
                svars['skipscript'] = False

                amount_items = len(xml_to_root(file_path))

                if amount_items == 0:
                    warn.log('no items found in xml file')
                    svars['skipscript'] = True
                    break

                svars['total_items'] = amount_items

##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


##################################################################################################
# GET FUNCTIONS
##################################################################################################

def get_news_items(root):
    return root.findall(TAGS['item'])


def get_news_title(news_item):
    return replace_html_entities(REPLACE_DICT, news_item.findtext(TAGS['title'], ''))


def get_news_description(news_item):
    return remove_tags_from_string(TAGS_TO_REMOVE, news_item.findtext(TAGS['descr'], ''))


def get_short_date(news_item):
    return parse_string_to_string(news_item.findtext(TAGS['pubDate'], ''), DATETIME_FORMAT, DATETIME_ABREVIATION_FORMAT)


def get_full_date(news_item):
    return parse_string_to_string(news_item.findtext(TAGS['pubDate'], ''), DATETIME_FORMAT, DATETIME_FULL_FORMAT)

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################


def parse_news_item(news_item):
    item = ET.Element("item")
    ET.SubElement(item, "title").text = get_news_title(news_item)
    ET.SubElement(item, "descr").text = get_news_description(news_item)
    ET.SubElement(item, "pubDate").text = get_short_date(news_item)
    ET.SubElement(item, "fullMonthPubDate").text = get_full_date(news_item)

    debug.log('item: {}'.format(item))

    return item
