import numpy as np
import os
try:
    import cygnsslib
except ImportError:
    import sys
    parent_dir_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    sys.path.insert(0, parent_dir_path)
    import cygnsslib


if __name__ == '__main__':
    CYGNSS_L1_dir = os.environ["CYGNSS_L1_PATH"]
    year = 2018

    daylist = list(range(1, 365))

    radius = 5e3
    thesh_ddm_snr = 10.
    thesh_noise = 1
    max_grp_dist = 100
    point_names = ["Y1", "Y2", "Y3", "Y4", "Y5", "Y6", "Y7", "Y8", "Y9", "Y10", "Y11", "Y12", "Y13"]
    loc_list = np.array([[-34.62888, 145.84895], [-34.65478, 146.11028], [-34.621, 146.424], [-34.71943, 146.02003], [-34.72835, 146.29317], [-34.84262, 145.86692],
                         [-34.85183, 146.1153], [-34.84697, 146.41398], [-34.96777, 146.01632], [-35.00535, 146.30988], [-35.10975, 145.93553], [-35.0696, 146.16893],
                         [-35.09025, 146.30648]])
    for i_loc, loc in enumerate(loc_list):
        out_root = 'yanco_{:d}_{:s}'.format(year, point_names[i_loc])
        ref_pos = loc
        out_options = dict()
        out_options["plt_tag"] = point_names[i_loc]
        out_options["save_cvs"] = True
        out_high, out_low, out_ref = cygnsslib.write_sp_within_radius(CYGNSS_L1_dir, year, daylist, ref_pos, radius, out_root, thesh_ddm_snr,
                                                                      thesh_noise, out_options=out_options)
        out_kml = 'grp{:d}_{:s}'.format(max_grp_dist, out_high)
        cygnsslib.group_sp_within_distance(out_high, out_kml=out_kml, max_dist=max_grp_dist, save_csv=True)
