#!/usr/bin/env python3
"""
 DESCRIPTION
          This tool is part of cygnsslib python package. The package is created by Mixil lab at USC
          See <https://bitbucket.org/usc_mixil/cygnss-library>

          This Tool download SRTM .hgt data

 AUTHOR   Amer Melebari
          Microwave Systems, Sensors and Imaging Lab (MiXiL)
          University of Southern California
 EMAIL    jamesdca@usc.edu
 CREATED  2020-08-16
 Updated  2020-06-22


part of the download_file() is from the following codes:
https://git.earthdata.nasa.gov/projects/LPDUR/repos/daac_data_download_python/
https://github.com/DHI-GRAS/earthdata-download/tree/master/earthdata_download

  Copyright 2020 University of Southern California
"""
from cygnsslib.data_downloader.pass_core import MixilKeys
from getpass import getpass
from time import sleep
from tqdm.auto import tqdm
import numpy as np
import os
import requests
import shutil
import zipfile

CHUNK_SIZE = 512 * 1024  # 512 kB
MAX_CONNECTIONS_TRIES = 10
MIN_FILE_SIZE_BYTES = 10e3
SRTM_USGS_URL = 'https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/'
"""
"""


class EarthdataSession(requests.Session):

    AUTH_DOMAINS = ['nasa.gov', 'usgs.gov']

    def __init__(self, username, password):
        """Create Earthdata Session that preserves headers when redirecting"""
        super(EarthdataSession, self).__init__()  # Python 2 and 3
        self.auth = (username, password)

    def rebuild_auth(self, prepared_request, response):
        """Keep headers upon redirect as long as we are on any of self.AUTH_DOMAINS"""
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            original_domain = '.'.join(original_parsed.hostname.split('.')[-2:])
            redirect_domain = '.'.join(redirect_parsed.hostname.split('.')[-2:])
            if original_domain != redirect_domain and redirect_domain not in self.AUTH_DOMAINS and original_domain not in self.AUTH_DOMAINS:
                del headers['Authorization']


def _cyg_data_auth_err_handling():
    print('Error in the Earthdata Credentials, try to enter them again.')
    print('Note: you need to re-start the code after this download as the new user/pass need to be re-loaded')
    save_pass_str = input('Do you want to save the new user/pass? (if yes, the old user/pass will be deleted) [Yes, No]')
    save_pass = True if (save_pass_str.lower() in ['y', 'yes']) else False
    podaac_usr, podaac_pass = get_earthdata_cred(pass_folder=None, save_pass=save_pass)
    return podaac_usr, podaac_pass


def _download_file_earthdata(file_url, output_folder, auth):
    """
    download the file with url into folder output_folder

    :param file_url: url of the file
    :type file_url: str
    :param output_folder: saving folder
    :type output_folder: str
    :param auth: username and pass
    :type auth: tuple of str
    :return: downloaded file path
    :rtype: str
    """
    file_name = file_url.split('/')[-1]
    out_file = os.path.join(output_folder, file_name)

    out_file_temp = f'{out_file:s}.incomplete'
    for i_try in np.arange(MAX_CONNECTIONS_TRIES):
        try:
            with EarthdataSession(username=auth[0], password=auth[1]) as session:
                with session.get(file_url, stream=True) as response:
                    response.raise_for_status()
                    response.raw.decode_content = True
                    with tqdm.wrapattr(open(out_file_temp, "wb"), "write", miniters=1, total=int(response.headers.get('content-length', 0)),
                                       desc=out_file_temp) as target_file:
                        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                            target_file.write(chunk)

            filesize = os.path.getsize(out_file_temp)
            if filesize < MIN_FILE_SIZE_BYTES:
                raise RuntimeError(f'Size of downloaded file is only {(filesize * 1e-3):.3f} B. Suspecting broken file ({out_file_temp}).')

        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
            if i_try < MAX_CONNECTIONS_TRIES:
                print('Connection Error sleep for 5 sec')
                sleep(5)
            else:
                raise RuntimeError(f'a connection error was raised when trying to access {file_url:s}\n {e}')
        except requests.exceptions.RequestException:
            if i_try < MAX_CONNECTIONS_TRIES:
                podaac_usr, podaac_pass = _cyg_data_auth_err_handling()
                auth = (podaac_usr, podaac_pass)
            else:
                raise RuntimeError('Authentication error, please check your PODAAC user/pass')
        except RuntimeError as e:
            if i_try < MAX_CONNECTIONS_TRIES:
                continue
            else:
                raise RuntimeError(e)

        else:  # if it was successful
            break

    shutil.move(out_file_temp, out_file)

    return out_file


