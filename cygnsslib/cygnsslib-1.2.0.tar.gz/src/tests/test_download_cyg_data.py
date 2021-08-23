import os

import cygnsslib.data_downloader.download_cyg_rawif

try:
    from cygnsslib import cygnss_download
except ImportError:
    import sys
    parent_dir_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    sys.path.insert(0, parent_dir_path)
    from cygnsslib import cygnss_download
import numpy as np
import datetime as dt

if __name__ == '__main__':

    # data_day = np.arange(5, 10)
    data_year = 2020
    # sc_num = 3
    # sc_num = None
    check_md5_exist_file = False
    cyg_data_ver = 'v2.1'
    cygnss_l1_path = os.environ["CYGNSS_L1_PATH"]
    data_day = 24
    sc_num = 3
    cygnss_download.download_cyg_files(data_year, data_day, list_sc_num=sc_num, cyg_data_ver=cyg_data_ver, cyg_data_lvl='L1',
                                       cygnss_l1_path=cygnss_l1_path, check_md5_exist_file=check_md5_exist_file)
    st_date = dt.date(year=2019, month=1, day=12)
    end_date = dt.date(year=2020, month=1, day=3)

    cygnss_download.download_cyg_files_between_date(st_date, end_date, list_sc_num=sc_num, cyg_data_ver=cyg_data_ver, cyg_data_lvl='L1',
                                                    cygnss_l1_path=cygnss_l1_path, check_md5_exist_file=check_md5_exist_file)

    cygnsslib.data_downloader.download_cyg_rawif.download_cyg_rawif_files(data_year=2020, list_data_day=227)

    st_date = dt.date(year=2020, month=8, day=4)
    end_date = dt.date(year=2020, month=8, day=4)
    cygnsslib.data_downloader.download_cyg_rawif.download_rawif_cyg_files_between_date(st_date, end_date, download_l1_data=True)

