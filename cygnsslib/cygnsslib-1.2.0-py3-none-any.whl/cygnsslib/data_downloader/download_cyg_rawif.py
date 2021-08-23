import datetime as dt
import fnmatch
import numpy as np
import os
import warnings

from cygnsslib.data_downloader.download_cygnss import PODAAC_CYG_URL, _get_cyg_page_data, download_file, download_cyg_files, get_podaac_cred


def download_cyg_rawif(data_year, data_day, sc_num, out_folder, podaac_usr_pass, day_page_data=None, download_l1_data=False):
    """
    download cygnss data raw if files from PODAAC, the username and pass can be obtained from https://podaac-tools.jpl.nasa.gov/drive/
    Don't use this function directly, instead use download_cyg_rawif_files()

    :param data_year: data year (ex. 2019)
    :type data_year: int
    :param data_day: data day number (ex. 130)
    :type data_day: int
    :param sc_num: cygnss spacecraft number (1-8)
    :type sc_num: int
    :param out_folder: folder of the saved output (ex: /cygnss_data/L1/v2.1/2019/020)
    :type out_folder: str
    :param podaac_usr_pass: PODAAC user name and pass (usr name, pass)
    :type podaac_usr_pass: tuple of string
    :param day_page_data: page of the selected day, this to reduce the times the script requests the page from the website, default None
    :type day_page_data: list of str or None
    :param download_l1_data: when there is a Rawif data, download its L1 data with it, env $CYGNSS_L1_PATH var should point to the folder of L1 data.
    :type download_l1_data: bool
    :return: file names
    :rtype: list of str
    """
    _files_flag = np.zeros(2).astype(bool)  # check if both the data file and the metadata file are exist
    if not os.path.isdir(out_folder):
        raise ValueError('Invalid out_folder={} specified'.format(out_folder))

    cyg_folder_url = '{:s}/{:s}/{:s}/{:04d}/{:03d}/'.format(PODAAC_CYG_URL, 'L1', 'raw_if', data_year, data_day)
    cyg_files_url = list()
    if day_page_data is None:
        day_page_data = _get_cyg_page_data(cyg_folder_url, podaac_usr_pass)

    tag = 'cyg{:02d}_raw_if'.format(sc_num)
    endtag = '.bin'
    for item in day_page_data:
        if 'cyg' in item:
            try:
                ind = item.index(tag)
                item = item[ind:]
                end = item.index(endtag)
            except ValueError:
                pass
            else:
                file_name = item[:end + 4]
                if 'data' in file_name and not _files_flag[0]:  # only allow one data file name
                    _files_flag[0] = True
                    cyg_files_url.append('{:s}{:s}'.format(cyg_folder_url, file_name))
                elif 'meta' in file_name and not _files_flag[1]:  # only allow one metadata file name
                    _files_flag[1] = True
                    cyg_files_url.append('{:s}{:s}'.format(cyg_folder_url, file_name))

    if not cyg_files_url:  # if no file
        return None
    if not _files_flag.all():  # if only found the data file or the metadata file
        warnings.warn("couldn't find both data and the metadata files for year: {:04d}, day: {:03d}, sc: {:01d}".format(data_year, data_day, sc_num),
                      RuntimeWarning)
    out_files = list()
    for file_url in cyg_files_url:
        file = download_file(file_url, out_folder, auth=podaac_usr_pass)
        if file is not None:
            out_files.append(file)
    if download_l1_data:
        download_cyg_files(data_year, data_day, sc_num, podaac_usr=podaac_usr_pass[0], podaac_pass=podaac_usr_pass[1])
    return out_files


