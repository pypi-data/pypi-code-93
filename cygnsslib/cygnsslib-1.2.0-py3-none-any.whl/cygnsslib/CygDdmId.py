from cygnsslib.cyg import get_list_ddm_info_from_kml, cyg_environ_check
from netCDF4 import Dataset
import copy
import fnmatch
import numpy as np
import os
import pandas as pd
import warnings

L1_LAND_FOLDER = "v3Land"
L1_OCEAN_FOLDER = "v3.0"


def get_sample_id_of_different_cyg_version(in_cygddmid, new_version, original_cyg_ver=None):
    """


    :param in_cygddmid:
    :type in_cygddmid: CygDdmId
    :param new_version:
    :param original_cyg_ver:
    :return:
    """
    cyg_environ_check()
    if original_cyg_ver is not None:
        original_l1_path = os.path.join(os.environ.get("CYGNSS_PATH"), 'L1', original_cyg_ver)
    else:
        original_l1_path = os.environ.get("CYGNSS_L1_PATH")
    dist_cygnss_l1_path = os.path.join(os.environ.get("CYGNSS_PATH"), 'L1', new_version)
    in_cygddmid.fill_file_name(cygnss_l1_path=original_l1_path)
    cygnss_original_ver_file = os.path.join(original_l1_path, f'{in_cygddmid.year:04d}', f'{in_cygddmid.day:03d}', in_cygddmid.file_name)
    ds_cyg = Dataset(cygnss_original_ver_file, 'r')
    ds_cyg.set_auto_maskandscale(False)
    tcs = pd.Timestamp(ds_cyg.time_coverage_start)
    tcs_in_sec = (tcs - copy.deepcopy(tcs).replace(hour=0, minute=0, second=0, microsecond=0, nanosecond=0)).delta * 1e-9

    # Number of seconds relative to the beginning of the day [sec]. resolution is nano second
    sel_sample_time_sec = ds_cyg.variables['ddm_timestamp_utc'][in_cygddmid.samp_id] + tcs_in_sec
    ds_cyg.close()  # close the file

    # open the land file
    cyg_dis_ver_file_name = find_cygnss_file(data_year=in_cygddmid.year, data_day=in_cygddmid.day, sc_num=in_cygddmid.sc_num,
                                             cygnss_l1_path=dist_cygnss_l1_path)
    dis_ver_file_path = os.path.join(dist_cygnss_l1_path, f'{in_cygddmid.year:04d}', f'{in_cygddmid.day:03d}', cyg_dis_ver_file_name)
    dis_ver_sample_id = get_sample_id_from_time_rltv_tcs(dis_ver_file_path, sel_sample_time_sec)
    dis_ver_cygddmid = CygDdmId(cyg_dis_ver_file_name, in_cygddmid.year, in_cygddmid.day, in_cygddmid.sc_num, in_cygddmid.ch_id, dis_ver_sample_id)
    return dis_ver_cygddmid


