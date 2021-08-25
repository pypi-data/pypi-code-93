import os
import time
from imghdr import what
import shutil
import requests
from bs4 import BeautifulSoup
from firstimpression.scala import install_content
from firstimpression.api.request import request
from firstimpression.constants import TEMP_FOLDER, LOCAL_INTEGRATED_FOLDER, PLACEHOLDER_FOLDER, IMG_EXTENSIONS
import xml.etree.ElementTree as ET


def create_directories(directories):
    for dirpath in directories:
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)


def get_age(filepath):
    return time.time() - os.path.getmtime(filepath)


def check_too_old(filepath, max_age):
    try:
        file_age = get_age(filepath)
    except WindowsError:
        return True

    if file_age > max_age:
        return True
    else:
        return False


def check_valid_jpeg(filepath):
    return what(filepath) == 'jpeg' or what(filepath) == 'jpg'


def download_media(media_link, subdirectory, temp_folder, filename=None):
    # Downloads and returns path of media
    if filename is None:
        media_filename = media_link.split('/').pop()
    else:
        media_filename = filename
    media_path = os.path.join(temp_folder, subdirectory, media_filename)

    response = requests.get(media_link, stream=True)

    with open(media_path, 'wb') as writefile:
        shutil.copyfileobj(response.raw, writefile)

    return media_path


def install_media(media_link, subdirectory):
    install_content(media_link, subdirectory)
    return os.path.join('Content:\\', subdirectory, media_link.split('\\').pop())


def purge_directories(directories, max_days):
    # Remove all files from directory that are older than max_days
    for directory in directories:
        for file in os.listdir(directory):
            
            filepath = os.path.join(directory, file)
            
            if os.path.isdir(filepath):
                purge_directories([filepath], max_days)
            else:
                file_age = get_age(filepath)

                if file_age > max_days * 86400:
                    os.remove(filepath)


def write_root_to_xml_files(root, path, subfolder=None):
    tree = ET.ElementTree(root)
    tree.write(path)
    install_content(path, subfolder)


def xml_to_root(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return root

def list_files(url, extensions):
    response = request(url).text
    soup = BeautifulSoup(response, 'html.parser')
    all_elements = [elem.get('href') for elem in soup.find_all('a')]
    select_elements = [elem for elem in all_elements if '.' + elem.split('.')[-1] in extensions]
    return select_elements

def list_files_dir(path):
    return [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]

def update_directories_api(api_name, max_days=1):
    temp_folder = os.path.join(TEMP_FOLDER, api_name)
    local_folder = os.path.join(LOCAL_INTEGRATED_FOLDER, api_name)
    temp_placeholder = os.path.join(TEMP_FOLDER, 'placeholders')

    create_directories([temp_folder, local_folder, PLACEHOLDER_FOLDER, temp_placeholder])
    update_placeholders()
    purge_directories([temp_folder, local_folder], max_days)

def update_placeholders():
    url = 'http://37.97.211.104/narrowcasting/placeholders'
    max_age = 60 * 60 * 24

    for file in list_files(url, IMG_EXTENSIONS):
        if check_too_old(os.path.join(TEMP_FOLDER, 'placeholders', file), max_age):
            download_install_media(url + '/{}'.format(file), TEMP_FOLDER, 'placeholders')
            
def download_install_media(url, temp_dir, subdir, fname=None):
    return install_media(download_media(url, subdir, temp_dir, fname), subdir)