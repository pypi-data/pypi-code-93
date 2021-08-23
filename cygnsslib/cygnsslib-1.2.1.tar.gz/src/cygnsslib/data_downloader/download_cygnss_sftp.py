import os.path
import shutil
from getpass import getpass
from typing import Optional, Union
import numpy as np
import paramiko
from cygnsslib.data_downloader.download_cygnss import checksum
from cygnsslib.data_downloader.pass_core import MixilKeys
import time
import pysftp
import tqdm
MAX_CONNECTIONS_TRIES = 4


def find_file_name_in_dir(dir_data: list, data_year: int, data_day: int, sc_num: int, ver_tag: str = '') -> Optional[str]:

    cyg_file_name = None
    tag = f'cyg{sc_num:02d}.'
    endtag = ver_tag + '.nc'
    for item in dir_data:
        if tag in item:
            try:
                ind = item.index(tag)
                item = item[ind:]
                end = item.index(endtag)
            except ValueError:
                continue

            cyg_file_name = item[:end + len(endtag)]
            break
    if cyg_file_name is None:
        print(f"File doesn't exist in the SFTP, year:{data_year:04d}, day:{data_day:03d}, SC: {sc_num:02d}")
        return cyg_file_name

    return cyg_file_name


def check_file_exit(year, day, sc_num, out_main_folder, ver_tag=''):

    dir_path = os.path.join(out_main_folder, f'{year:04d}', f'{day:03d}')
    if not os.path.isdir(dir_path):
        return None
    cyg_file_name = None
    tag = f'cyg{sc_num:02d}.'
    endtag = ver_tag + '.nc'
    for item in os.listdir(dir_path):
        if tag in item and item.endswith(endtag):
            try:
                ind = item.index(tag)
                item = item[ind:]
                end = item.index(endtag)
            except ValueError:
                continue

            cyg_file_name = item[:end + len(endtag)]
            break
    return cyg_file_name


def download_cygnss_data_from_sftp(year: int, list_days: Union[list, np.ndarray], list_sc: Union[list, np.ndarray], out_main_folder: str,
                                   sftp_data_tag: str, data_path_sftp: Optional[str] = None, save_username_pass: bool = True,
                                   reset_pass: bool = False) -> Union[list[str], str, None]:
    """
    download cygnss data from the SFTP server
    :param sftp_data_tag: files tag in the SFTP server, this should be the tag of the file before .nc, i.e. sand265
    :param year: the year of the data
    :param list_days: list of days (has to be the same size as list_sc)
    :param list_sc: list of the spacecrafts numbers (has to be the same size as list_days)
    :param out_main_folder: path of the main folder, this should point to the folder of the version i.e. data/cygnss_data/v3.1a
    :param data_path_sftp: path of the data in the SFTP server, default is /data/cygnss/products/l1. Note there is no backslash at the end
    :param save_username_pass: save your username and pass?
    :param reset_pass: reset the saved data?
    :return: file(s) name or None if no files found
    """

    sftp_host, sftp_username, sftp_pass = get_podaac_cred(pass_folder=None, save_data=save_username_pass, reset_data=reset_pass)
    saved_files_list = list()
    if data_path_sftp is None:
        data_path_sftp = '/data/cygnss/products/l1'
    for _ in range(MAX_CONNECTIONS_TRIES):
        try:
            with pysftp.Connection(sftp_host, username=sftp_username, password=sftp_pass) as sftp:
                debug(f"{time.strftime('%d-%m-%Y %H:%M')} - Connected to SFTP")
                for day, sc_num in zip(list_days, list_sc):
                    file_name_ = check_file_exit(year, day, sc_num, out_main_folder, sftp_data_tag)
                    if file_name_ is not None:
                        print(f'{file_name_} exist')
                        saved_files_list.append(file_name_)
                        continue
                    with sftp.cd(f'{data_path_sftp}/{year:04d}/{day:03d}'):
                        files_list = sftp.listdir()
                        filename = find_file_name_in_dir(files_list, year, day, sc_num, sftp_data_tag)
                        if filename is None:
                            continue

                        folder_path = os.path.join(out_main_folder, f'{year:04d}', f'{day:03d}')
                        if not os.path.isdir(folder_path):
                            os.makedirs(folder_path)
                        file_path = os.path.join(folder_path, filename)
                        file_temp_path = file_path + '.inc'
                        for i_try in range(MAX_CONNECTIONS_TRIES):
                            try:
                                with tqdm.tqdm(desc=f'{filename}', unit='Mb') as pbar:
                                    def _update_pbar(prog, tot):
                                        pbar.total = bytes2mb(tot)
                                        pbar.n = bytes2mb(prog)
                                        pbar.refresh()
                                    sftp.get(filename, file_temp_path, callback=_update_pbar, preserve_mtime=True)
                                server_md5_checksum = sftp.open(filename + '.md5', 'r').read().decode().split(' ')[0]
                                file_checksum = checksum(file_temp_path)
                                if server_md5_checksum != file_checksum:
                                    raise RuntimeError()
                            except RuntimeError:  # MD5 verification failed
                                if i_try < MAX_CONNECTIONS_TRIES:
                                    print("MD5 checksum failed! Trying to re-download it again")
                                    os.remove(file_temp_path)
                                else:
                                    print("MD5 checksum failed!")
                                    shutil.move(file_temp_path, file_path)  # rename file
                                    break
                            else:  # if it was successful
                                shutil.move(file_temp_path, file_path)  # rename file
                                break
                    saved_files_list.append(filename)

        except (paramiko.SSHException, EOFError, paramiko.ssh_exception.SSHException, paramiko.SFTPError) as e:
            print(e, 'waiting 5 sec')
            time.sleep(5)
        else:
            break
    if not saved_files_list:
        return None

    if len(saved_files_list) > 1:
        return saved_files_list
    else:
        return saved_files_list[0]


def debug(msg: str):
    print(msg)


def bytes2mb(size_byte): return np.around(float(size_byte) / 1048576, decimals=2)


def get_podaac_cred(pass_folder=None, save_data=True, reset_data=False) -> tuple[str, str, str]:
    """
    import podaac username and pass from the system, if not found it ask you to enter them

    :return:
    """
    if reset_data:
        mixil_keys = MixilKeys(pass_folder=pass_folder)
        mixil_keys.remove('cygnss_sftp_host')
        mixil_keys.remove('cygnss_sftp_username')
        mixil_keys.remove('cygnss_sftp_pass')
        del mixil_keys

    if save_data:
        mixil_keys = MixilKeys(pass_folder=pass_folder)
        mixil_keys.require('cygnss_sftp_host', msg='CYGNSS Host IP/URL: ', is_password=False)
        mixil_keys.require('cygnss_sftp_username', msg='username: ', is_password=False)
        mixil_keys.require('cygnss_sftp_pass', msg='password: ', is_password=True)
        sftp_host = mixil_keys.retrieve('cygnss_sftp_host')
        sftp_username = mixil_keys.retrieve('cygnss_sftp_username')
        sftp_pass = mixil_keys.retrieve('cygnss_sftp_pass')
    else:
        sftp_host = input('CYGNSS Host IP/URL: ')
        sftp_username = input('username: ')
        sftp_pass = getpass('password: ')

    return sftp_host, sftp_username, sftp_pass