def get_land_prod_info_from_ocean_prod(year, day, sc_num, l1_ocean_sample, cygnss_l1_path=None, l1_ocean_folder_name=None,
                                       l1_land_folder_name=None):
    """
    get sample id for land product (v3Land) from the ocean product

    :param year: data year, ex. 2019
    :type year: int
    :param day: day of the year, (1-36X)
    :type day: int
    :param sc_num: spacecraft id, (1-8)
    :type sc_num: int
    :param l1_ocean_sample: sample id of the ocean product (zero-based)
    :type l1_ocean_sample: int
    :param cygnss_l1_path: path of the cygnss L1 data (default: os.environ.get("CYGNSS_L1_PATH"))
    :type cygnss_l1_path: str or None
    :param l1_ocean_folder_name: L1 ocean folder name (default: L1_OCEAN_FOLDER)
    :type l1_ocean_folder_name: str or None
    :param l1_land_folder_name: L1 land folder name (default: L1_LAND_FOLDER)
    :type l1_land_folder_name: str or None
    :return: sample id of the land product (zero-based)
    """
    if cygnss_l1_path is None:
        raise ValueError("$CYGNSS_L1_PATH environment variable need to be set, or use cygnss_l1_path input parameter")

    l1_land_folder_name = L1_LAND_FOLDER if l1_land_folder_name is None else l1_land_folder_name
    l1_ocean_folder_name = L1_OCEAN_FOLDER if l1_ocean_folder_name is None else l1_ocean_folder_name

    cygnss_l1_root_path = uppath(cygnss_l1_path, 1)
    cygnss_l1_land_path = os.path.join(cygnss_l1_root_path, l1_land_folder_name)
    cygnss_l1_ocean_path = os.path.join(cygnss_l1_root_path, l1_ocean_folder_name)

    #  get selected DDM time stamp from the ocean file
    cyg_ocean_file_name = find_cygnss_file(data_year=year, data_day=day, sc_num=sc_num, cygnss_l1_path=cygnss_l1_ocean_path)
    cygnss_ocean_file = os.path.join(cygnss_l1_ocean_path, f'{year:04d}', f'{day:03d}', cyg_ocean_file_name)
    ds_cyg = Dataset(cygnss_ocean_file, 'r')
    ds_cyg.set_auto_maskandscale(False)

    tcs = pd.Timestamp(ds_cyg.time_coverage_start)
    tcs_in_sec = (tcs - copy.deepcopy(tcs).replace(hour=0, minute=0, second=0, microsecond=0, nanosecond=0)).delta * 1e-9
    sel_sample_time = np.array(ds_cyg.variables['ddm_timestamp_utc'][l1_ocean_sample]) + tcs_in_sec  # Number of seconds relative to the beginning of
    # the day [sec]. resolution is nano second

    ds_cyg.close()  # close the file

    # open the land file
    cyg_land_file_name = find_cygnss_file(data_year=year, data_day=day, sc_num=sc_num, cygnss_l1_path=cygnss_l1_land_path)
    cygnss_land_file = os.path.join(cygnss_l1_land_path, f'{year:04d}', f'{day:03d}', cyg_land_file_name)
    l1_land_sample_id = get_sample_id_from_time_rltv_tcs(cygnss_land_file, sel_sample_time)
    return cyg_land_file_name, l1_land_sample_id, sel_sample_time


def find_cygnss_file(data_year, data_day, sc_num, cygnss_l1_path=None):
    """
    find cygnss file name in the folder, raise FileNotFoundError if not found

    :param data_year: data year, ex. 2019
    :type data_year: int
    :param data_day: day of the year, (1-36X)
    :type data_day: int
    :param sc_num: spacecraft id, (1-8)
    :type sc_num: int
    :param cygnss_l1_path: path of the cygnss L1 data (default: os.environ.get("CYGNSS_L1_PATH"))
    :type cygnss_l1_path: str or None
    :return: cygnss file name
    :type: str
    """
    if cygnss_l1_path is None:
        cygnss_l1_path = os.environ.get("CYGNSS_L1_PATH")
        if cygnss_l1_path is None:
            raise ValueError("$CYGNSS_L1_PATH environment variable need to be set, or use cygnss_l1_path input parameter")

    cyg_folder = os.path.join(cygnss_l1_path, f'{data_year:04d}', f'{data_day:03d}')

    result = list()
    pattern = f"cyg{sc_num:02d}*.nc"
    for root, dirs, files in os.walk(cyg_folder):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(name)
    if not result:
        raise FileNotFoundError(f"No file for sc: {sc_num:d} found in {cyg_folder:s}")

    cyg_file_name = result[0]
    return cyg_file_name


