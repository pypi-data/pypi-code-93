import urllib.request
import os
from os import path
import zipfile


def download_runner(runner_type, download_urls):
    name = runner_type
    runner_dir = get_runner_dir()

    if download_urls.get(runner_type) is None:
        return

    url = download_urls[name]

    if path.isdir(runner_dir) is False:
        os.mkdir(runner_dir)

    if path.isdir(os.path.join(runner_dir, name)) is False or path.isdir(
            os.path.join(runner_dir, name, 'data')) is False:
        print('Folder does not exist, downloading....')
        print('Path to download is: ', runner_dir)

        try:
            urllib.request.urlretrieve(url, os.path.join(runner_dir, name + '.zip'))
        except urllib.error.HTTPError as e:
            print(e.code)
        except:
            print('Error during retrieving file')

    else:
        print('Folder exists, skipping download')

    unzip_and_delete(runner_dir, name)


def get_runner_dir():
    cur_dir = os.getcwd()
    parent_dir = os.path.abspath(os.path.join(cur_dir, os.pardir))
    runner_dir = os.path.join(parent_dir, 'runners')
    return runner_dir


def unzip_and_delete(runner_dir, name):
    # unzip
    if path.isdir(os.path.join(runner_dir, name)) is False or path.isdir(
            os.path.join(runner_dir, name, 'data')) is False:
        zip_ref = zipfile.ZipFile(os.path.join(runner_dir, name + '.zip'), 'r')
        zip_ref.extractall(os.path.join(runner_dir))
        zip_ref.close()

        # delete zip
        os.remove(os.path.join(runner_dir, name + '.zip'))
