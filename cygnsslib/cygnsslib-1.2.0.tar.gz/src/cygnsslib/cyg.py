#!/usr/bin/env python3

#  FILE     cyg.py
#  DESCRIPTION
#           Tool set for working with CYGNSS data
#           See <https://bitbucket.org/usc_mixil/cygnss-library>
#  AUTHOR   James D. Campbell
#           Microwave Systems, Sensors and Imaging Lab (MiXiL)
#           University of Southern California
#  EMAIL    jamesdca@usc.edu
#  CREATED  2018-04-06
#  Updated  2020-06-10 by Amer Melebari (amelebar@usc.edu)
#
#  Copyright 2020 University of Southern California
import matplotlib.colors
from osgeo import gdal, ogr
from cygnsslib.data_downloader.download_cygnss import get_cyg_file, download_cyg_files
from geographiclib.geodesic import Geodesic
from lxml import etree
import cygnsslib.istarmap  # fix for tqdm with multiprocessing
from multiprocessing import Pool
from netCDF4 import Dataset
from tqdm import tqdm
from typing import Union, Optional
import datetime
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import warnings


def cyg_environ_check():
    if os.environ.get("CYGNSS_L1_PATH") is None:
        if os.environ.get('CYGNSS_DEFAULT_VER') is None or os.environ.get('CYGNSS_PATH') is None:
            raise ValueError("$CYGNSS_L1_PATH environment variable need to be set, or use cygnss_l1_path input parameter")
        else:
            os.environ['CYGNSS_L1_PATH'] = os.path.join(os.environ['CYGNSS_PATH'], 'L1', os.environ['CYGNSS_DEFAULT_VER'])
    if os.environ.get('CYGNSS_PATH') is None:
        os.environ['CYGNSS_PATH'] = os.sep.join(os.environ.get("CYGNSS_L1_PATH").split(os.sep)[:-2])
    if os.environ.get('CYGNSS_DEFAULT_VER') is None:
        os.environ['CYGNSS_DEFAULT_VER'] = os.environ.get("CYGNSS_L1_PATH").split(os.sep)[-1]


def check_cyg_quality(qflags_list, sp_rx_gain=1):
    """

    :param qflags_list:
    :type qflags_list: list of str
    :param sp_rx_gain: SP Rx gain
    :type sp_rx_gain: float
    :return:
    """
    lvl_1_flags = ['rfi_detected', 'direct_signal_in_ddm']
    lvl_2_flags = ['s_band_powered_up', 'small_sc_attitude_err', 'large_sc_attitude_err', 'black_body_ddm', 'ddmi_reconfigured',
                   'spacewire_crc_invalid', 'ddm_is_test_pattern', 'channel_idle', 'large_step_lna_temp', 'sp_non_existent_error']
    out_flag = 0 if sp_rx_gain > 0 else 2
    for flag_msg in qflags_list:
        if out_flag == 2:  # if we found lvl 2 flag, exit the loop
            break
        for flag in lvl_2_flags:
            if flag in flag_msg:
                out_flag = 2
                break
        if out_flag != 2:
            for flag in lvl_1_flags:
                if flag in flag_msg:
                    out_flag = 1
                    break
    return out_flag


def land_flags_check(qflags, sp_rx_gain=1):
    """
    Look up CYGNSS quality control flags for land applications
    :param qflags:
    :param sp_rx_gain: SP Rx gain
    :type sp_rx_gain: float
    :return: land_flag, qflags_tf, err_msg
    """

    err_msg_list = ['poor_overall_quality', 's_band_powered_up', 'small_sc_attitude_err', 'large_sc_attitude_err', 'black_body_ddm',
                    'ddmi_reconfigured', 'spacewire_crc_invalid', 'ddm_is_test_pattern', 'channel_idle', 'low_confidence_ddm_noise_floor',
                    'sp_over_land', 'sp_very_near_land', 'sp_near_land', 'large_step_noise_floor', 'large_step_lna_temp', 'direct_signal_in_ddm',
                    'low_confidence_gps_eirp_estimate', 'rfi_detected', 'brcs_ddm_sp_bin_delay_error', 'brcs_ddm_sp_bin_dopp_error',
                    'neg_brcs_value_used_for_nbrcs', 'gps_pvt_sp3_error', 'sp_non_existent_error', 'brcs_lut_range_error', 'ant_data_lut_range_error',
                    'bb_framing_error', 'fsw_comp_shift_error']
    qflags_tf = np.copy(qflags).astype(bool)
    qflags_tf = qflags_tf.fill(False)
    # idx 0,10,11,12 are flags for land
    non_land_flag_idx = np.append(np.arange(1, 10), np.arange(13, 27)).astype(int)
    qflags_msg_list = list()
    for flag_idx in non_land_flag_idx:
        if qflags.size < 2 and (qflags & (1 << flag_idx)):
            qflags_msg_list.append(err_msg_list[flag_idx])

        qflags_tf = np.logical_or(qflags & (1 << flag_idx), qflags_tf)

    land_flag = np.array(qflags & (1 << 10), dtype=bool)  # report is the sp over land
    our_flags = check_cyg_quality(qflags_msg_list, sp_rx_gain)
    if sp_rx_gain <= 0.0:
        qflags_msg_list.append('negative_sp_rx_gain')
    return qflags_msg_list, land_flag, our_flags


def write_sp_within_radius(cygnss_l1_dir: Optional[str], year: int, daylist: Union[list[int], np.ndarray, int], ref_pos: tuple[float, float],
                           radius: float, out_folder_path: str, out_file_tag: str, thresh_ddm_snr: float = -9999.0, plt_thresh_noise: float = 1.0,
                           download_cygnss_data: bool = True, out_options: Optional[dict] = None,
                           save_podaac_pass: bool = True) -> tuple[str, str, str]:
    """
        This  search for all CYGNSS DDMs within radius from the ref_pos in the daylist time period. It exports the plots of the DDMs with SNR above
        thesh_ddm_snr
    Note: The structure of the folders/files of  CYGNSS date need to be the same as the POO.DAC

    :param cygnss_l1_dir: the path of the main folder of CYGNSS L1 data (after the versions) (if None it uses os.environ.get("CYGNSS_L1_PATH"))
    :param year: year number in 4 digits (ex. 2020) (you can't select multiple years for now
    :param daylist: list of days
    :param ref_pos: [lat,long]
    :param radius: radius of search in m
    :param out_folder_path: output folder path
    :param out_file_tag: tag for all the output files, ex: "out_root"_above_thresh.kml
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :param thresh_ddm_snr: DDM SNR threshold, above this value the DDM map image will be saved
    :param plt_thresh_noise: noise threshold, each pixel in the DDM below this value will be replaced by this value
    :param download_cygnss_data: download CYGNSS L1 data if they're not available ?
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :param save_podaac_pass: save PO DAAC username/password? ignored if download_cygnss_data = False
    :return: high SNR, low SNR, reference kml files paths

    """
    geod = Geodesic.WGS84
    geo_shape = ogr.Geometry(ogr.wkbLinearRing)

    for angle in np.arange(0, 361, 1):
        poly_point = geod.Direct(ref_pos[0], ref_pos[1], angle, radius)
        geo_shape.AddPoint(poly_point["lon2"], poly_point["lat2"])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(geo_shape)
    tf_poly = False
    geo_shape = None

    year = int(year)
    if np.size(daylist) == 1:
        daylist = [int(daylist)]
    date_list = np.zeros(len(daylist), dtype=dt.date)
    for idx, iday in enumerate(daylist):
        date_list[idx] = dt.date(year, month=1, day=1) + dt.timedelta(days=int(iday) - 1)
    out_root = os.path.join(out_folder_path, out_file_tag)
    return _write_sp_from_poly_or_circle(cygnss_l1_dir, date_list, ref_pos, radius, thresh_ddm_snr, plt_thresh_noise, out_root, poly, tf_poly,
                                         download_cygnss_data, out_options, save_podaac_pass)


