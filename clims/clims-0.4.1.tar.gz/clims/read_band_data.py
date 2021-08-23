import numpy as np


def read_bands(band_segments, band_totlength, max_spin_channel):
    band_data = {}

    prev_end = band_segments[0][0]
    distance = band_totlength / 30.0  # distance between line segments that do not coincide

    xpos = 0.0
    labels = [(0.0, band_segments[0][4])]

    for iband, (start, end, length, npoint, startname, endname) in enumerate(band_segments):
        band_data[iband + 1] = []
        if any(start != prev_end):
            xpos += distance
            labels += [(xpos, startname)]

        xvals = xpos + np.linspace(0, length, npoint)
        xpos = xvals[-1]

        labels += [(xpos, endname)]

        prev_end = end
        prev_endname = endname

        for spin in range(max_spin_channel):
            data = np.loadtxt("band%i%03i.out" % (spin + 1, iband + 1))
            idx = data[:, 0].astype(int)
            kvec = data[:, 1:4]
            band_occupations = data[:, 4::2]
            band_energies = data[:, 5::2]
            assert (npoint) == len(idx)
            band_data[iband + 1] += [
                {
                    "xvals": xvals,
                    "band_energies": band_energies,
                    "color": "kr"[spin],
                    "band_occupations": band_occupations,
                }
            ]
    shift = shift_band_data(band_data, max_spin_channel)

    return band_data, labels, shift


def shift_band_data(band_data, max_spin_channel):

    vbm = -1000000000
    for n, segment in band_data.items():
        for spin in range(max_spin_channel):
            occs = segment[spin]["band_occupations"]
            for k in range(len(occs)):
                occ_diff = occs[k][1:] - occs[k][:-1]
                fermi_inds = np.nonzero(occ_diff != 0)[0]
                # print(fermi_inds)
                if len(fermi_inds) == 1:
                    tmp_vbm = segment[spin]["band_energies"][k][fermi_inds]
                    if vbm < tmp_vbm:
                        vbm = tmp_vbm
                else:
                    print("Your system is probably a metal. Not shifting bands.")
                    return 0

    # Shift all bands
    for n in band_data.keys():
        for spin in range(max_spin_channel):
            band_data[n][spin]["band_energies"] -= vbm[0]

    return -vbm[0]