def get_sample_id_from_time_rltv_tcs(cyg_full_file, sel_sample_time):
    """
    get sample id (zero-based) from the time (in seconds) of the selected DDM (sample) relative to the time_coverage_start
    :param cyg_full_file: cygnss file
    :type cyg_full_file: str
    :param sel_sample_time: time (in seconds) of the selected DDM (sample) relative to the time_coverage_start
    :type sel_sample_time: float
    :return: L1 sample id (zero-based)
    :type: int
    """
    ds_cyg = Dataset(cyg_full_file, 'r')
    ds_cyg.set_auto_maskandscale(False)

    tcs = pd.Timestamp(ds_cyg.time_coverage_start)
    tcs_in_sec = (tcs - copy.deepcopy(tcs).replace(hour=0, minute=0, second=0, microsecond=0, nanosecond=0)).delta * 1e-9

    sample_time = np.array(ds_cyg.variables['ddm_timestamp_utc']) + tcs_in_sec  # Number of seconds relative to the beginning of the day [sec]
    # resolution is nano second
    ds_cyg.close()

    sel_ddm_tf = np.isclose(sample_time, sel_sample_time, rtol=0, atol=1e-6)  # set atol=1e-9 as the resolution in nano second
    if sel_ddm_tf.sum() > 1:  # if we have two samples with the same time tamp
        raise RuntimeError("Detecting two samples with time sample less than 1 nS.")
    if sel_ddm_tf.sum() == 0:
        warnings.warn(f'No sample with time relative to tcs {sel_sample_time:f} s, in {cyg_full_file:s}')
        l1_sample_id = np.nan
    else:
        l1_sample_id = int(np.where(sel_ddm_tf)[0])
    return l1_sample_id


def uppath(path, n):
    path_split = path.split(os.sep)
    if path_split[-1] == '':
        n += 1
    return os.sep.join(path.split(os.sep)[:-n])


def cyg_id_list_from_kml(in_kml):
    """
    create list of CygDdmId from kml file

    :param str in_kml: kml file
    :return: list of CygDdmId
    :rtype: list of CygDdmId
    """
    ddms_list = get_list_ddm_info_from_kml(in_kml)
    cyg_ddm_id_list = list()
    for ddm_info in ddms_list:
        cyg_ddm_id_list.append(CygDdmId(None, ddm_info['year'], ddm_info['day'], ddm_info['sc_num'], ddm_info['ch_id'], ddm_info['samp_id'],
                                        sample_time_sec=ddm_info['time_rltv_tsc_ns'], ddm_tag=ddm_info['tag']))

    return cyg_ddm_id_list


def cyg_id_list_from_csv(in_xls_file_path: str) -> list:
    if in_xls_file_path.endswith('.csv'):
        df = pd.read_csv(in_xls_file_path)
    else:
        df = pd.read_excel(in_xls_file_path)

    cyg_ddm_id_list = list()
    for idx, ddm_info in df.iterrows():
        cyg_ddm_id_list.append(CygDdmId(None, ddm_info.year, ddm_info.day, ddm_info.spacecraft_num, ddm_info.channel, ddm_info.sample_zero_based))
    return cyg_ddm_id_list