def write_sp_within_box_between_dates(st_date: dt.date, end_date: dt.date, lat_lim: Union[list[float], np.ndarray],
                                      lon_lim: Union[list[float], np.ndarray], out_folder_path: str, out_file_tag: str,
                                      thresh_ddm_snr: float = -9999.0, plt_thresh_noise: float = 1.0, download_cygnss_data: bool = True,
                                      out_options: Optional[dict] = None, save_podaac_pass: bool = True,
                                      cygnss_l1_dir: Optional[str] = None) -> tuple[str, str, str]:
    geo_shape = ogr.Geometry(ogr.wkbLinearRing)
    lat_lim = np.sort(lat_lim)
    lon_lim = np.sort(lon_lim)

    geo_shape.AddPoint(lon_lim[0], lat_lim[0])
    geo_shape.AddPoint(lon_lim[1], lat_lim[0])
    geo_shape.AddPoint(lon_lim[1], lat_lim[1])
    geo_shape.AddPoint(lon_lim[0], lat_lim[1])
    geo_shape.AddPoint(lon_lim[0], lat_lim[0])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(geo_shape)
    ref_pos = (0.0, 0.0)
    ref_pos[1], ref_pos[0], *_ = poly.Centroid().GetPoint()
    radius = 10
    tf_poly = True
    geo_shape = None

    num_days = (end_date - st_date).days + 1
    date_list = np.zeros(num_days, dtype=dt.date)
    for iday in range(0, num_days):
        date_list[iday] = st_date + dt.timedelta(days=iday)
    out_root = os.path.join(out_folder_path, out_file_tag)
    return _write_sp_from_poly_or_circle(cygnss_l1_dir, date_list, ref_pos, radius, thresh_ddm_snr, plt_thresh_noise, out_root, poly, tf_poly,
                                         download_cygnss_data, out_options, save_podaac_pass)


def write_sp_within_box(year: int, daylist: Union[list[int], np.ndarray, int], lat_lim: Union[list[float], np.ndarray],
                        lon_lim: Union[list[float], np.ndarray], out_folder_path: str, out_file_tag: str,
                        thresh_ddm_snr: float = -9999.0, plt_thresh_noise: float = 1.0, download_cygnss_data: bool = True,
                        out_options: Optional[dict] = None, save_podaac_pass: bool = True,
                        cygnss_l1_dir: Optional[str] = None) -> tuple[str, str, str]:
    geo_shape = ogr.Geometry(ogr.wkbLinearRing)
    lat_lim = np.sort(lat_lim)
    lon_lim = np.sort(lon_lim)

    geo_shape.AddPoint(lon_lim[0], lat_lim[0])
    geo_shape.AddPoint(lon_lim[1], lat_lim[0])
    geo_shape.AddPoint(lon_lim[1], lat_lim[1])
    geo_shape.AddPoint(lon_lim[0], lat_lim[1])
    geo_shape.AddPoint(lon_lim[0], lat_lim[0])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(geo_shape)
    ref_pos = (0.0, 0.0)
    ref_pos[1], ref_pos[0], *_ = poly.Centroid().GetPoint()
    radius = 10
    tf_poly = True
    geo_shape = None

    year = int(year)
    if np.size(daylist) == 1:
        daylist = [int(daylist)]
    date_list = np.zeros(len(daylist), dtype=dt.date)
    for idx, iday in enumerate(daylist):
        date_list[idx] = dt.date(year, month=1, day=1) + dt.timedelta(days=int(iday) - 1)
    out_root = os.path.join(out_folder_path, out_file_tag)
    return _write_sp_from_poly_or_circle(cygnss_l1_dir, date_list, ref_pos, radius, thresh_ddm_snr, plt_thresh_noise, out_root, poly, tf_poly,
                                         download_cygnss_data, out_options, save_podaac_pass)


def write_sp_within_radius_between_dates(cygnss_l1_dir: Optional[str], st_date: dt.date, end_date: dt.date, ref_pos: tuple[float, float],
                                         radius: float, out_folder_path: str, out_file_tag: str, thresh_ddm_snr: float = -9999.0,
                                         plt_thresh_noise: float = 1.0, download_cygnss_data: bool = True, out_options: Optional[dict] = None,
                                         save_podaac_pass: bool = True) -> tuple[str, str, str]:
    """
        This search for all CYGNSS DDMs within radius from the ref_pos from st_date to end_date. It exports the plots of the DDMs with SNR above
        thesh_ddm_snr
    Note: The structure of the folders/files of  CYGNSS date need to be the same as the POO.DAC

    :param cygnss_l1_dir: the path of the main folder of CYGNSS L1 data (after the versions) (if None it uses os.environ.get("CYGNSS_L1_PATH"))
    :param st_date: start date
    :param end_date: end date
    :param ref_pos: [lat,long]
    :param radius: radius of search in m
    :param out_folder_path: output folder path
    :param out_file_tag: tag for all the output files, ex: "out_root"_above_thresh.kml
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :param thresh_ddm_snr: DDM SNR threshold, above this value the DDM map image will be saved
    :param plt_thresh_noise: noise threshold, each pixel in the DDM below this value will be replaced by this value
    :param download_cygnss_data: download CYGNSS L1 data if they're not available ?
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :param save_podaac_pass: save PO DAAC username/password? ignored if download_cygnss_data = False
    :return: high SNR, low SNR, reference kml files paths
    """
    geod = Geodesic.WGS84
    geo_shape = ogr.Geometry(ogr.wkbLinearRing)

    for angle in np.arange(0, 361, 1):
        poly_point = geod.Direct(ref_pos[0], ref_pos[1], angle, radius)
        geo_shape.AddPoint(poly_point["lon2"], poly_point["lat2"])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(geo_shape)
    tf_poly = False
    geo_shape = None

    num_days = (end_date - st_date).days + 1
    date_list = np.zeros(num_days, dtype=dt.date)
    for iday in range(0, num_days):
        date_list[iday] = st_date + dt.timedelta(days=iday)
    out_root = os.path.join(out_folder_path, out_file_tag)

    return _write_sp_from_poly_or_circle(cygnss_l1_dir, date_list, ref_pos, radius, thresh_ddm_snr, plt_thresh_noise, out_root, poly, tf_poly,
                                         download_cygnss_data, out_options, save_podaac_pass)


def write_sp_from_kml(cygnss_l1_dir: Optional[str], year: int, daylist: Union[list[int], np.ndarray], in_kml: str, out_folder_path: str,
                      out_file_tag: str, thresh_ddm_snr: float = -9999.0, plt_thresh_noise: float = 1.0, download_cygnss_data: bool = True,
                      out_options: Optional[dict] = None, save_podaac_pass: bool = True) -> tuple[str, str, str]:
    """
    This  search for all CYGNSS DDMs within the polygon in the in_kml within the daylist time period. It exports the plots of the DDMs with SNR above
    thesh_ddm_snr
    Note: The structure of the folders/files of  CYGNSS date need to be the same as the POO.DAC

    :param cygnss_l1_dir: the path of the main folder of CYGNSS L1 data (after the versions) (if None it uses os.environ.get("CYGNSS_L1_PATH"))
    :type cygnss_l1_dir: str or None
    :param year: year number in 4 digits (ex. 2020) (you can't select multiple years for now
    :type year: int
    :param daylist: list of days
    :type daylist: list or np.array or int
    :param in_kml: name of the kml file that have the poly
    :type in_kml: str
    :param out_folder_path: output folder path
    :param out_file_tag: tag for all the output files, ex: "out_root"_above_thresh.kml
    :param thresh_ddm_snr: DDM SNR threshold, above this value the DDM map image will be saved
    :type thresh_ddm_snr: float
    :param plt_thresh_noise: noise threshold, each pixel in the DDM below this value will be replaced by this value
    :type plt_thresh_noise: float
    :param download_cygnss_data: download CYGNSS L1 data if they're not available ?
    :type download_cygnss_data: bool
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :type out_options: dict or None
    :param save_podaac_pass: save PO DAAC username/password? ignored if download_cygnss_data = False
    :type save_podaac_pass: bool
    :return: high SNR, low SNR, reference kml files paths
    """
    # Read polygon from input file and make longitude positive
    poly = get_poly(in_kml)
    # Find specular points inside polygon and write them to output
    ref_pos = (0.0, 0.0)
    ref_pos[1], ref_pos[0], *_ = poly.Centroid().GetPoint()
    radius = 10
    tf_poly = True
    year = int(year)
    if np.size(daylist) == 1:
        daylist = [int(daylist)]
    date_list = np.zeros(len(daylist), dtype=dt.date)
    for idx, iday in enumerate(daylist):
        date_list[idx] = dt.date(year, month=1, day=1) + dt.timedelta(days=int(iday) - 1)
    out_root = os.path.join(out_folder_path, out_file_tag)

    return _write_sp_from_poly_or_circle(cygnss_l1_dir, date_list, ref_pos, radius, thresh_ddm_snr, plt_thresh_noise, out_root, poly, tf_poly,
                                         download_cygnss_data, out_options, save_podaac_pass)


