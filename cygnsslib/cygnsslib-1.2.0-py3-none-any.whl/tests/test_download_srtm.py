import numpy as np
import os
try:
    from cygnsslib import srtm_download
except ImportError:
    import sys
    parent_dir_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    sys.path.insert(0, parent_dir_path)
    from cygnsslib import srtm_download

if __name__ == '__main__':
    lat = np.array([21, 22, 20])
    lon = [29, 30]
    srtm_download.download_srtm_ght_files(lat, lon)
