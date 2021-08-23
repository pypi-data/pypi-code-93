import numpy as np
from clims.elements import colors
import re


def plot_mulliken_bands(
    ax_bands, segment_no, spin, species, atomic_numbers, is_SOC, structure, segments
):

    masks = {}
    markersizeunit = 12
    n_atoms = len(structure)
    factor_atoms = 1
    total_atom_ind = 4

    if is_SOC:
        factor_atoms = 2
        total_atom_ind = 5
    for s in species:
        if is_SOC:
            # There are double the number of states for SOC.
            masks[s] = [x == s for x in structure.get_chemical_symbols() for _ in (0, 1)]
        else:
            masks[s] = [x == s for x in structure.get_chemical_symbols()]

    with open("bandmlk%i%03i.out" % (spin + 1, segment_no + 1)) as f:
        output = f.read()
    print("Parsing bandmlk%i%03i.out" % (spin + 1, segment_no + 1))
    k_points = output.split("k point number:")[1:]
    # print("Number of k_points", len(k_points))
    len_k = len(k_points)

    # Find out actual number of states:
    start_state = int(re.search(r"\n *State *([0-9]*)\n", k_points[0]).group(1)) - 1
    states = re.split(r"\n *State *[0-9]*\n", k_points[0])[1:]
    n_states = len(states)

    mulliken_k = np.zeros((len(species), n_states * len_k))
    x_vals = np.zeros(n_states * len_k)
    y_vals = np.zeros(n_states * len_k)

    for i_k, k in enumerate(k_points):
        start_state = int(re.search(r"\n *State *([0-9]*)\n", k).group(1)) - 1
        states = re.split(r"\n *State *[0-9]*\n", k)[1:]
        end_state = start_state + n_states
        mulliken = np.zeros((n_states, factor_atoms * n_atoms))
        for i_state, state in enumerate(states):
            lines = state.splitlines()
            for i, line in enumerate(lines):
                mulliken[i_state, i] = float(line.split()[total_atom_ind])
        for i_s, (s, a) in enumerate(zip(species, atomic_numbers)):
            spec_mlk = mulliken[:, masks[s]].sum(axis=1)
            mulliken_k[i_s, i_k * n_states : (i_k + 1) * n_states] = spec_mlk
            x_vals[i_k * n_states : (i_k + 1) * n_states] = [segments["xvals"][i_k]] * n_states
            y_vals[i_k * n_states : (i_k + 1) * n_states] = segments["band_energies"][i_k][
                start_state:end_state
            ]

    scatters = ()
    for i_s, (s, a) in enumerate(zip(species, atomic_numbers)):
        sc = ax_bands.scatter(
            x_vals,
            y_vals,
            s=(markersizeunit * mulliken_k[i_s]) ** 2,
            c=colors[a - 1],
            alpha=0.3,
            edgecolors="none",
        )
        scatters += (sc,)

    return scatters