def write_sp_from_kml_between_dates(cygnss_l1_dir: Optional[str], st_date: dt.date, end_date: dt.date, in_kml: str, out_folder_path: str,
                                    out_file_tag: str, thresh_ddm_snr: float = -9999.0, plt_thresh_noise: float = 1.0,
                                    download_cygnss_data: bool = True, out_options: Optional[dict] = None,
                                    save_podaac_pass: bool = True) -> tuple[str, str, str]:
    """
    This  search for all CYGNSS DDMs within the polygon in the in_kml within the daylist time period. It exports the plots of the DDMs with SNR above
    thesh_ddm_snr
    Note: The structure of the folders/files of  CYGNSS date need to be the same as the POO.DAC

    :param cygnss_l1_dir: the path of the main folder of CYGNSS L1 data (after the versions) (if None it uses os.environ.get("CYGNSS_L1_PATH"))
    :param st_date: start date
    :param end_date: end date
    :param in_kml: name of the kml file that have the poly
    :param out_folder_path: output folder path
    :param out_file_tag: tag for all the output files, ex: "out_root"_above_thresh.kml
    :param thresh_ddm_snr: DDM SNR threshold, above this value the DDM map image will be saved
    :param plt_thresh_noise: noise threshold, each pixel in the DDM below this value will be replaced by this value
    :param download_cygnss_data: download CYGNSS L1 data if they're not available ?
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :param save_podaac_pass: save PO DAAC username/password? ignored if download_cygnss_data = False
    :return: high SNR, low SNR, reference kml files paths

    """
    # Read polygon from input file and make longitude positive
    poly = get_poly(in_kml)
    # Find specular points inside polygon and write them to output
    ref_pos = (0.0, 0.0)
    ref_pos[1], ref_pos[0], *_ = poly.Centroid().GetPoint()
    radius = 10
    tf_poly = True
    num_days = (end_date - st_date).days + 1
    date_list = np.zeros(num_days, dtype=dt.date)
    for iday in range(num_days):
        date_list[iday] = st_date + dt.timedelta(days=iday)
    out_root = os.path.join(out_folder_path, out_file_tag)

    return _write_sp_from_poly_or_circle(cygnss_l1_dir, date_list, ref_pos, radius, thresh_ddm_snr, plt_thresh_noise, out_root, poly, tf_poly,
                                         download_cygnss_data, out_options, save_podaac_pass)


def get_poly(in_kml):
    """
    get the polygon from the kml file and return a geometry class

    :param in_kml: kml file name
    :type in_kml: str
    :return: Geometry class in GDAL
    """
    dvr = ogr.GetDriverByName("KML")
    if not os.path.exists(in_kml):
        raise ImportError("Cannot find file {}".format(in_kml))

    ds_in = dvr.Open(in_kml)
    lyr = ds_in.GetLayer()
    feat = lyr.GetNextFeature()
    geom = feat.GetGeometryRef()
    ring = geom.GetGeometryRef(0)
    for i_pt in range(ring.GetPointCount()):
        pt = ring.GetPoint(i_pt)
        if pt[0] <= 0:
            lon_pos = pt[0] + 360
            ring.SetPoint(i_pt, lon_pos, pt[1])
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    ds_in = None
    return poly


