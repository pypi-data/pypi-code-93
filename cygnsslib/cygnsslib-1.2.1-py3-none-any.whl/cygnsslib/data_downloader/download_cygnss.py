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
 CREATED  2020‑07‑19
 Updated  2020-08-22

  Copyright 2020 University of Southern California
"""
from cygnsslib.data_downloader.download_srtm import EarthdataSession
from cygnsslib.data_downloader.pass_core import MixilKeys
from getpass import getpass
from time import sleep
from tqdm.auto import tqdm
import datetime as dt
import fnmatch
import hashlib
import numpy as np
import os
import requests
import shutil
import warnings

CYG_MIN_FILE_SIZE = 50e6  # in bytes
PODAAC_CYG_URL = 'https://podaac-tools.jpl.nasa.gov/drive/files/allData/cygnss'
OPEN_DAP_URL = 'https://opendap.jpl.nasa.gov/opendap/allData/cygnss'
L1_VER = 'v3.0'
CHUNK_SIZE = 1024 * 1024  # 1 MB
MAX_CONNECTIONS_TRIES = 10


def _cyg_data_auth_err_handling():
    print('Error in the PODAAC API Credentials, try to enter them again.')
    print('Note: you need to re-start the code after this download as the new user/pass need to be re-loaded')
    save_pass_str = input('Do you want to save the new user/pass? (if yes, the old user/pass will be deleted) [Yes, No]')
    save_pass = True if (save_pass_str.lower() in ['y', 'yes']) else False
    podaac_usr, podaac_pass = get_podaac_cred(pass_folder=None, save_pass=save_pass)
    return podaac_usr, podaac_pass


def checksum(file_path, chunk_num_blocks=4096):
    """
    do md5 checksum for large files

    :param file_path: file path
    :type file_path: str
    :param chunk_num_blocks: number of blocks in a chunk
    :type chunk_num_blocks: int
    :return:
    """

    h = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_num_blocks * h.block_size):
            h.update(chunk)
    return h.hexdigest()


def download_file(file_url, output_folder, auth=None, url_md5_checksum=None):
    """
    download the file with url into folder output_folder

    :param file_url: url of the file
    :type file_url: str
    :param output_folder: saving folder
    :type output_folder: str
    :param auth: username or pass
    :type auth: tuple of str or None
    :param url_md5_checksum: md5 checksum of the downloaded file, if None, the code will find it
    :type url_md5_checksum: str
    :return: downloaded file path
    :rtype: str
    """
    num_redownload = 0
    file_name = file_url.split('/')[-1]
    out_file = os.path.join(output_folder, file_name)
    out_file_temp = f'{out_file:s}.incomplete'
    for i_try in range(MAX_CONNECTIONS_TRIES):
        try:
            with EarthdataSession(username=auth[0], password=auth[1]) as session:
                with session.get(file_url, stream=True) as response:
                    if response.status_code == 404:
                        return None
                    elif response.status_code == 401:  # Auth Error
                        raise requests.exceptions.RequestException
                    response.raise_for_status()
                    response.raw.decode_content = True
                    file_size = int(response.headers.get('content-length', 0))
                    free_disk_space = shutil.disk_usage(output_folder).free
                    if file_size > free_disk_space:
                        def bytes2mb(x: float) -> int: return int(x / 1024 / 1024)
                        raise IOError(f'No enough space in the disk. file size: {bytes2mb(file_size):d} MB, free space {bytes2mb(free_disk_space):d}')
                    file_screen_name = f'...{os.sep.join(out_file_temp.split(os.sep)[-4:])[:-11]}' if (len(out_file_temp) > 80) else out_file_temp
                    with tqdm.wrapattr(open(out_file_temp, "wb"), "write", miniters=1, total=file_size, desc=file_screen_name) as target_file:
                        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                            target_file.write(chunk)
                if url_md5_checksum is None:  # get md5 checksum
                    url_md5_checksum = session.get(f'{file_url:s}.md5').content.strip().decode('utf').split()[0]
                if url_md5_checksum:  # if the md5 file available
                    file_checksum = checksum(out_file_temp)
                    if url_md5_checksum != file_checksum:
                        raise RuntimeError
                else:
                    print(f'MD5 checksum is not available for this file; {file_name:s}')
        except RuntimeError:  # MD5 verification failed
            if i_try < MAX_CONNECTIONS_TRIES and num_redownload < 2:
                print("MD5 checksum failed! Trying to re-download it again")
                os.remove(out_file_temp)
                num_redownload += 1
            else:
                print("MD5 checksum failed!")
                shutil.move(out_file_temp, out_file)
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            if i_try < MAX_CONNECTIONS_TRIES:
                print('Connection Error sleep for 5 sec')
                sleep(5)
            else:
                raise RuntimeError(f'a connection error was raised when trying to access {file_url:s}')
        except requests.exceptions.RequestException:
            if i_try < MAX_CONNECTIONS_TRIES:
                podaac_usr, podaac_pass = _cyg_data_auth_err_handling()
                auth = (podaac_usr, podaac_pass)
            else:
                raise RuntimeError('Authentication error, please check your PODAAC user/pass')

        else:  # if it was successful
            shutil.move(out_file_temp, out_file)
            break
    return out_file


def _get_cyg_page_data(cyg_folder_url, podaac_usr_pass):
    data = None
    for i_try in range(MAX_CONNECTIONS_TRIES):
        try:
            with EarthdataSession(username=podaac_usr_pass[0], password=podaac_usr_pass[1]) as session:
                with session.get(cyg_folder_url) as response:
                    data = str(response.content).split('<tr>')
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            if i_try < MAX_CONNECTIONS_TRIES:
                print('Connection Error sleep for 5 sec')
                sleep(5)
            else:
                raise RuntimeError(f'a connection error was raised when trying to access {cyg_folder_url:s}')

        else:  # if it was successful
            break

    return data


def _get_md5_file(day_page_data, sc_num, cyg_folder_url, auth):
    tag = f'cyg{sc_num:02d}.'
    endtag = '.nc.md5'
    for item in day_page_data:
        if tag in item:
            try:
                ind = item.index(tag)
                item = item[ind:]
                end = item.index(endtag)
            except ValueError:
                continue

            file_name = item[:end] + endtag
            md5_file_full_url = f'{cyg_folder_url:s}{file_name:s}'
            for i_try in range(MAX_CONNECTIONS_TRIES):
                try:
                    with EarthdataSession(username=auth[0], password=auth[1]) as session:
                        mdf5_file = session.get(md5_file_full_url).content.strip().decode('utf').split()
                        if mdf5_file:
                            cyg_file_name = mdf5_file[1]
                            cyg_checksum = mdf5_file[0]
                            return cyg_file_name, cyg_checksum
                        else:
                            print(f'MD5 checksum is not available for this file; {file_name:s}')
                            return None, None
                except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
                    if i_try < MAX_CONNECTIONS_TRIES:
                        print('Connection Error sleep for 5 sec')
                        sleep(5)
                    else:
                        raise RuntimeError(f'a connection error was raised when trying to access {md5_file_full_url:s}')
                except requests.exceptions.RequestException:
                    if i_try < MAX_CONNECTIONS_TRIES:
                        podaac_usr, podaac_pass = _cyg_data_auth_err_handling()
                        auth = (podaac_usr, podaac_pass)
                    else:
                        raise RuntimeError('Authentication error, please check your PODAAC user/pass')

    return None, None


def download_cyg_file(data_year, data_day, sc_num, cyg_data_ver, cyg_data_lvl, out_folder, podaac_usr_pass, day_page_data=None, cyg_file_name=None,
                      cyg_md5_checksum=None):
    """
    download cygnss data file from PODAAC, the username and pass can be obtained from https://podaac-tools.jpl.nasa.gov/drive/
    Don't use this function directly, instead use download_cyg_files()

    :param data_year: data year (ex. 2019)
    :type data_year: int
    :param data_day: data day number (ex. 130)
    :type data_day: int
    :param sc_num: cygnss spacecraft number (1-8)
    :type sc_num: int
    :param cyg_data_ver: cygnss data version (ex: 'v2.1')
    :type cyg_data_ver: str
    :param cyg_data_lvl: cygnss data level (ex: 'L1')
    :type cyg_data_lvl: str
    :param out_folder: folder of the saved output (ex: /cygnss_data/L1/v2.1/2019/020)
    :type out_folder: str
    :param podaac_usr_pass: PODAAC user name and pass (usr name, pass)
    :type podaac_usr_pass: tuple of string
    :param day_page_data: page of the selected day, this to reduce the times the script requests the page from the website, default None
    :type day_page_data: list of str or None
    :param cyg_file_name: cygness file name, if None, the code will find it
    :type cyg_file_name: str
    :param cyg_md5_checksum: md5 checksum, if None, the code will find it
    :type cyg_md5_checksum: str
    :return: file name
    :rtype: str or None
    """

    if os.path.isfile(out_folder):
        raise ValueError(f'Invalid out_folder={out_folder}, this is a file not a folder')

    cyg_folder_url = f'{PODAAC_CYG_URL:s}/{cyg_data_lvl:s}/{cyg_data_ver:s}/{data_year:04d}/{data_day:03d}/'
    if cyg_file_name is None:
        if day_page_data is None:
            day_page_data = _get_cyg_page_data(cyg_folder_url, podaac_usr_pass)

        tag = f'cyg{sc_num:02d}.'
        endtag = '.nc'
        for item in day_page_data:
            if tag in item:
                try:
                    ind = item.index(tag)
                    item = item[ind:]
                    end = item.index(endtag)
                except ValueError:
                    continue

                cyg_file_name = item[:end + 3]
                break
    if cyg_file_name is None:
        print(f"File doesn't exist in the PODAAC, year:{data_year:04d}, day:{data_day:03d}, SC: {sc_num:02d}")
        return cyg_file_name
    if not os.path.isdir(out_folder):
        os.makedirs(out_folder, exist_ok=True)

    cyg_file_full_url = f'{cyg_folder_url:s}{cyg_file_name:s}'
    cyg_file_name = download_file(cyg_file_full_url, out_folder, auth=podaac_usr_pass, url_md5_checksum=cyg_md5_checksum)
    if cyg_file_name is None:
        print(f"File doesn't exist in the PODAAC, year:{data_year:04d}, day:{data_day:03d}, SC: {sc_num:02d}")
    return cyg_file_name


def download_cyg_files(data_year, list_data_day, list_sc_num=None, podaac_usr=None, podaac_pass=None, cyg_data_ver=None, cyg_data_lvl='L1',
                       cygnss_l1_path=None, check_md5_exist_file=False, force_download=False, save_podaac_pass=True):
    """
    
    download multiple CYGNSS files
    
    :param data_year: data year
    :type data_year: int
    :param list_data_day: list of data days
    :type list_data_day: list or int or np.array
    :param list_sc_num: list of cygnss spacecraft numbers (1-8), if None will download all SCs
    :type list_sc_num: list or int or np.array or None
    :param podaac_usr: PODAAC user name. if None, it will ask you to enter it
    :type podaac_usr: str or None
    :param podaac_pass: PODAAC Drive API password. if None, it will ask you to enter it
    :type podaac_pass: str or None
    :param cyg_data_ver: cygnss data version (ex: 'v2.1')
    :type cyg_data_ver: str
    :param cyg_data_lvl: cygnss data level (ex: 'L1')
    :type cyg_data_lvl: str
    :param cygnss_l1_path: path of the cygnss L1 data (default: os.environ.get('CYGNSS_L1_PATH'))
    :type cygnss_l1_path: str or None
    :param check_md5_exist_file: check md5 checksum for existing files? this will make it very slow
    :type check_md5_exist_file: bool
    :param force_download: re-download the file even if the version is not included in the path (not recommended)
    :type force_download: bool
    :param save_podaac_pass: save podaac username and pass in your system? (select False if you're using a shared or public PC)
    :type save_podaac_pass: bool
    :return: 
    """
    if cygnss_l1_path is None:
        cygnss_l1_path = os.environ.get('CYGNSS_L1_PATH')
    if np.size(list_data_day) == 1:
        list_data_day = [int(list_data_day)]
    if list_sc_num is None:
        list_sc_num = np.arange(1, 9)
    elif np.size(list_sc_num) == 1:
        list_sc_num = [int(list_sc_num)]

    if cygnss_l1_path is None:
        raise ValueError("$CYGNSS_L1_PATH environment variable need to be set, or use cygnss_l1_path input parameter")

    if cyg_data_ver is None:
        folder_list = cygnss_l1_path.split(os.path.sep)
        if not folder_list[-1]:
            folder_list.pop(-1)
        cyg_data_ver = folder_list[-1]
    cyg_data_lvl = cyg_data_lvl.upper()

    podaac_usr_pass = get_podaac_cred(save_pass=save_podaac_pass) if (podaac_usr is None or podaac_pass is None) else (podaac_usr, podaac_pass)
    ver_folder_exist = check_ver_folder(cygnss_l1_path, cyg_data_ver)
    if not force_download and not ver_folder_exist:
        error_str = f"You are trying to download version {cyg_data_ver:s}, but the path doesn't contain the version name"
        raise ValueError(f'{error_str:s}\nuse force_download=True to remove this error')
    downloaded_files_list = list()
    for data_day in list_data_day:
        downloaded_files_list += _download_cyg_single_day(data_year, data_day, list_sc_num, podaac_usr_pass, cyg_data_ver, cyg_data_lvl,
                                                          cygnss_l1_path, check_md5_exist_file)
    return downloaded_files_list


def download_cyg_files_between_date(st_date, end_date, list_sc_num=None, podaac_usr=None, podaac_pass=None, cyg_data_ver=None, cyg_data_lvl='L1',
                                    cygnss_l1_path=None, check_md5_exist_file=False, force_download=False,
                                    save_podaac_pass=True):
    """
    download CYGNSS data between two dates (including start and end date)

    :param st_date: start date
    :type st_date: date
    :param end_date: end date
    :type end_date: date
    :param list_sc_num: list of cygnss spacecraft numbers (1-8), if None will download all SCs
    :type list_sc_num: list or np.array or int
    :param podaac_usr: PODAAC user name. if None, it will ask you to enter it
    :type podaac_usr: str or None
    :param podaac_pass: PODAAC Drive API password. if None, it will ask you to enter it
    :type podaac_pass: str or None
    :param cyg_data_ver: cygnss data version (ex: 'v2.1')
    :type cyg_data_ver: str
    :param cyg_data_lvl: cygnss data level (ex: 'L1')
    :type cyg_data_lvl: str
    :param cygnss_l1_path: path of the cygnss L1 data (default: os.environ.get('CYGNSS_L1_PATH'))
    :type cygnss_l1_path: str or None
    :param check_md5_exist_file: check md5 checksum for existing files? this will make it very slow
    :type check_md5_exist_file: bool
    :param force_download: download the file even if the version is not included in the path (not recommended)
    :param save_podaac_pass: save podaac username and pass in your system? (select False if you're using a shared or public PC)
    :type save_podaac_pass: bool
    :return:
    """
    if cygnss_l1_path is None:
        cygnss_l1_path = os.environ.get('CYGNSS_L1_PATH')
    if list_sc_num is None:
        list_sc_num = np.arange(1, 9)
    elif np.size(list_sc_num) == 1:
        list_sc_num = [int(list_sc_num)]
    if cygnss_l1_path is None:
        raise ValueError("$CYGNSS_L1_PATH environment variable need to be set, or use cygnss_l1_path input parameter")
    if cyg_data_ver is None:
        folder_list = cygnss_l1_path.split(os.path.sep)
        if not folder_list[-1]:
            folder_list.pop(-1)
        cyg_data_ver = folder_list[-1]
    cyg_data_lvl = cyg_data_lvl.upper()
    podaac_usr_pass = get_podaac_cred(save_pass=save_podaac_pass) if (podaac_usr is None or podaac_pass is None) else (podaac_usr, podaac_pass)

    ver_folder_exist = check_ver_folder(cygnss_l1_path, cyg_data_ver)
    if not force_download and not ver_folder_exist:
        error_str = f"You are trying to download version {cyg_data_ver:s}, but the path doesn't contain the ver name ({cygnss_l1_path:s})"
        raise ValueError(f'{error_str:s}\nuse force_download=True to remove this error')

    num_days = (end_date - st_date).days + 1
    downloaded_files_list = list()
    for iday in range(0, num_days):
        data_date = st_date + dt.timedelta(days=iday)
        data_year = data_date.year
        data_day = data_date.timetuple().tm_yday
        downloaded_files_list += _download_cyg_single_day(data_year, data_day, list_sc_num, podaac_usr_pass, cyg_data_ver, cyg_data_lvl,
                                                          cygnss_l1_path, check_md5_exist_file)
    return downloaded_files_list


def _download_cyg_single_day(data_year, data_day, list_sc_num, podaac_usr_pass, cyg_data_ver, cyg_data_lvl, cygnss_l1_path,
                             check_md5_exist_file=False, silent_run=False):
    """
    download a single day, access this function from download_cyg_files()
    :param data_year: data year
    :type data_year: int
    :param data_day: data day of the year
    :type data_day: int
    :param list_sc_num: list of cygnss spacecraft numbers (1-8), if None will download all SCs
    :type list_sc_num: list or np.array or int
    :param podaac_usr_pass: PODAAC user name and pass (usr name, pass)
    :type podaac_usr_pass: tuple of string
    :param cyg_data_ver: cygnss data version (ex: 'v2.1')
    :type cyg_data_ver: str
    :param cyg_data_lvl: cygnss data level (ex: 'L1')
    :type cyg_data_lvl: str
    :param cygnss_l1_path: path of the cygnss L1 data
    :type cygnss_l1_path: str
    :param check_md5_exist_file: check md5 checksum for existing files? this will make it very slow
    :type check_md5_exist_file: bool
    :param silent_run: if true no screen output will be shown except downloading progress and errors
    :type silent_run: bool
    :return:
    """

    cyg_day_folder = os.path.join(cygnss_l1_path, f'{data_year:04d}', f'{data_day:03d}')
    # if not os.path.isdir(cyg_day_folder):  # commented so we don't create folders for days without data
    #     os.makedirs(cyg_day_folder, exist_ok=True)
    cyg_day_folder_url = f'{PODAAC_CYG_URL:s}/{cyg_data_lvl:s}/{cyg_data_ver:s}/{data_year:04d}/{data_day:03d}/'
    day_page_data = _get_cyg_page_data(cyg_day_folder_url, podaac_usr_pass)
    file_name_list = list()
    for sc_num in list_sc_num:
        download_file_tf = False
        disk_cyg_file_name = get_cyg_file(cyg_day_folder, sc_num)
        cyg_md5_checksum = None
        cyg_file_name = None
        if check_md5_exist_file:
            cyg_file_name, cyg_md5_checksum = _get_md5_file(day_page_data, sc_num, cyg_day_folder_url, podaac_usr_pass)
            if cyg_file_name is None:  # No md5 ==> no cygnss file
                print(f"File doesn't exist in the PODAAC, year:{data_year:04d}, day:{data_day:03d}, sc_num: {sc_num:02d}")
                continue
            if disk_cyg_file_name is not None:
                cyg_file_full_path = os.path.join(cyg_day_folder, disk_cyg_file_name)
                # file_size = os.path.getsize(cyg_file_full_path)
                # file_name = cyg_file_name
                if cyg_file_name != disk_cyg_file_name:
                    os.remove(cyg_file_full_path)
                    download_file_tf = True
                else:
                    file_checksum = checksum(cyg_file_full_path)
                    if file_checksum != cyg_md5_checksum:
                        print('disk version of cygnss file failed md5 checksum test, re-downloading the file again')
                        os.remove(cyg_file_full_path)
                        download_file_tf = True

        file_name = None
        if not download_file_tf:
            if disk_cyg_file_name is None:
                download_file_tf = True
            else:
                cyg_file_full_path = os.path.join(cyg_day_folder, disk_cyg_file_name)
                file_size = os.path.getsize(cyg_file_full_path)
                if file_size > CYG_MIN_FILE_SIZE:
                    if not silent_run:
                        print(f'{disk_cyg_file_name:s} file exist')
                else:
                    print(f'{disk_cyg_file_name:s} file size is too small ({int(file_size/1024/1024)} MB), re-downloading the file')
                    os.remove(cyg_file_full_path)
                    download_file_tf = True

        if download_file_tf:
            file_name = download_cyg_file(data_year, data_day, sc_num, cyg_data_ver, cyg_data_lvl, cyg_day_folder, podaac_usr_pass=podaac_usr_pass,
                                          day_page_data=day_page_data, cyg_file_name=cyg_file_name, cyg_md5_checksum=cyg_md5_checksum)
        if file_name is not None:
            file_name_list.append(file_name)

    return file_name_list


def get_cyg_file(cyg_day_folder, sc_num):
    """
    check if the file exist and return the file name, if not exist return None

    :param cyg_day_folder: cygnss day folder
    :type cyg_day_folder: str
    :param sc_num: spacecraft number
    :type sc_num: int
    :return: file name
    :rtype: str
    """
    result = []
    pattern = f"cyg{sc_num:02d}*.nc"
    for root, dirs, files in os.walk(cyg_day_folder):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(name)
                break  # finding the first file

    if len(result) == 0:
        cyg_file_name = None
    else:
        cyg_file_name = result[0]

    return cyg_file_name


def check_ver_folder(cygnss_l1_path, cyg_data_ver):
    """
    check if the version name in the path

    :param cygnss_l1_path: path of the cygnss L1 data
    :type cygnss_l1_path: str
    :param cyg_data_ver: cygnss data version (ex: 'v2.1')
    :type cyg_data_ver: str
    :return:
    """
    path_split = cygnss_l1_path.split(os.sep)
    if cyg_data_ver in path_split:
        out = True
    else:
        warnings.warn(f"You are trying to download version {cyg_data_ver:s}, but the path doesn't contain the version name", RuntimeWarning)
        out = False
    return out


def get_podaac_cred(pass_folder=None, save_pass=True, reset_pass=False):
    """
    import podaac username and pass from the system, if not found it ask you to enter them

    :return:
    """
    if reset_pass:
        mixil_keys = MixilKeys(pass_folder=pass_folder)
        mixil_keys.remove('podaac_usr')
        mixil_keys.remove('podaac_pass')
        del mixil_keys

    if save_pass:
        mixil_keys = MixilKeys(pass_folder=pass_folder)
        mixil_keys.require('podaac_usr', msg='Get PODAAC API Credentials from: https://podaac-tools.jpl.nasa.gov/drive/ \nPO.DAAC Username: ')
        mixil_keys.require('podaac_pass', msg='PO.DAAC Drive API Password: ')
        podaac_usr = mixil_keys.retrieve('podaac_usr')
        podaac_pass = mixil_keys.retrieve('podaac_pass')
    else:
        podaac_usr = getpass('PO.DAAC Username: ')
        podaac_pass = getpass('PO.DAAC Drive API Password: ')

    return podaac_usr, podaac_pass


if __name__ == "__main__":
    # main()
    # from cygnsslib import cygnss_download
    # import datetime as dt

    # st_date = dt.date(year=2020, month=7, day=1)
    # end_date = dt.date(year=2020, month=12, day=31)
    # cyg_data_ver = 'v2.1'
    # download_cyg_files_between_date(st_date, end_date, cyg_data_ver=cyg_data_ver)
    # os.environ["CYGNSS_L1_PATH"] = '/media/amer/Data/cygnss_data/L1/v3.0'
    st_date = dt.date(year=2019, month=1, day=1)
    end_date = dt.date(year=2019, month=1, day=2)
    cyg_data_ver = 'v3.0'
    download_cyg_files_between_date(st_date, end_date, cyg_data_ver=cyg_data_ver, check_md5_exist_file=False)
