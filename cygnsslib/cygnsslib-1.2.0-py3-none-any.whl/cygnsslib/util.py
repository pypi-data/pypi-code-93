from collections.abc import Iterable
from cygnsslib import get_list_ddm_info_from_kml
from cygnsslib.CygDdmId import CygDdmId, get_sample_id_of_different_cyg_version, cyg_environ_check
from netCDF4 import Dataset
import numpy as np
import os
import pandas as pd


def find_land_prod_sample_id_from_excel(xls_in, xls_out=None, start_col=1, st_row=1, out_sheet_suffix='', land_samp_col=None, timestamp_col=None):
    """

    Read the first sheet and the col. start_col to start_col+4.

    The output file is all the cells with new column: land_sample_zero_based

    :param xls_in: input Excel file
    :type xls_in: str
    :param xls_out: output Excel file name, if None add "_land_prod" to the file
    :type xls_out: str or None
    :param start_col: starting col. the function read start_col to start_col+4
    :type start_col: int
    :param st_row: Starting row, default 1 which is the header
    :type st_row: int
    :param out_sheet_suffix: suffix of the sheet name (NOT file name)
    :type out_sheet_suffix: str
    :param land_samp_col: col number of land_sample_zero_based, if None the default is start_col + 5
    :type land_samp_col: int or None
    :param timestamp_col: write the timestamp to tis col. if None the function will not write the timestamp
    :type timestamp_col: int or None
    :return: output file name
    :rtype: str
    """
    if xls_out is None:
        inxls_list = xls_in.split('.')
        xls_out = f'{inxls_list[0]:s}_land_prod.xlsx'  # car read xlsx and xls but write only to xls

    if not os.path.exists(xls_in):
        raise FileExistsError(f"Input Excel file doesn't exist, {xls_in:s}")
    df = pd.read_excel(xls_in)

    land_samp_list = []
    for i_ddm in df.itertuples():
        try:
            ddm_id = CygDdmId(None, i_ddm.year, i_ddm.day, i_ddm.flight_model, i_ddm.channel, i_ddm.sample_zero_based)
        except AttributeError:
            ddm_id = CygDdmId(None, i_ddm[start_col+1], i_ddm[start_col+2], i_ddm[start_col+3], i_ddm[start_col+4], i_ddm[start_col+5])
        try:
            ddm_id.fill_land_parameters()
        except Exception as e:
            ddm_id.land_samp_id = None
        land_samp_list.append(ddm_id.land_samp_id)

    if land_samp_col is None or land_samp_col < 0:
        try:
            land_samp_col = int(np.where('sample_zero_based' == df.columns)[0][0] + 1)
        except IndexError:
            land_samp_col = start_col + 5
    df.insert(land_samp_col, 'land_sample_zero_based', land_samp_list)
    df.to_excel(xls_out, index=False)