def _write_sp_from_poly_or_circle(cygnss_l1_path: Optional[str], date_list: Optional[list[dt.date], np.ndarray], ref_pos: tuple[float, float],
                                  radius: float, thresh_ddm_snr: float, plt_thresh_noise: float, out_root: str, poly, tf_poly: bool,
                                  download_cygnss_data: bool = True, out_options: Optional[dict] = None,
                                  save_podaac_pass: bool = True) -> tuple[str, str, str]:
    """

    :param cygnss_l1_path: the path of the main folder of CYGNSS L1 data (after the versions) (if None it uses os.environ.get("CYGNSS_L1_PATH"))
    :param date_list: list of dates
    :type date_list: list of dt.date or np.array of dt.date
    :param ref_pos: (lat,long)
    :param radius: radius of search in m
    :param thresh_ddm_snr: DDM SNR threshold, above this value the DDM image will be saved
    :param plt_thresh_noise: noise threshold, each pixel in the DDM below this value will be replaced by this value
    :param out_root: tag for all the output files, ex: "out_root"_above_thresh.kml
    :param poly: Geometry class with the poly to search within
    :type poly: Geometry
    :param download_cygnss_data: download CYGNSS L1 data if they're not available ?
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :param save_podaac_pass: save PO DAAC username/password? ignored if download_cygnss_data = False
    :return: high SNR, low SNR, reference kml files paths
    """

    if out_options is None:
        out_options = dict()

    save_csv = out_options["save_csv"] if ("save_csv" in out_options) else False
    save_ddm_img = out_options["save_ddm_img"] if ("save_ddm_img" in out_options) else True
    plt_tag = out_options["plt_tag"] if ("plt_tag" in out_options) else ""
    title_img_inc_ddm_time = out_options['title_img_inc_ddm_time'] if ("title_img_inc_ddm_time" in out_options) else False
    img_save_type = out_options['img_save_type'] if ("img_save_type" in out_options) else ['png']
    tf_print_screan = not out_options['silent_mode'] if ("silent_mode" in out_options) else True
    pbar_tf = True if not tf_print_screan else False
    pbar_tf = out_options['progress_bar'] if ("progress_bar" in out_options) else pbar_tf
    parallel = out_options['multithreads'] if ('multithreads' in out_options) else False
    save_klm = out_options['save_klm'] if ('save_klm' in out_options) else True
    sp_high_color_name = out_options['sp_kml_color'] if ('sp_kml_color' in out_options) else 'lime'
    save_below_thresh = out_options['save_data_below_threshold'] if ('save_data_below_threshold' in out_options) else True
    sheet_save_type = 'xlsx'
    if 'sheet_type' in out_options:
        if out_options['sheet_type'].lower() == 'csv':
            sheet_save_type = 'csv'

    if cygnss_l1_path is None:
        cygnss_l1_path = os.environ.get("CYGNSS_L1_PATH")
        if cygnss_l1_path is None:
            raise ValueError("$CYGNSS_L1_PATH environment variable need to be set, or use cygnss_l1_path input parameter")

    # Define bounding box containing circle of input radius for efficient data exclusion
    geod = Geodesic.WGS84
    if tf_poly:
        bbox = poly.GetEnvelope()
        ref_pos = [0.0, 0.0]
        ref_pos[1], ref_pos[0], *_ = poly.Centroid().GetPoint()
        radius = 10
    else:
        g_n = geod.Direct(ref_pos[0], ref_pos[1], 0, radius)
        g_e = geod.Direct(ref_pos[0], ref_pos[1], 90, radius)
        g_s = geod.Direct(ref_pos[0], ref_pos[1], 180, radius)
        g_w = geod.Direct(ref_pos[0], ref_pos[1], 270, radius)
        bbox = [g_w["lon2"], g_e["lon2"], g_s["lat2"], g_n["lat2"]]

    # Define style tables
    sp_high_color_hex = matplotlib.colors.cnames.get(sp_high_color_name, default='#00FF00')
    st_high = ogr.StyleTable()
    st_low = ogr.StyleTable()
    st_ref = ogr.StyleTable()
    st_high.AddStyle("sp_normal", f'SYMBOL(c:{sp_high_color_hex},s:1.0,id:"http://maps.google.com/mapfiles/kml/shapes/donut.png")')
    st_high.AddStyle("sp_highlight", f'SYMBOL(c:{sp_high_color_hex},s:1.3,id:"http://maps.google.com/mapfiles/kml/shapes/donut.png")')
    st_low.AddStyle("sp_normal", 'SYMBOL(c:#FF0000,s:1.0,id:"http://maps.google.com/mapfiles/kml/shapes/donut.png")')
    st_low.AddStyle("sp_highlight", 'SYMBOL(c:#FF0000,s:1.3,id:"http://maps.google.com/mapfiles/kml/shapes/donut.png")')
    st_ref.AddStyle("ref_normal", 'SYMBOL(c:#FFFF00,s:1.0,id:"http://maps.google.com/mapfiles/kml/shapes/flag.png")')
    st_ref.AddStyle("ref_highlight", 'SYMBOL(c:#FFFF00,s:1.3,id:"http://maps.google.com/mapfiles/kml/shapes/flag.png")')
    # Open output
    dvr = ogr.GetDriverByName("LIBKML")
    ds_out_high = None
    ds_out_low = None
    out_high = out_root + "_above_thresh.kml"
    out_low = out_root + "_below_thresh.kml"
    if save_klm:
        ds_out_high = dvr.CreateDataSource(out_high)
        ds_out_high.SetStyleTable(st_high)
        if save_below_thresh:
            ds_out_low = dvr.CreateDataSource(out_low)
            ds_out_low.SetStyleTable(st_low)

    df_high = None
    df_low = None
    out_sheet_name_list = [out_root + f"_{tag}_thresh" for tag in ['above', 'below']]
    st_low, st_ref, st_high = None, None, None

    # Iterate over selected CYGNSS datasets
    lookat_range = 35000  # m
    lookat_tilt = 0  # deg
    lyr_options = [f"LOOKAT_LONGITUDE={ref_pos[1]}",
                   f"LOOKAT_LATITUDE={(ref_pos[0])}",
                   f"LOOKAT_RANGE={lookat_range}",
                   f"LOOKAT_TILT={lookat_tilt}",
                   "FOLDER=YES"]

    # create in-situ kml file
    dvr = ogr.GetDriverByName("KML")
    out_ref = out_root + "_search_area.kml"
    ds_out_ref = dvr.CreateDataSource(out_ref)
    ds_out_ref.SetStyleTable(st_ref)
    lyr_name = "search_area"
    lyr = ds_out_ref.CreateLayer(lyr_name, geom_type=ogr.wkbLinearRing)
    lyr.CreateField(ogr.FieldDefn("Name", ogr.OFTString))
    feat = ogr.Feature(lyr.GetLayerDefn())
    feat.SetGeometry(poly)
    feat.SetField("Name", "search area")
    lyr.CreateFeature(feat)
    feat = None
    lyr_ref = None
    lyr = ds_out_ref.CreateLayer("In_Situ_Sensors", geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("Name", ogr.OFTString))
    feat = ogr.Feature(lyr.GetLayerDefn())
    pt_cur = ogr.Geometry(ogr.wkbPoint)
    pt_cur.AddPoint(float(ref_pos[1]), float(ref_pos[0]))
    feat.SetGeometry(pt_cur)
    feat.SetField("Name", "In-Situ Sensors")
    feat.SetStyleString("@ref")
    lyr.CreateFeature(feat)
    feat = None
    lyr = None
    ds_out_ref = None

    if parallel:
        # date_list_ = tqdm(date_list, total=len(date_list), desc='Searching CYGNSS files', unit='day') if pbar_tf else date_list
        pbar = None
        gdal.UseExceptions()
        pnt_list_high = list()
        pnt_list_low = list()

        with Pool() as pool:
            args = ((cygnss_l1_path, i_date, download_cygnss_data, thresh_ddm_snr, bbox, poly, tf_poly,
                     ref_pos, radius, save_podaac_pass, tf_print_screan, save_ddm_img, img_save_type,
                     plt_tag, plt_thresh_noise, title_img_inc_ddm_time) for i_date in date_list)
            if pbar_tf:
                for day_pnt_list_high, day_pnt_list_low in tqdm(pool.istarmap(_find_sp_in_day, args), total=len(date_list),
                                                                desc='Searching CYGNSS files', unit='day'):
                    if day_pnt_list_high:
                        pnt_list_high += day_pnt_list_high
                    if day_pnt_list_low:
                        pnt_list_low += day_pnt_list_low
            else:
                for day_pnt_list_high, day_pnt_list_low in pool.starmap(_find_sp_in_day, args):
                    if day_pnt_list_high:
                        pnt_list_high += day_pnt_list_high
                    if day_pnt_list_low:
                        pnt_list_low += day_pnt_list_low
        del args, day_pnt_list_high, day_pnt_list_low
    else:
        pbar = tqdm(total=len(date_list) * 8, desc='Searching CYGNSS files', unit='file') if pbar_tf else None
        pnt_list_high = list()
        pnt_list_low = list()
        for i_date in date_list:
            day_pnt_list_high, day_pnt_list_low = _find_sp_in_day(cygnss_l1_path, i_date, download_cygnss_data, thresh_ddm_snr, bbox, poly, tf_poly,
                                                                  ref_pos, radius, save_podaac_pass, tf_print_screan, save_ddm_img, img_save_type,
                                                                  plt_tag, plt_thresh_noise, title_img_inc_ddm_time, pbar)
            if day_pnt_list_high:
                pnt_list_high += day_pnt_list_high
            if day_pnt_list_low:
                pnt_list_low += day_pnt_list_low
    if pbar is not None:
        pbar.close()
    if save_below_thresh:
        ds_out_low, df_low = _export_sp_points(pnt_list_low, ds_out_low, lyr_options, save_klm, save_csv)
        ds_out_low = None
    ds_out_high, df_high = _export_sp_points(pnt_list_high, ds_out_high, lyr_options, save_klm, save_csv)
    ds_out_high = None

    if save_klm:
        add_look_at(out_high, ref_pos, lookat_tilt, lookat_range)
        if save_below_thresh:
            add_look_at(out_low, ref_pos, lookat_tilt, lookat_range)
    if save_csv:
        for df, fname in zip((df_high, df_low), out_sheet_name_list):
            if df is not None:
                if sheet_save_type == 'csv':
                    df.to_csv(f'{fname}.csv', index=False)
                else:
                    try:
                        df.to_excel(f'{fname}.xlsx', index=False)
                    except ValueError:
                        warnings.warn(f'cannot save data into xlsx file as the number of rows exceeded Excel limit. saving into {fname}.csv')
                        df.to_csv(f'{fname}.csv', index=False)
    pt_cur = None
    geod = None
    return out_high, out_low, out_ref


def _export_sp_points(pnt_list: list[dict], ds_out, lyr_options, save_klm: bool, save_csv: bool) -> tuple[ogr.DataSource, Optional[pd.DataFrame]]:
    df_data = None
    if not pnt_list:
        print('No SP found in the selected region')
        return ds_out, df_data
    if save_klm:
        for lyr_ in pnt_list:
            lyr = ds_out.CreateLayer(lyr_['lyr_name'], options=lyr_options, geom_type=ogr.wkbPoint)
            lyr.CreateField(ogr.FieldDefn("Name", ogr.OFTString))
            lyr.CreateField(ogr.FieldDefn("description", ogr.OFTString))
            for pnt_ in lyr_['points']:
                feat = ogr.Feature(lyr.GetLayerDefn())
                pt_cur = ogr.Geometry(ogr.wkbPoint)
                pt_cur.AddPoint(pnt_['ddm_data']['sp_lon'], pnt_['ddm_data']['sp_lat'])
                feat.SetField("Name", f"{pnt_['ddm_data']['sample_zero_based']}")
                feat.SetField('description', pnt_['dec'])
                feat.SetGeometry(pt_cur)
                feat.SetStyleString("@sp")
                lyr.CreateFeature(feat)
                feat = None
            lyr = None
    if save_csv:
        out_dic = dict()
        for keys in pnt_list[0]['points'][0]['ddm_data'].keys():
            out_dic[keys] = list()
        for lyr_ in pnt_list:
            for pnt_ in lyr_['points']:
                for keys, item in pnt_['ddm_data'].items():
                    out_dic[keys].append(item)

        df_data = pd.DataFrame(out_dic)

    return ds_out, df_data