def extract_srtm_zipfile(zip_file, out_path):
    """
    unzip file

    :param zip_file: zip file path
    :type zip_file: str
    :param out_path: extraction out folder
    :type out_path: str
    :return: unzipped file name
    :rtype: str
    """

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        file_name = zip_ref.namelist()[0]
        zip_ref.extractall(out_path, members=[file_name])

    return os.path.join(out_path, file_name)


def get_srtm_file_name(lat, lon):
    """
    get SRTM file name. the name of the zipped file, for the unzipped file use get_srtm_ght_file_name_frm_lat_lon() or get_srtm_unzipped_file_name()
    :param lat: latitude
    :type lat: int or float
    :param lon: longitude
    :type lon: int or float
    :return:
    """
    file_coord = _get_srtm_file_coord_name(lat, lon)
    file_name = f'{file_coord:s}.SRTMGL1.hgt.zip'
    return file_name


def _get_srtm_file_coord_name(lat, lon):
    """

    :param lat: latitude
    :type lat: int or float
    :param lon: longitude
    :type lon: int or float
    :return:
    """
    lat = int(lat)
    lon = int(lon)
    if lat > 59 or lat < -56:
        raise ValueError('Latitude value should be between -56 to 59. Got {:d}'.format(lat))
    if lon > 179 or lon < -180:
        raise ValueError('Longitude value should be between -180 to 179. Got {:d}'.format(lon))
    lat_direction = 'N' if (lat >= 0) else 'S'
    lon_direction = 'E' if (lon >= 0) else 'W'
    file_coord = '{:s}{:02d}{:s}{:03d}'.format(lat_direction, abs(lat), lon_direction, abs(lon))
    return file_coord


def get_srtm_ght_file_name(lat, lon):
    """
    return the name of the .hgt file from lat, lon value
    :param lat: latitude
    :type lat: int or float
    :param lon: longitude
    :type lon: int or float
    :return:
    """
    file_coord = _get_srtm_file_coord_name(lat, lon)
    file_name = f'{file_coord:s}.hgt'
    return file_name


def get_srtm_unzipped_file_name(zipped_filename):
    """
    return the unzipped SRTM file name from the zipped SRTM file name

    :param zipped_filename: zipped SRTM file name from get_srtm_file_name()
    :type zipped_filename: str
    :return: unzipped SRTM file name
    :rtype: str
    """
    return '{:s}.hgt'.format(zipped_filename.split('.')[0])


def get_earthdata_cred(pass_folder=None, save_pass=True, reset_pass=False):
    """
    import EarthData username and pass from the system, if not found it ask you to enter them

    :return:
    """
    if reset_pass:
        mixil_keys = MixilKeys(pass_folder=pass_folder)
        mixil_keys.remove('lpdaac_usr')
        mixil_keys.remove('lpdaac_pass')
        del mixil_keys

    if save_pass:
        mixil_keys = MixilKeys(pass_folder=pass_folder)
        mixil_keys.require('lpdaac_usr', msg='Get NASA Earthdata Credentials from: https://urs.earthdata.nasa.gov/home \nNASA Earthdata Username: ')
        mixil_keys.require('lpdaac_pass', msg='NASA Earthdata Password: ')
        earthdata_usr = mixil_keys.retrieve('lpdaac_usr')
        earthdata_pass = mixil_keys.retrieve('lpdaac_pass')
    else:
        earthdata_usr = getpass('NASA Earthdata Username: ')
        earthdata_pass = getpass('NASA Earthdata Password: ')

    return earthdata_usr, earthdata_pass