def get_ant_pattern_for_diff_versions(in_kml_xls, kml_cyg_ver, cyg_ver_list, out_xls):
    if in_kml_xls.endswith('.kml'):
        ddm_list = get_list_ddm_info_from_kml(in_kml_xls)
    else:
        try:
            in_df = pd.read_excel(in_kml_xls)
        except pd.Error.ParseError:
            in_df = pd.read_csv(in_kml_xls)
        ddm_list = []
        for i_row, row in in_df.iterrows():
            data = {'year': row.year, 'day': row.day, 'sc_num': row.sc_num, 'ch_id': row.ch_id}
            try:
                data['samp_id'] = row.sample_id
            except AttributeError:
                data['samp_id'] = row.samp_id
            ddm_list.append(data)

    cyg_environ_check()
    if kml_cyg_ver is not None:
        original_l1_path = os.path.join(os.environ.get("CYGNSS_PATH"), 'L1', kml_cyg_ver)
    else:
        original_l1_path = os.environ.get("CYGNSS_L1_PATH")
        kml_cyg_ver = original_l1_path.split(os.sep)[-1]
    if not isinstance(cyg_ver_list, Iterable):
        cyg_ver_list = [cyg_ver_list]
    cyg_ddm_id_list = []
    out_df = pd.DataFrame({'year': [],
                           'day': [],
                           'sc_num': [],
                           'ch_id': [],
                           'lat': [],
                           'lon': [],
                           'sp_inc_angle_deg': [],
                           'utc_time': [],
                           'utc_time_str': [],
                           'original_ver': [],
                           'org_ver_samp_id': [],
                           f'orig_ver_ant_pattern_db': [],
                           'original_ver_gps_eirp': []})
    for ddm_info in ddm_list:
        cyg_ddm_id = CygDdmId(None, ddm_info['year'], ddm_info['day'], ddm_info['sc_num'], ddm_info['ch_id'], ddm_info['samp_id'])
        cyg_ddm_id.fill_file_name(original_l1_path)
        cyg_ddm_id_list.append(cyg_ddm_id)
        cygnss_original_ver_file = os.path.join(original_l1_path, f'{cyg_ddm_id.year:04d}', f'{cyg_ddm_id.day:03d}', cyg_ddm_id.file_name)
        ds_cyg = Dataset(cygnss_original_ver_file, 'r')
        ds_cyg.set_auto_maskandscale(False)
        orig_ant_patt = float(ds_cyg.variables["sp_rx_gain"][cyg_ddm_id.samp_id, cyg_ddm_id.ch_id - 1])
        ddm_time = pd.Timedelta(int(ds_cyg.variables['ddm_timestamp_utc'][cyg_ddm_id.samp_id] * 1e9), 'ns') + pd.Timestamp(ds_cyg.time_coverage_start)
        lat = float(ds_cyg.variables['sp_lat'][cyg_ddm_id.samp_id, cyg_ddm_id.ch_id - 1])
        lon = float(ds_cyg.variables['sp_lon'][cyg_ddm_id.samp_id, cyg_ddm_id.ch_id - 1])
        gps_eirp = float(ds_cyg.variables['gps_eirp'][cyg_ddm_id.samp_id, cyg_ddm_id.ch_id - 1])
        inc_angle = float(ds_cyg.variables['sp_inc_angle'][cyg_ddm_id.samp_id, cyg_ddm_id.ch_id - 1])
        if lon > 180:
            lon -= 360.0
        ds_cyg.close()
        out_df = out_df.append(pd.DataFrame({'year': [ddm_info['year']],
                                             'day': [ddm_info['day']],
                                             'sc_num': [ddm_info['sc_num']],
                                             'ch_id': [ddm_info['ch_id']],
                                             'lat': [lat],
                                             'lon': [lon],
                                             'sp_inc_angle_deg': [inc_angle],
                                             'utc_time': [ddm_time.tz_convert(None)],  # make it tz unaware for Excel
                                             'utc_time_str': [str(ddm_time)],
                                             'original_ver': [kml_cyg_ver],
                                             'org_ver_samp_id': [ddm_info['samp_id']],
                                             'orig_ver_ant_pattern_db': [orig_ant_patt],
                                             'original_ver_gps_eirp': [gps_eirp]
                                             }), ignore_index=True)
    for iver, cyg_ver in enumerate(cyg_ver_list, 1):
        cur_ver_l1_path = os.path.join(os.environ.get("CYGNSS_PATH"), 'L1', cyg_ver)
        ant_patt_list = []
        curr_ver_samp_id = []
        gps_eirp_list = []
        for i_ddm, cyg_ddm_id in enumerate(cyg_ddm_id_list):
            new_cyg_ddm_id = get_sample_id_of_different_cyg_version(cyg_ddm_id, cyg_ver, original_cyg_ver=kml_cyg_ver)
            cygnss_cur_ver_file = os.path.join(cur_ver_l1_path, f'{new_cyg_ddm_id.year:04d}', f'{new_cyg_ddm_id.day:03d}', new_cyg_ddm_id.file_name)
            ds_cyg = Dataset(cygnss_cur_ver_file, 'r')
            ds_cyg.set_auto_maskandscale(False)
            ant_patt = float(ds_cyg.variables["sp_rx_gain"][new_cyg_ddm_id.samp_id, new_cyg_ddm_id.ch_id - 1])
            ddm_time_ns_rltv_tcs = int(ds_cyg.variables['ddm_timestamp_utc'][new_cyg_ddm_id.samp_id] * 1e9)
            ddm_time = pd.Timedelta(ddm_time_ns_rltv_tcs, 'ns') + pd.Timestamp(ds_cyg.time_coverage_start)
            gps_eirp_list.append(float(ds_cyg.variables['gps_eirp'][cyg_ddm_id.samp_id, cyg_ddm_id.ch_id - 1]))
            if ddm_time.tz_convert(None) - out_df.utc_time[i_ddm] > pd.Timedelta(2, 'ns'):
                raise RuntimeError(f'There is something wrong with the code. DDM time of original version is different from the time of this version'
                                   f'\nddm time original ver:{out_df.utc_time[i_ddm]}, this ver{ddm_time}')
            ds_cyg.close()
            ant_patt_list.append(ant_patt)
            curr_ver_samp_id.append(new_cyg_ddm_id.samp_id)
        out_df.insert(len(out_df.columns), f'ver_num{iver}', [cyg_ver] * len(ant_patt_list))
        out_df.insert(len(out_df.columns), f'samp_id_num{iver}', curr_ver_samp_id)
        out_df.insert(len(out_df.columns), f'ant_patt_num{iver}_db', ant_patt_list)
        out_df.insert(len(out_df.columns), f'gps_eirp_num{iver}', gps_eirp_list)
    out_df.to_excel(out_xls, index=True)
    return out_xls


if __name__ == '__main__':
    # xls_in = 'SLV_Z4_thawed_2019.xlsx'
    # find_land_prod_sample_id_from_excel(xls_in, xls_out=None, start_col=1, out_sheet_suffix='', timestamp_col=0)
    # xls_in = 'SLV_Z1_thawed_2019.xlsx'
    # find_land_prod_sample_id_from_excel(xls_in, xls_out=None, st_row=1, start_col=1, out_sheet_suffix='', timestamp_col=0)
    kml_file_path = 'z1_test_v3_samples.xlsx'
    ant_comp_xls = 'z1_test_v3_samples_antt.xlsx'
    get_ant_pattern_for_diff_versions(kml_file_path, kml_cyg_ver='v3.0', cyg_ver_list=['v2.1'], out_xls=ant_comp_xls)
    kml_file_path = '/media/amer/myfiles/cygnss/kml_files/Z1/z1_yr19_aft_aug_above_thresh.kml'
    ant_comp_xls = 'v2v3_ant_com.xlsx'
    get_ant_pattern_for_diff_versions(kml_file_path, kml_cyg_ver='v3.0', cyg_ver_list=['v2.1'], out_xls=ant_comp_xls)