class CygDdmId:

    def __init__(self, file_name, year, day, sc_num, ch_id, samp_id, land_samp_id=None, sample_time_sec=None, land_file_name=None, ddm_tag=None):
        """
        This class hold the info needed to select specific CYGNSS DDM

        :param file_name: file name
        :type file_name: str or None
        :param year: data year, ex. 2019
        :type year: int
        :param day: day of the year, (1-36X)
        :type day: int
        :param sc_num: spacecraft id, (1-8)
        :type sc_num: int
        :param ch_id: channel id (1-4) (one-based)
        :type ch_id: int
        :param samp_id: sample id (zero-based)
        :type samp_id: int
        :param land_samp_id: sample id of the land product (zero-based)
        :type land_samp_id: int or None
        :param sample_time_sec: time (in seconds) of the selected DDM (sample) from the beginning of the day
        :type sample_time_sec: float or None
        :param land_file_name: land product file name
        :type land_file_name: str or None
        """
        if land_samp_id is not None:
            land_samp_id = int(land_samp_id)

        self.file_name = file_name

        self.year = int(year)
        self.day = int(day)
        self.ch_id = int(ch_id)
        self.samp_id = int(samp_id)
        self.sc_num = int(sc_num)
        self.land_samp_id = land_samp_id
        self.sample_time_sec = sample_time_sec  # easy way of identifying sample ID for the different products
        self.land_file_name = land_file_name  # land product file name
        self.ddm_tag = ddm_tag

    def set_land_sample_id(self, land_samp_id):
        """
        set land_samp_id field

        :param land_samp_id: sample id of the land product (zero-based)
        :type land_samp_id: int
        :return:
        """
        self.land_samp_id = int(land_samp_id)

    def set_ddm_time(self, sample_time_sec):
        """
        set sample_time_sec field

        :param sample_time_sec: time (in seconds) of the selected DDM (sample) from the beginning of the day
        :type sample_time_sec: float or None
        :return:
        """
        self.sample_time_sec = sample_time_sec

    def set_land_file_name(self, land_file_name):
        """
        set land_file_name field

        :param land_file_name: land product file name
        :type land_file_name: str
        :return:
        """
        self.land_file_name = land_file_name

    def fill_file_name(self, cygnss_l1_path=None):
        """
        search for the file name and fill the file_name name
        :param cygnss_l1_path: path of the cygnss L1 data (default: os.environ.get("CYGNSS_L1_PATH"))
        :type cygnss_l1_path: str or None
        :return:
        """
        self.file_name = find_cygnss_file(self.year, self.day, self.sc_num, cygnss_l1_path)

    def fill_land_parameters(self, cygnss_l1_path=None, l1_ocean_folder_name=None, l1_land_folder_name=None):
        """
        using samp_id or sample_time_sec as the sample id for the ocean product, this function fill land_samp_id, sample_time_sec,
        land_file_name fields.

        Note only the fields with None value will be filled.

        :param cygnss_l1_path: path of the cygnss L1 data (default: os.environ.get("CYGNSS_L1_PATH"))
        :type cygnss_l1_path: str or None
        :param l1_ocean_folder_name: L1 ocean folder name (default: L1_OCEAN_FOLDER)
        :type l1_ocean_folder_name: str or None
        :param l1_land_folder_name: L1 land folder name (default: L1_LAND_FOLDER)
        :type l1_land_folder_name: str or None
        :return:
        """
        if cygnss_l1_path is None:
            cygnss_l1_path = os.environ.get("CYGNSS_L1_PATH")
            if cygnss_l1_path is None:
                raise ValueError("$CYGNSS_L1_PATH environment variable need to be set, or use cygnss_l1_path input parameter")

        l1_land_folder_name = L1_LAND_FOLDER if l1_land_folder_name is None else l1_land_folder_name
        l1_ocean_folder_name = L1_OCEAN_FOLDER if l1_ocean_folder_name is None else l1_ocean_folder_name
        cygnss_l1_root_path = uppath(cygnss_l1_path, 1)
        cygnss_l1_land_path = os.path.join(cygnss_l1_root_path, l1_land_folder_name)

        if self.land_file_name is None:
            self.land_file_name = find_cygnss_file(data_year=self.year, data_day=self.day, sc_num=self.sc_num, cygnss_l1_path=cygnss_l1_land_path)

        if self.sample_time_sec is not None:
            cygnss_land_file = os.path.join(cygnss_l1_land_path, f'{self.year:04d}', f'{self.day:03d}', self.land_file_name)
            self.land_samp_id = get_sample_id_from_time_rltv_tcs(cyg_full_file=cygnss_land_file, sel_sample_time=self.sample_time_sec)
        else:
            self.land_file_name, self.land_samp_id, self.sample_time_sec = get_land_prod_info_from_ocean_prod(
                self.year, self.day, self.sc_num, self.samp_id, cygnss_l1_path=cygnss_l1_path, l1_ocean_folder_name=l1_ocean_folder_name,
                l1_land_folder_name=l1_land_folder_name)

    def get_utc_time(self):
        """
        Return DDM sample time

        :return: DDM UTC Time
        :rtype: pd.Timestamp
        """
        day_date = pd.Timestamp(self.year, 1, 1) + pd.Timedelta(days=self.day-1)
        ddm_time = day_date + pd.Timedelta(int(self.sample_time_sec * 1e9), 'ns')

        return ddm_time