def _find_sp_in_day(cygnss_l1_path: str, i_date: datetime.date, download_cygnss_data: bool, thresh_ddm_snr: float, bbox: list,
                    poly: ogr.Geometry, tf_poly: bool, ref_pos: Union[list, np.ndarray], radius: float, save_podaac_pass: bool,
                    tf_print_screan: bool, save_ddm_img: bool, img_save_type: Union[list, np.ndarray], plt_tag: str, plt_thresh_noise: float,
                    title_img_inc_ddm_time: str, pbar: Optional[tqdm] = None) -> tuple[list, list]:
    geod = Geodesic.WGS84
    day_pnt_list_high = list()
    day_pnt_list_low = list()
    day = i_date.timetuple().tm_yday
    cyg_day_folder = os.path.join(cygnss_l1_path, f'{i_date.year:04d}', f'{day:03d}')
    for sc_num in np.arange(1, 9):
        if pbar is not None:
            pbar.update()
        filename = get_cyg_file(cyg_day_folder, sc_num)
        if filename is None and download_cygnss_data:
            file_name = download_cyg_files(i_date.year, day, sc_num, cygnss_l1_path=cygnss_l1_path, save_podaac_pass=save_podaac_pass)
            filename = None if (not file_name) else file_name[0]

        if filename is None:
            continue
        if tf_print_screan:
            print(filename)
        fullfile = os.path.join(cyg_day_folder, filename)
        try:
            nc_file = Dataset(fullfile)

        except OSError as e:
            print(e)
            raise RuntimeError(f'Mostly, the file is damaged, try to re-download it again \n file path {fullfile}')
        nc_file.set_auto_maskandscale(False)
        tsc = nc_file.time_coverage_start
        ddm_timestamp_utc = nc_file.variables["ddm_timestamp_utc"]
        sample = nc_file.variables["sample"]
        sc_num = nc_file.variables["spacecraft_num"]
        sp_lat = np.array(nc_file.variables["sp_lat"])
        sp_lon = np.array(nc_file.variables["sp_lon"])
        sp_inc_angle = nc_file.variables["sp_inc_angle"]
        ddm_snr = nc_file.variables["ddm_snr"]
        brcs = nc_file.variables["brcs"]
        n_delay = nc_file.dimensions["delay"].size
        n_doppler = nc_file.dimensions["doppler"].size
        sp_lon_rolled = sp_lon[:]
        tf_rolled = sp_lon[:] > 180.0
        sp_lon_rolled[tf_rolled] = sp_lon_rolled[tf_rolled] - 360.0
        tf_in_box = (sp_lat[:] > bbox[2]) & (sp_lat[:] < bbox[3]) & (sp_lon_rolled > bbox[0]) & (sp_lon_rolled < bbox[1])
        tf_chan = np.sum(tf_in_box, axis=0) != 0

        for i_chan, tf_hit in enumerate(tf_chan):
            if tf_hit:
                tf_sel = tf_in_box[:, i_chan]
                sample_sel = sample[tf_sel]
                for i_samp in sample_sel:
                    if tf_poly:
                        pt_cur = ogr.Geometry(ogr.wkbPoint)
                        pt_cur.AddPoint(float(sp_lon[i_samp, i_chan]), float(sp_lat[i_samp, i_chan]))
                        sp_is_in_poly = pt_cur.Within(poly)
                        pt_cur = None
                    else:
                        g_dist = geod.Inverse(ref_pos[0], ref_pos[1], float(sp_lat[i_samp, i_chan]), float(sp_lon_rolled[i_samp, i_chan]))["s12"]
                        sp_is_in_poly = g_dist < radius
                        if sp_is_in_poly and tf_print_screan:
                            print(f'(dist={g_dist:2.0f} m)(ddm_snr={ddm_snr[i_samp, i_chan]:2.1f} dB)')

                    if sp_is_in_poly:
                        if ddm_snr[i_samp, i_chan] < thresh_ddm_snr:
                            pnt_list = day_pnt_list_low
                        else:
                            pnt_list = day_pnt_list_high
                        lyr_name = f"yr{i_date.year:04d}_day{day:03d}_sc{sc_num[0]}_ch{i_chan + 1}"
                        if not pnt_list or pnt_list[-1]['lyr_name'] != lyr_name:  # new lyr
                            pnt_list.append({'lyr_name': lyr_name, 'points': []})
                        timestamp_utc = np.timedelta64(int(ddm_timestamp_utc[i_samp] * 1e9), 'ns') + np.datetime64(tsc)
                        timestamp_utc_str = np.datetime_as_string(timestamp_utc)
                        qflags = np.array(nc_file.variables["quality_flags"][i_samp, i_chan])
                        qflags_msg_list, land_flag, our_flags = land_flags_check(qflags, nc_file.variables["sp_rx_gain"][i_samp, i_chan])
                        description_field = [f'Year: {i_date.year:4d}', f'Day: {day:03d}', f'SC: {sc_num[0]:d}',
                                             f'Ch: {i_chan + 1:d}', f'Sample Id: {i_samp:d}',
                                             f'SNR: {ddm_snr[i_samp, i_chan]:.2f} dB',
                                             f'Incident Angle: {sp_inc_angle[i_samp, i_chan]:.2f} deg',
                                             f'Time form TSC: {int(ddm_timestamp_utc[i_samp] * 1e9):d} ns',
                                             f'DDM time: {timestamp_utc_str:s}', f'DDM quality: {our_flags:d}']
                        ddm_data = {'ddm_timestamp_utc_str': timestamp_utc_str,
                                    'year': i_date.year,
                                    'day': day,
                                    'spacecraft_num': int(sc_num[0]),
                                    'channel': int(i_chan + 1),
                                    'sample_zero_based': int(i_samp),
                                    'sp_lat': float(sp_lat[i_samp, i_chan]),
                                    'sp_lon': float(sp_lon_rolled[i_samp, i_chan]),
                                    'sp_inc_angle': float(sp_inc_angle[i_samp, i_chan]),
                                    'ddm_snr': float(ddm_snr[i_samp, i_chan]),
                                    'DDM_quality': our_flags,
                                    'is_over_land': bool(land_flag),
                                    'quality_flags_msg': ', '.join(qflags_msg_list)}
                        pnt_list[-1]['points'].append({'ddm_data': ddm_data, 'dec': ','.join(description_field)})
                        if ddm_snr[i_samp, i_chan] >= thresh_ddm_snr and save_ddm_img:  # Save plot of BRCS
                            plot_cyg_brcs(brcs[i_samp, i_chan, :, :], ddm_snr[i_samp, i_chan], ddm_timestamp_utc[i_samp], lyr_name, n_delay,
                                          n_doppler, plt_tag, f"{i_samp}", sp_inc_angle[i_samp, i_chan], plt_thresh_noise, title_img_inc_ddm_time,
                                          img_save_type)
        nc_file.close()
    return day_pnt_list_high, day_pnt_list_low


def plot_cyg_brcs(brcs_sel, ddm_snr, ddm_timestamp_utc, lyr_name, n_delay, n_doppler, plt_tag, pt_name, sp_inc_angle, plt_thresh_noise,
                  title_img_inc_ddm_time, img_save_type):
    tf_noise = brcs_sel < plt_thresh_noise
    brcs_sel[tf_noise] = plt_thresh_noise
    brcs_db = 10 * np.log10(brcs_sel)
    out_png = plt_tag + lyr_name + "_samp" + pt_name
    print(out_png)
    fig, ax = plt.subplots()
    plt.imshow(brcs_db, extent=[0.5, n_doppler + 0.5, n_delay + 0.5, 0.5])
    plt.gca().invert_yaxis()
    plt.colorbar(shrink=0.9)
    img_title = "BRCS [dBsm]\nddm_snr = {:.2f} dB, inc = {:.1f} deg".format(ddm_snr, sp_inc_angle)
    img_title = "{:s}\nddm rltv time: {:d} ns".format(img_title, int(ddm_timestamp_utc * 1e9)) if title_img_inc_ddm_time else img_title
    plt.title(img_title)
    plt.xlabel("Doppler Bin")
    plt.ylabel("Delay Bin")
    plt.xticks(range(1, n_doppler + 1))
    plt.yticks(range(1, n_delay + 1))
    for save_type in img_save_type:
        fig_path = '{:s}.{:s}'.format(out_png.split('.')[0], save_type)
        fig.savefig(fig_path, format=save_type, bbox_inches='tight')

    plt.close(fig)