def download_rawif_cyg_files_between_date(st_date, end_date, list_sc_num=None, podaac_usr=None, podaac_pass=None,
                                          cygnss_l1_path=None, re_download=False, save_podaac_pass=True,
                                          download_l1_data=False):
    """
    download RAWIF CYGNSS data between two dates (including start and end date)

    :param st_date: start date
    :type st_date: dt.date
    :param end_date: end date
    :type end_date: dt.date
    :param list_sc_num: list of cygnss spacecraft numbers (1-8), if None will download all SCs
    :type list_sc_num: list or int or np.array or None
    :param podaac_usr: PODAAC user name. if None, it will ask you to enter it
    :type podaac_usr: str or None
    :param podaac_pass: PODAAC Drive API password. if None, it will ask you to enter it
    :type podaac_pass: str or None
    :param cygnss_l1_path: path of the cygnss L1 data (default: os.environ.get('CYGNSS_L1_PATH')), see description for more details
    :type cygnss_l1_path: str or None
    :param re_download: re-download the file if it exist?
    :type re_download: bool
    :param save_podaac_pass: save podaac username and pass in your system? (select False if you're using a shared or public PC)
    :type save_podaac_pass: bool
    :param download_l1_data: when there is a Rawif data, download its L1 data with it, env $CYGNSS_L1_PATH var should point to the folder of L1 data.
    :type download_l1_data: bool
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

    # check if the folder name is not raw_if, if not, change the folder name
    folder_list = cygnss_l1_path.split(os.path.sep)
    if not folder_list[-1]:
        folder_list.pop(-1)
    if 'raw_if' not in folder_list[-1]:
        folder_list[-1] = 'raw_if'
    cygnss_l1_path = os.sep.join(folder_list)

    podaac_usr_pass = get_podaac_cred(save_pass=save_podaac_pass) if (podaac_usr is None or podaac_pass is None) else (podaac_usr, podaac_pass)

    num_days = (end_date - st_date).days + 1
    for iday in range(0, num_days):
        data_date = st_date + dt.timedelta(days=iday)
        data_year = data_date.year
        data_day = data_date.timetuple().tm_yday
        _download_single_day_rawif(data_year, data_day, list_sc_num, cygnss_l1_path, podaac_usr_pass, re_download, download_l1_data)


def download_cyg_rawif_files(data_year, list_data_day, list_sc_num=None, podaac_usr=None, podaac_pass=None,
                             cygnss_l1_path=None, re_download=False, save_podaac_pass=True, download_l1_data=False):
    """

    download the raw_if cygnss data,
    if cygnss_l1_path or os.environ.get('CYGNSS_L1_PATH') point to a folder with name not "raw_if", it will save the data in a raw_if folder in the
    parent dir.

    :param data_year: list of data years
    :type data_year:  int
    :param list_data_day: list of data days
    :type list_data_day: list or int or np.array
    :param list_sc_num: list of cygnss spacecraft numbers (1-8), if None will download all SCs
    :type list_sc_num: list or int or np.array or None
    :param podaac_usr: PODAAC user name. if None, it will ask you to enter it
    :type podaac_usr: str or None
    :param podaac_pass: PODAAC Drive API password. if None, it will ask you to enter it
    :type podaac_pass: str or None
    :param cygnss_l1_path: path of the cygnss L1 data (default: os.environ.get('CYGNSS_L1_PATH')), see description for more details
    :type cygnss_l1_path: str or None
    :param re_download: re-download the file if it exist?
    :type re_download: bool
    :param save_podaac_pass: save podaac username and pass in your system? (select False if you're using a shared or public PC)
    :type save_podaac_pass: bool
    :param download_l1_data: when there is a Rawif data, download its L1 data with it, env $CYGNSS_L1_PATH var should point to the folder of L1 data.
    :type download_l1_data: bool
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

    # check if the folder name is not raw_if, if not, change the folder name
    folder_list = cygnss_l1_path.split(os.path.sep)
    if not folder_list[-1]:
        folder_list.pop(-1)
    if 'raw_if' not in folder_list[-1]:
        folder_list[-1] = 'raw_if'
    cygnss_l1_path = os.sep.join(folder_list)

    podaac_usr_pass = get_podaac_cred(save_pass=save_podaac_pass) if (podaac_usr is None or podaac_pass is None) else (podaac_usr, podaac_pass)

    for data_day in list_data_day:
        _download_single_day_rawif(data_year, data_day, list_sc_num, cygnss_l1_path, podaac_usr_pass, re_download, download_l1_data)


def _download_single_day_rawif(data_year, data_day, list_sc_num, cygnss_l1_path, podaac_usr_pass, re_download, download_l1_data=False):
    """
    download Rawif data for a single day, don't use this function to download the files, instead use download_cyg_rawif_files() or
    download_rawif_cyg_files_between_date ()

    :param data_year: data year
    :type data_year:  int
    :param data_day: data day number
    :type data_day: int
    :param list_sc_num: list of cygnss spacecraft numbers (1-8)
    :type list_sc_num: list or int or np.array
    :param cygnss_l1_path: main path of the data
    :type cygnss_l1_path: str
    :param podaac_usr_pass: PODAAC user name and pass (usr name, pass)
    :type podaac_usr_pass: tuple of string
    :param re_download: re-download the file if it exist?
    :type re_download: bool
    :param download_l1_data: when there is a Rawif data, download its L1 data with it, env $CYGNSS_L1_PATH var should point to the folder of L1 data.
    :type download_l1_data: bool
    :return:
    """
    cyg_day_folder = os.path.join(cygnss_l1_path, '{:04d}'.format(data_year), '{:03d}'.format(data_day))
    cyg_day_folder_url = '{:s}/{:s}/{:s}/{:04d}/{:03d}/'.format(PODAAC_CYG_URL, 'L1', 'raw_if', data_year, data_day)
    day_page_data = _get_cyg_page_data(cyg_day_folder_url, podaac_usr_pass)
    if not os.path.isdir(cyg_day_folder):
        os.makedirs(cyg_day_folder, exist_ok=True)
    for sc_num in list_sc_num:
        cyg_files_name = get_cyg_rawif_files(cyg_day_folder, sc_num)
        if cyg_files_name is None:
            download_cyg_rawif(data_year, data_day, sc_num, cyg_day_folder, podaac_usr_pass=podaac_usr_pass, day_page_data=day_page_data,
                               download_l1_data=download_l1_data)

        elif re_download:
            for file_name in cyg_files_name:
                cyg_file_full_path = os.path.join(cygnss_l1_path, '{:04d}'.format(data_year), '{:03d}'.format(data_day), file_name)
                os.remove(cyg_file_full_path)
            download_cyg_rawif(data_year, data_day, sc_num, cyg_day_folder, podaac_usr_pass=podaac_usr_pass, day_page_data=day_page_data,
                               download_l1_data=download_l1_data)
        else:
            for file_name in cyg_files_name:
                print('{:s} file exist'.format(file_name))


def get_cyg_rawif_files(cyg_day_folder, sc_num):
    """
    check if the file exist and return the file name, if not exist return None.
    if exist it will return list of the files

    :param cyg_day_folder: cygnss day folder
    :type cyg_day_folder: str
    :param sc_num: spacecraft number
    :type sc_num: int
    :return: file name
    :rtype: str
    """
    _files_flag = np.zeros(2).astype(bool)
    result = []
    pattern = "cyg{:02d}*.bin".format(sc_num)
    for root, dirs, files in os.walk(cyg_day_folder):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(name)

    if len(result) == 0:
        return None
    else:
        files_name_list = list()
        for file_name in result:
            if 'data' in file_name:
                _files_flag[0] = True
                files_name_list.append(file_name)
            elif 'meta' in file_name:
                _files_flag[1] = True
                files_name_list.append(file_name)

    if not _files_flag.all():
        warnings.warn("couldn't find both data and the metadata files in {:s}, sc: {:d}, try to download both".format(cyg_day_folder, sc_num),
                      RuntimeWarning)
        return None

    return files_name_list


if __name__ == '__main__':
    down_start_date = dt.date(year=2020, month=8, day=4)
    down_end_date = dt.date(year=2020, month=8, day=4)
    download_rawif_cyg_files_between_date(down_start_date, down_end_date)
    download_cyg_rawif_files(data_year=2020, list_data_day=227)
