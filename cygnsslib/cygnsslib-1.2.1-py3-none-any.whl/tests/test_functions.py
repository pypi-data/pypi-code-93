import os
from cygnsslib import create_centered_polygon, write_sp_within_radius

if __name__ == '__main__':
    # CYGNSS_L1_dir = os.path.join("G:\\", "cygnss_data", "L1", "v3")
    CYGNSS_L1_dir = None
    year = 2020
    daylist = list(range(1, 153))

    radius = 10e3
    thesh_ddm_snr = 3
    thesh_noise = 1
    out_root = "z1_2020_v3"
    # ref_pos = [37.1898, -105.9903] # Z4
    ref_pos = [37.1906, -105.9921]  # Z1
    write_sp_within_radius(CYGNSS_L1_dir, year, daylist, ref_pos, radius, out_root, thesh_ddm_snr, thesh_noise)
    create_centered_polygon(ref_pos, radius, "a", shape="circle")