def extract_parameters_frm_descrp(description_field):
    """

    :param description_field: the description field in the kml file
    :type description_field: str
    :return:
    :rtype: dic
    """
    if description_field == '':
        out_dic = None
    else:
        des_field_lwrcase = description_field.lower()
        year = int(des_field_lwrcase[des_field_lwrcase.find('year:'):].split(',')[0][5:])
        day = int(des_field_lwrcase[des_field_lwrcase.find('day:'):].split(',')[0][4:])
        sc_num = int(des_field_lwrcase[des_field_lwrcase.find('sc:'):].split(',')[0][3:])
        ch_id = int(des_field_lwrcase[des_field_lwrcase.find('ch:'):].split(',')[0][3:])
        samp_id = int(des_field_lwrcase[des_field_lwrcase.find('sample id:'):].split(',')[0][10:])
        snr = float(des_field_lwrcase[des_field_lwrcase.find('snr:'):].split(',')[0][4:-2])
        inc_ang = float(des_field_lwrcase[des_field_lwrcase.find('incident angle:'):].split(',')[0][15:-3])
        time_rltv_tsc_ns = int(des_field_lwrcase[des_field_lwrcase.find('time form tsc:'):].split(',')[0][14:-2])
        ddm_time_str = des_field_lwrcase[des_field_lwrcase.find('ddm time:'):].split(',')[0][10:]
        out_dic = {'year': year, 'day': day, 'sc_num': sc_num, 'ch_id': ch_id, 'samp_id': samp_id, 'snr': snr, 'inc_angl': inc_ang,
                   'time_rltv_tsc_ns': time_rltv_tsc_ns, 'sp_desc': description_field, 'ddm_time': ddm_time_str}

    return out_dic


def add_look_at(filename, ref_pos, lookat_tilt, lookat_range):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(filename, parser)
    root = tree.getroot()
    doc = root.find('Document', namespaces=root.nsmap)
    look_at = etree.SubElement(doc, "LookAt", nsmap=root.nsmap)
    longitude = etree.SubElement(look_at, "longitude", nsmap=root.nsmap)
    longitude.text = "{}".format(ref_pos[1])
    latitude = etree.SubElement(look_at, "latitude", nsmap=root.nsmap)
    latitude.text = "{}".format(ref_pos[0])
    tilt = etree.SubElement(look_at, "tilt", nsmap=root.nsmap)
    tilt.text = "{}".format(lookat_tilt)
    rng = etree.SubElement(look_at, "range", nsmap=root.nsmap)
    rng.text = "{}".format(lookat_range)
    tree.write(filename, pretty_print=True, xml_declaration=True, encoding='UTF-8')


def create_centered_polygon(ref_pos, radius, out_kml, shape="circle"):
    """
    this function create a circle or a square in a kml file

    :param ref_pos: center of the polygon (lat,long)
    :type ref_pos: tuple or list
    :param radius: radius for the circle or half the length of the square [m]
    :type radius: float
    :param out_kml: name of the kml output file
    :type out_kml: str
    :param shape: only two shape are currently implemented; circle and square
    :type shape: str
    :return: file
    """
    geod = Geodesic.WGS84
    geo_shape = ogr.Geometry(ogr.wkbLinearRing)

    angle_inc_list = {"circle": 1, "square": 90}

    for angle in np.arange(0, 361, angle_inc_list[shape]):
        poly_point = geod.Direct(ref_pos[0], ref_pos[1], angle, radius)
        geo_shape.AddPoint(poly_point["lon2"], poly_point["lat2"])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(geo_shape)
    print(poly.Centroid())
    lyr_name = "{}_centered".format(shape)
    dvr = ogr.GetDriverByName("KML")
    ds_out = dvr.CreateDataSource(out_kml)
    lyr = ds_out.CreateLayer(lyr_name, geom_type=ogr.wkbLinearRing)
    feat = ogr.Feature(lyr.GetLayerDefn())
    feat.SetGeometry(poly)
    feat.SetField("Name", "radius of {:.0f}".format(radius))
    lyr.CreateFeature(feat)
    ds_out = None


def create_kml_from_list_points(loc_list, loc_names=None, out_kml="points.kml", lyr_name="points"):
    """
    create kml file from list of positions
    :param loc_list: array: Dim 0: points, dim 1: (lat,long)
    :type loc_list: ndarray
    :param loc_names: list of names, if None the name will be "Point No. d" starting from 1
    :type loc_names: list
    :param out_kml: out kml file name, default points.kml
    :type out_kml: str
    :param lyr_name: layer name, default: points
    :type lyr_name: str
    :return: void
    """

    st_ref = ogr.StyleTable()
    st_ref.AddStyle("ref_normal", 'SYMBOL(c:#FFFF00,s:1.0,id:"http://maps.google.com/mapfiles/kml/shapes/flag.png")')
    st_ref.AddStyle("ref_highlight", 'SYMBOL(c:#FFFF00,s:1.3,id:"http://maps.google.com/mapfiles/kml/shapes/flag.png")')
    cnt_point = np.average(loc_list, axis=0)
    lookat_range = 35000  # m
    lookat_tilt = 0  # deg
    lyr_options = ["LOOKAT_LONGITUDE={}".format(cnt_point[1]),
                   "LOOKAT_LATITUDE={}".format(cnt_point[0]),
                   "LOOKAT_RANGE={}".format(lookat_range),
                   "LOOKAT_TILT={}".format(lookat_tilt),
                   "FOLDER=YES"]

    # Open output
    dvr = ogr.GetDriverByName("LIBKML")
    ds_out_ref = dvr.CreateDataSource(out_kml)
    ds_out_ref.SetStyleTable(st_ref)

    lyr = ds_out_ref.CreateLayer(lyr_name, options=lyr_options, geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("Name", ogr.OFTString))
    point = ogr.Geometry(ogr.wkbPoint)

    for i_loc, loc in enumerate(loc_list):
        feat = ogr.Feature(lyr.GetLayerDefn())
        point.AddPoint(float(loc[1]), float(loc[0]))
        feat.SetGeometry(point)

        pt_name = "Point No. {:d}".format(i_loc + 1) if loc_names is None else "{}".format(loc_names[i_loc])
        feat.SetField("Name", pt_name)
        feat.SetStyleString("@ref")
        lyr.CreateFeature(feat)

    ds_out = None


def get_list_ddm_info_from_kml(in_kml: str) -> list[dict]:
    """
    get DDMs info from the kml file

    :param in_kml: kml file
    :type in_kml: str
    :return: list of dic that contains ddms info
    :rtype: list of dict
    """
    dvr = ogr.GetDriverByName("KML")
    kml_data = dvr.Open(in_kml, 0)
    if kml_data is None:
        raise FileExistsError(f"{in_kml:s} file doesn't exist")

    # get all the points in the KML file
    sp_loc_list = list()
    for lyr in kml_data:
        lyr_name = lyr.GetName()
        lyr_year = None
        lyr_day = None
        lyr_sc = None
        lyr_ch = None
        if 'yr' in lyr_name:
            lyr_year = int(lyr_name.split('yr')[1][0:4])
            lyr_day = int(lyr_name.split('day')[1][0:3])
            lyr_sc = int(lyr_name.split('sc')[1][0:1])
            lyr_ch = int(lyr_name.split('ch')[1][0:1])

        ddm_tag = lyr_name if ('Group'.lower() in lyr_name.lower()) else ''

        for idx, feat in enumerate(lyr):
            # feat_def = feat.GetFieldDefn()
            samp_id = int(feat.GetField('Name')) if str.isalnum(feat.GetField('Name')) else None

            geom = feat.GetGeometryRef()
            num_points = geom.GetPointCount()
            if num_points > 1:
                ValueError('expected one points in {:s}. got {:d}'.format(lyr_name, num_points))

            samp_loc = geom.GetPoint()
            ddm_info = extract_parameters_frm_descrp(feat.GetField('description'))
            if ddm_info is None:
                year = lyr_year
                day = lyr_day
                sc_num = lyr_sc
                ch_id = lyr_ch
                snr = None
                inc_ang = None
                time_rltv_tsc_ns = None
                ddm_time_str = None
            else:
                year = ddm_info['year']
                day = ddm_info['day']
                sc_num = ddm_info['sc_num']
                ch_id = ddm_info['ch_id']
                samp_id = ddm_info['samp_id']
                snr = ddm_info['snr']
                inc_ang = ddm_info['inc_angl']
                time_rltv_tsc_ns = ddm_info['time_rltv_tsc_ns']
                ddm_time_str = ddm_info['ddm_time']

            sp_loc_list.append({'year': year,
                                'day': day,
                                'sc_num': sc_num,
                                'ch_id': ch_id,
                                'samp_id': samp_id,
                                'lat': samp_loc[1],
                                'lon': samp_loc[0],
                                'snr': snr,
                                'inc_angl': inc_ang,
                                'time_rltv_tsc_ns': time_rltv_tsc_ns,
                                'sp_desc': feat.GetField('description'),
                                'ddm_time': ddm_time_str,
                                'tag': ddm_tag})
    return sp_loc_list