def download_srtm_ght_files(list_lat, list_lon, out_folder=None, earthdata_usr_pass=None, save_pass=True, unzipfile=False, remove_zippedfile=True,
                            silent_run=False):
    """
    download a multiple SRTM file in ght format. it download the files within the lat/long lists

    The files are in this URL: https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/
    the username/password can be obtained from https://urs.earthdata.nasa.gov/home

    :param list_lat: list of latitude
    :type list_lat: list of int or numpy.array or int
    :param list_lon: list of longitude
    :type list_lon: list of int or or numpy.array or int
    :param out_folder: save folder, if None, it will be saved in "$SRTM_PATH/hgt"
    :type out_folder: str
    :param earthdata_usr_pass: earthdata username and password (usr,pass).  https://urs.earthdata.nasa.gov/home
    :type earthdata_usr_pass: tuple of str
    :param save_pass: (active if earthdata_usr_pass is None) save earthdata username and password in the system (select False if you're using a shared
     or public PC)
    :type save_pass: bool
    :param unzipfile: unzip the downloaded file?
    :type unzipfile: bool
    :param remove_zippedfile: delete the unzipped file after unzipping?
    :type remove_zippedfile: bool
    :param silent_run: if true no screen output will be shown except downloading progress and errors
    :type silent_run: bool
    :return: files path
    :rtype: list of str
    """
    try:
        iter(list_lat)
    except TypeError:
        list_lat = [int(list_lat)]
    try:
        iter(list_lon)
    except TypeError:
        list_lon = [int(list_lon)]

    if out_folder is None:
        out_folder = os.path.join(os.environ['SRTM_PATH'], 'hgt')
        os.makedirs(out_folder, exist_ok=True)
    if earthdata_usr_pass is None:
        earthdata_usr_pass = get_earthdata_cred(save_pass=save_pass)

    d_file_paths = list()
    for lat in list_lat:
        for lon in list_lon:
            d_file_paths.append(download_srtm_ght_single_file(lat, lon, out_folder=out_folder, earthdata_usr_pass=earthdata_usr_pass,
                                                              save_pass=save_pass, unzipfile=unzipfile, remove_zipedfile=remove_zippedfile,
                                                              silent_run=silent_run))

    return d_file_paths


def download_srtm_ght_single_file(lat, lon, out_folder=None, earthdata_usr_pass=None, save_pass=True, unzipfile=False, remove_zipedfile=True,
                                  silent_run=False):
    """

    download a single SRTM file in ght format, don't use this function directly, consider using download_srtm_ght_files()
    The files are in this URL: https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/
    the username/password can be obtain from https://urs.earthdata.nasa.gov/home

    :param lat: file latitude
    :type lat: int
    :param lon: file longitude
    :type lon: int
    :param out_folder: save folder, if None, it will be saved in "$SRTM_PATH/hgt"
    :type out_folder: str
    :param earthdata_usr_pass: earthdata username and password (usr,pass).  https://urs.earthdata.nasa.gov/home
    :type earthdata_usr_pass: tuple of string
    :param save_pass: (active if earthdata_usr_pass is None) save earthdata username and password in the system (select False if you're using a shared
     or public PC)
    :type save_pass: bool
    :param unzipfile: unzip the downloaded file?
    :type unzipfile: bool
    :param remove_zipedfile: delete the unzipped file after unzipping? ignored if unzipfile is False
    :type remove_zipedfile: bool
    :param silent_run: if true no screen output will be shown except downloading progress
    :type silent_run: bool
    :return: file path
    :rtype: str
    """
    if out_folder is None:
        out_folder = os.path.join(os.environ['SRTM_PATH'], 'hgt')
        os.makedirs(out_folder, exist_ok=True)

    file_name = get_srtm_file_name(lat, lon)
    file_path = os.path.join(out_folder, file_name)
    unzipped_file_path = os.path.join(out_folder, get_srtm_unzipped_file_name(file_name))
    if os.path.exists(unzipped_file_path):
        if not silent_run:
            print(f'{unzipped_file_path:s} file exist')
        return unzipped_file_path
    if os.path.exists(file_path):
        if not silent_run:
            print(f'{file_path:s} file exist')
        return file_path

    if earthdata_usr_pass is None:
        earthdata_usr_pass = get_earthdata_cred(save_pass=save_pass)
    file_url = f'{SRTM_USGS_URL:s}{file_name:s}'
    saved_zip_file = _download_file_earthdata(file_url, out_folder, auth=earthdata_usr_pass)
    if not unzipfile:
        return saved_zip_file

    extract_srtm_zipfile(saved_zip_file, out_folder)
    unzipped_file = os.path.join(out_folder, get_srtm_unzipped_file_name(file_name))
    if remove_zipedfile:
        os.remove(saved_zip_file)
    return unzipped_file


if __name__ == '__main__':
    files_lat = np.array([21, 22, 20])
    files_lon = [29, 30]
    download_srtm_ght_files(files_lat, files_lon)