def group_sp_within_distance(in_kml, out_kml, max_dist, save_csv=False, sheet_type='xlsx'):
    """
    This function group the SP locations into groups, each group the distance between the points is less than the max distance

    :param in_kml: the kml file name from _write_sp_from_poly_or_circle() function
    :type in_kml: str
    :param out_kml: output kml file name
    :type out_kml: str
    :param max_dist: maximum distance between points within a group
    :type max_dist: float
    :param save_csv: export as a CSV file?
    :type save_csv: bool
    :param sheet_type: save the sheet in CSV or xls format? [CSV, xlsx]
    :type sheet_type: str
    :return:
    """
    sheet_type = 'csv' if sheet_type.lower() == 'csv' else 'xlsx'
    sp_loc_list = get_list_ddm_info_from_kml(in_kml)

    # find SP points within max_dist
    st_ref = ogr.StyleTable()
    for istyle in np.arange(1, 11):
        st_ref.AddStyle("pd{:d}_normal".format(istyle),
                        'SYMBOL(c:#00FF00,s:1.0,id:"http://maps.google.com/mapfiles/kml/paddle/{:d}.png")'.format(istyle))
        st_ref.AddStyle("pd{:d}_highlight".format(istyle),
                        'SYMBOL(c:#00FF00,s:1.3,id:"http://maps.google.com/mapfiles/kml/paddle/{:d}.png")'.format(istyle))

    dvr = ogr.GetDriverByName("LIBKML")
    ds_out_ref = dvr.CreateDataSource(out_kml)
    ds_out_ref.SetStyleTable(st_ref)
    lookat_range = 35000  # m
    lookat_tilt = 0  # deg
    # Open output
    df = None
    if save_csv:
        out_csv_file_name = f"{out_kml.split('.')[0]:s}.{sheet_type:s}"
        df = pd.DataFrame({'group_id': [],
                           'ddm_timestamp_utc_str': [],
                           'year': [],
                           'day': [],
                           'ddm_time_from_tsc_ns': [],
                           'sample_zero_based': [],
                           'spacecraft_num': [],
                           'channel': [],
                           'sp_lat': [],
                           'sp_lon': [],
                           'sp_inc_angle': [],
                           'ddm_snr': []})

    point = ogr.Geometry(ogr.wkbPoint)
    grp_id = 0  # first group start from 1
    geod = Geodesic.WGS84
    loc_in_grp = np.full(len(sp_loc_list), False,
                         dtype=bool)  # to prevent duplication of group, we're only considering level 2 don't come in multiple groups

    for idx1, sp_loc in enumerate(sp_loc_list[:-1]):
        if not loc_in_grp[idx1]:
            grp_exist = False
            loc_in_this_grp = np.full(len(sp_loc_list), False, dtype=bool)  # to prevent duplication in the group

            for idx2 in np.arange(idx1 + 1, len(sp_loc_list)):
                sp_loc2 = sp_loc_list[idx2]
                g_dist = geod.Inverse(sp_loc['lat'], sp_loc['lon'], sp_loc2['lat'], sp_loc2['lon'])
                if g_dist["s12"] <= max_dist:
                    if not grp_exist:
                        grp_exist = True
                        grp_id += 1
                        print(f'Group {grp_id:d}')
                        lyr_name = f'group: {grp_id:d}'
                        lyr_options = [f"LOOKAT_LONGITUDE={sp_loc['lon']}",
                                       f"LOOKAT_LATITUDE={sp_loc['lat']}",
                                       f"LOOKAT_RANGE={lookat_range}",
                                       f"LOOKAT_TILT={lookat_tilt}",
                                       f"FOLDER=YES"]

                        lyr = ds_out_ref.CreateLayer(lyr_name, options=lyr_options, geom_type=ogr.wkbPoint)
                        lyr.CreateField(ogr.FieldDefn("Name", ogr.OFTString))
                        lyr.CreateField(ogr.FieldDefn("description", ogr.OFTString))

                        # add the first point
                        feat = ogr.Feature(lyr.GetLayerDefn())
                        point.AddPoint(sp_loc['lon'], sp_loc['lat'])
                        feat.SetGeometry(point)
                        loc_in_grp[idx1] = True
                        loc_in_this_grp[idx1] = True
                        pt_name = "yr{:04d}_day{:03d}_sc{}_ch{}_samp{}".format(sp_loc['year'], sp_loc['day'], sp_loc['sc_num'], sp_loc['ch_id'],
                                                                               sp_loc['samp_id'])
                        feat.SetField("Name", pt_name)
                        feat.SetField("description", sp_loc['sp_desc'])
                        feat.SetStyleString("@pd{:d}".format(np.mod(grp_id - 1, 10) + 1))
                        lyr.CreateFeature(feat)
                        if save_csv:
                            df = df.append(pd.DataFrame({'group_id': [grp_id],
                                                         'ddm_timestamp_utc_str': [sp_loc['ddm_time']],
                                                         'year': [sp_loc['year']],
                                                         'day': [sp_loc['day']],
                                                         'ddm_time_from_tsc_ns': [sp_loc['time_rltv_tsc_ns']],
                                                         'sample_zero_based': [sp_loc['samp_id']],
                                                         'spacecraft_num': [sp_loc['sc_num']],
                                                         'channel': [sp_loc['ch_id']],
                                                         'sp_lat': [sp_loc['lat']],
                                                         'sp_lon': [sp_loc['lon']],
                                                         'sp_inc_angle': [sp_loc['inc_angl']],
                                                         'ddm_snr': [sp_loc['snr']]}), ignore_index=True)
                    loc_in_grp[idx2] = True
                    if not loc_in_this_grp[idx2]:
                        point.AddPoint(sp_loc2['lon'], sp_loc2['lat'])
                        feat.SetGeometry(point)

                        pt_name = "yr{:04d}_day{:03d}_sc{}_ch{}_samp{}".format(sp_loc2['year'], sp_loc2['day'], sp_loc2['sc_num'], sp_loc2['ch_id'],
                                                                               sp_loc2['samp_id'])
                        feat.SetField("Name", pt_name)
                        feat.SetField("description", sp_loc2['sp_desc'])
                        feat.SetStyleString("@pd{:d}".format(np.mod(grp_id - 1, 10) + 1))
                        lyr.CreateFeature(feat)
                        if save_csv:
                            df = df.append(pd.DataFrame({'group_id': [grp_id],
                                                         'ddm_timestamp_utc_str': [sp_loc['ddm_time']],
                                                         'year': [sp_loc['year']],
                                                         'day': [sp_loc['day']],
                                                         'ddm_time_from_tsc_ns': [sp_loc['time_rltv_tsc_ns']],
                                                         'sample_zero_based': [sp_loc['samp_id']],
                                                         'spacecraft_num': [sp_loc['sc_num']],
                                                         'channel': [sp_loc['ch_id']],
                                                         'sp_lat': [sp_loc['lat']],
                                                         'sp_lon': [sp_loc['lon']],
                                                         'sp_inc_angle': [sp_loc['inc_angl']],
                                                         'ddm_snr': [sp_loc['snr']]}), ignore_index=True)

                        print('    distance to ref. point: {:f} m'.format(g_dist["s12"]))
                        loc_in_this_grp[idx2] = True

                    for idx3 in np.arange(idx1 + 1, len(sp_loc_list)):
                        if not loc_in_this_grp[idx3] and idx3 != idx2:
                            sp_loc3 = sp_loc_list[idx3]
                            g_dist = geod.Inverse(sp_loc2['lat'], sp_loc2['lon'], sp_loc3['lat'], sp_loc3['lon'])
                            if g_dist["s12"] <= max_dist:
                                point.AddPoint(sp_loc3['lon'], sp_loc3['lat'])
                                feat.SetGeometry(point)

                                pt_name = f"yr{sp_loc3['year']:04d}_day{sp_loc3['day']:03d}_sc{sp_loc3['sc_num']}_ch{sp_loc3['ch_id']}" \
                                          f"_samp{sp_loc3['samp_id']}"
                                feat.SetField("Name", pt_name)
                                feat.SetField("description", sp_loc3['sp_desc'])
                                feat.SetStyleString("@pd{:d}".format(np.mod(grp_id - 1, 10) + 1))
                                lyr.CreateFeature(feat)
                                if save_csv:
                                    df = df.append(pd.DataFrame({'group_id': [grp_id],
                                                                 'ddm_timestamp_utc_str': [sp_loc['ddm_time']],
                                                                 'year': [sp_loc['year']],
                                                                 'day': [sp_loc['day']],
                                                                 'ddm_time_from_tsc_ns': [sp_loc['time_rltv_tsc_ns']],
                                                                 'sample_zero_based': [sp_loc['samp_id']],
                                                                 'spacecraft_num': [sp_loc['sc_num']],
                                                                 'channel': [sp_loc['ch_id']],
                                                                 'sp_lat': [sp_loc['lat']],
                                                                 'sp_lon': [sp_loc['lon']],
                                                                 'sp_inc_angle': [sp_loc['inc_angl']],
                                                                 'ddm_snr': [sp_loc['snr']]}), ignore_index=True)
                                loc_in_this_grp[idx3] = True
                                print(f'    distance to ref. point: {g_dist["s12"]:f} m')

    ds_out_ref = None
    if save_csv:
        if sheet_type == 'csv':
            df.to_csv(out_csv_file_name, index=False)
        else:
            df.to_excel(out_csv_file_name, index=False)


def plot_brcs(cygnss_l1_dir, year, day, sc_num, ch_num, samp_num, tag_png, tag_title):
    """
    plotting BRCS of DDM,
    Note: this function is not kept up to date
    :param cygnss_l1_dir:
    :param year:
    :param day:
    :param sc_num:
    :param ch_num:
    :param samp_num:
    :param tag_png:
    :param tag_title:
    :return:
    """
    dirname = os.path.join(cygnss_l1_dir, f'{year:04d}', f'{day:03d}')
    assert os.path.isdir(dirname), f"Cannot find dir {dirname}"
    filelist = [x for x in os.listdir(dirname) if x.endswith('.nc')]
    filelist.sort()
    for filename in filelist:
        fullfile = os.path.join(dirname, filename)
        nc_file = Dataset(fullfile)
        nc_file.set_auto_maskandscale(False)
        nc_sc_num = nc_file.variables["spacecraft_num"]
        sc_num_sel = nc_sc_num[0]
        if sc_num_sel == sc_num:
            sp_lat = nc_file.variables["sp_lat"]
            sp_lon = nc_file.variables["sp_lon"]
            sp_inc_angle = nc_file.variables["sp_inc_angle"]
            brcs_ddm_peak_bin_delay_row = nc_file.variables["brcs_ddm_peak_bin_delay_row"]
            brcs_ddm_peak_bin_dopp_col = nc_file.variables["brcs_ddm_peak_bin_dopp_col"]
            sv_num = nc_file.variables["sv_num"]
            track_id = nc_file.variables["track_id"]
            rx_to_sp_range = nc_file.variables["rx_to_sp_range"]
            tx_to_sp_range = nc_file.variables["tx_to_sp_range"]
            brcs = nc_file.variables["brcs"]
            area_e = nc_file.variables["eff_scatter"]
            n_delay = nc_file.dimensions["delay"].size
            n_doppler = nc_file.dimensions["doppler"].size
            sp_lat_sel = sp_lat[samp_num, ch_num - 1]
            sp_lon_sel = sp_lon[samp_num, ch_num - 1]
            if sp_lon_sel >= 180.0:
                sp_lon_sel -= 360
            i_delay = brcs_ddm_peak_bin_delay_row[samp_num, ch_num - 1]
            i_dopp = brcs_ddm_peak_bin_dopp_col[samp_num, ch_num - 1]
            brcs_sel = brcs[samp_num, ch_num - 1, :, :]
            area_e_sel = area_e[samp_num, ch_num - 1, :, :]
            # el_obj = srtm.get_data()
            # el_meters = el_obj.get_elevation(sp_lat_sel,sp_lon_sel)
            el_meters = None
            if el_meters is None:
                print("Couldn't get the elevation, it's set to 0, mostly its because you're outside the range of srtm.")
                el_meters = 0

            print("Latitude: {0}, Longitude: {1}, Elevation: {2}".format(sp_lat_sel, sp_lon_sel, el_meters))
            sp_lat_dms = gdal.DecToDMS(float(sp_lat_sel), "Lat")
            sp_lon_dms = gdal.DecToDMS(float(sp_lon_sel), "Long")
            rx_to_sp_range_sel = rx_to_sp_range[samp_num, ch_num - 1]
            tx_to_sp_range_sel = tx_to_sp_range[samp_num, ch_num - 1]
            ratio = float(tx_to_sp_range_sel) / (tx_to_sp_range_sel + rx_to_sp_range_sel)
            factor = 4 * np.pi * (rx_to_sp_range_sel * ratio) ** 2
            if i_delay != -99 and i_dopp != -99:
                brcs_peak = brcs_sel[i_delay, i_dopp]
                area_peak = area_e_sel[i_delay, i_dopp]
                area_sp = area_e_sel[8, 5]
            else:
                brcs_peak = 0
                area_peak = 0
                area_sp = 0
            fresnel = brcs_peak / factor
            fig, ax = plt.subplots()
            plt.imshow(brcs_sel, extent=[0.5, n_doppler + 0.5, n_delay + 0.5, 0.5])
            plt.colorbar(shrink=0.9)
            title_str = "BRCS [m^2]: {}\n" \
                        "yr={}, day={:03d}, sc={}, ch={}, samp={}\n" \
                        "sp_lat={}, sp_lon={}\n" \
                        "el={:.0f} m, sp_inc={:.1f} deg, sv_num={}\n" \
                        "pk_delay={}, pk_dopp={}, Reflectivity={:.2g}\n"
            plt.title(title_str.format(tag_title, year, day, sc_num, ch_num, samp_num,
                                       sp_lat_dms, sp_lon_dms,
                                       el_meters, sp_inc_angle[samp_num, ch_num - 1], sv_num[samp_num, ch_num - 1],
                                       i_delay + 1, i_dopp + 1, fresnel))
            plt.xlabel('Doppler Bin')
            plt.ylabel('Delay Bin')
            plt.xticks(range(1, n_doppler + 1))
            plt.yticks(range(1, n_delay + 1))
            out_png = "{}_brcs_yr{}_day{:03d}_sc{}_ch{}_samp{}".format(tag_png, year, day, sc_num, ch_num, samp_num)
            fig.savefig(out_png, bbox_inches='tight')
            plt.close(fig)

            fig, ax = plt.subplots()
            plt.imshow(area_e_sel, extent=[0.5, n_doppler + 0.5, n_delay + 0.5, 0.5])
            plt.colorbar(shrink=0.9)
            title_str = "Effective Area [m^2]: {}\n" \
                        "yr={}, day={:03d}, sc={}, ch={}, samp={}\n" \
                        "sp_lat={}, sp_lon={}\n" \
                        "el={:.0f} m, sp_inc={:.1f} deg, sv_num={}\n" \
                        "pk_delay={}, pk_dopp={}, A_pk={:.2g}, A_sp={:.2g}\n"
            plt.title(title_str.format(tag_title, year, day, sc_num, ch_num, samp_num,
                                       sp_lat_dms, sp_lon_dms,
                                       el_meters, sp_inc_angle[samp_num, ch_num - 1], sv_num[samp_num, ch_num - 1],
                                       i_delay + 1, i_dopp + 1, area_peak, area_sp))
            plt.xlabel('Doppler Bin')
            plt.ylabel('Delay Bin')
            plt.xticks(range(1, n_doppler + 1))
            plt.yticks(range(1, n_delay + 1))
            out_png = "{}_area_yr{}_day{:03d}_sc{}_ch{}_samp{}".format(tag_png, year, day, sc_num, ch_num, samp_num)
            fig.savefig(out_png, bbox_inches='tight')
            plt.close(fig)
