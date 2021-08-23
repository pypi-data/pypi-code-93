import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys
import click
from ase.io import read
from clims.read_dos_data import read_species_dos, read_total_dos
from clims.read_band_data import read_bands
from clims.read_control import read_control
from clims.plot_mulliken import plot_mulliken_bands
from ase.symbols import symbols2numbers
from clims.elements import colors
from time import time


@click.command()
@click.option(
    "--emin",
    type=float,
    default=-20.1,
    help="Minimum energy value on the y axis of the plot(s).",
)
@click.option(
    "--emax",
    type=float,
    default=5.1,
    help="Maximum energy value on the y axis of the plot(s).",
)
@click.option(
    "--legend_offset",
    type=float,
    default=[1.01, 1.0],
    nargs=2,
    help="A x, y offset on the canvas that allows one to shift the legend horizontally.",
)
@click.option("--no_legend", is_flag=True, help="No legend will be printed into the plot.")
@click.option(
    "--show_l_components",
    is_flag=True,
    help="L components of the species_dos will be plotted if available.",
)
def aimsplot(emin, emax, legend_offset, no_legend, show_l_components):
    """
    Script to plot band structure and DOS calculated with FHI-aims.
    Requires the control.in/geometry.in files as well as the output
    of the calculation to be in the directory from which the script is called.

    This plot will be created in the same directory as a file aimsplot.png if all goes well.
    Specifically, the script allows to create a plot of

    - Energy band structures                  ("output band ...")

    - Density of states                       ("output dos ...")

    - Species-projected densities of states   ("output species_proj_dos ...")
    as well as, optionally, a decomposition of the DOS into angular momentum components

    - and, alternatively, the tetrahedron-integrated versions of DOS and species-projected DOS
    (much better resolution)

    This script can be called simply as "aimsplot.py", in which case a default range will be used for
    for the energy range covered on the y axis.

    There are several options that allow one to customize the energy range, type of output,
    legend placement etc.
    There are several options that allow one to customize the energy range, type of output,
    legend placement etc.

    aimsplot.py --help

    provides an overview of the available options.

    For example,

    aimsplot.py --Emin -20. --Emax 10. --legend_offset 1.0 0.2

    will customize both the y axis range shown, as well as the placement of the legend in
    the graph.

    To achieve labelling of the special points along the band structure plot,
    add two arguments to the "output band"
    command in the control.in, using the following syntax:

    output band <start> <end> <npoints> <starting_point_name> <ending_point_name>

    Example: To plot a band with 20 points from Gamma to half way along one of the
           reciprocal lattice vectors, write (in control.in)

    output band 0.0 0.0 0.0 0.5 0.0 0.0 20 Gamma <End_point_name>

    It is important to note that the graph can easily be further customized by editing
    this script, using the documentation available online for matplotlib.
    """

    ###########
    # OPTIONS #
    ###########
    # The DPI used for printing out images
    print_resolution = 250
    # Change the line width of plotted bands and k-vectors, 1 is default
    default_line_width = 1
    # Change the font size.  12 is the default.
    font_size = 12
    # Turn on spline interpolation for band structures NOT VERY WELL TESTED!
    should_spline = False
    # Whether to output the x-axis (e.g. the e=0 line) or not
    output_x_axis = True
    # If spline interpolation turned on, the sampling factor (1 is the original grid)
    spline_factor = 10
    # The maximum value of the DOS axis (a.k.a. x-axis) in the DOS
    # For zero or negative values, the script will use its default value, the maximum
    # value for the DOS in the energy window read in
    maxdos_output = -1

    e_shift = 0

    matplotlib.rcParams["lines.linewidth"] = default_line_width

    CUSTOM_YLIM = False
    if emin != -20.1 or emax != 5.1:
        CUSTOM_YLIM = True

    ########################

    print("Plotting bands for FHI-aims!")
    print("============================\n")
    print("Reading lattice vectors from geometry.in ...")

    structure = read("geometry.in")
    n_atoms = len(structure)
    latvec = structure.get_cell()
    print("Lattice vectors:")
    print(latvec[:], "\n")

    rlatvec = 2.0 * np.pi * latvec.reciprocal()
    print("Reciprocal lattice vectors:")
    print(rlatvec, "\n")

    ########################

    print("Reading information from control.in ...")

    PLOT_BANDS = False
    PLOT_BANDS_MULLIKEN = False
    PLOT_DOS = False
    PLOT_DOS_SPECIES = False
    PLOT_DOS_ATOM = False
    PLOT_SOC = False  # This is needed because there will only be one "spin" channel output,
    # but collinear spin may (or may not) be turned on, so the "spin
    # collinear" setting needs to be overridden
    PLOT_DOS_REVERSED = False

    max_spin_channel = 1
    band_segments = []
    band_totlength = 0.0  # total length of all band segments

    try:
        control = read_control()
        species = list(control["species"].keys())
        atomic_numbers = [symbols2numbers(s)[0] for s in species]
        output = control["output"]
    except:
        print("Something went wrong while parsing control.in")
        print("The following may missing: control.in or output flags")
        raise

    if "spin" in control and control["spin"] == "collinear":
        max_spin_channel = 2

    if (
        "calculate_perturbative_soc" in control
        or "include_spin_orbit" in control
        or "include_spin_orbit_sc" in control
    ):
        PLOT_SOC = True
        max_spin_channel = 1

    if "band_mulliken_orbit_num" in control:
        n_states_band_mulliken = int(control["band_mulliken_orbit_num"])
        if PLOT_SOC:
            n_states_band_mulliken = 2 * int(control["band_mulliken_orbit_num"])
    else:
        n_states_band_mulliken = 100
        if PLOT_SOC:
            n_states_band_mulliken = 200

    if "bands" in output:
        PLOT_BANDS = True
        if "is_band_mulliken" in output:
            PLOT_BANDS_MULLIKEN = True

        for band in output["bands"]:
            start = np.asarray(band[:3], dtype=float)
            end = np.asarray(band[3:6], dtype=float)
            length = np.linalg.norm(np.dot(rlatvec, end) - np.dot(rlatvec, start))
            band_totlength += length
            npoint = int(band[6])
            startname, endname = "", ""
            if len(band) > 7:
                startname = band[7]
            if len(band) > 8:
                endname = band[8]
            band_segments += [(start, end, length, npoint, startname, endname)]

    if "dos" in output or "dos_tetrahedron" in output:
        PLOT_DOS = True

    if "species_proj_dos" in output or "species_proj_dos_tetrahedron" in output:
        PLOT_DOS_SPECIES = True

    if "atom_proj_dos" in output or "atom_proj_dos_tetrahedron" in output:
        PLOT_DOS_ATOM = True

    if PLOT_BANDS and (PLOT_DOS or PLOT_DOS_SPECIES):
        ax_bands = plt.axes([0.1, 0.1, 0.6, 0.8])
        ax_dos = plt.axes([0.72, 0.1, 0.18, 0.8], sharey=ax_bands)
        ax_dos.set_title("DOS")
        plt.setp(ax_dos.get_yticklabels(), visible=False)
        ax_bands.set_ylabel("E [eV]")
        PLOT_DOS_REVERSED = True
    elif PLOT_BANDS:
        ax_bands = plt.subplot(1, 1, 1)
        ax_bands.set_ylabel("E [eV]")
    elif PLOT_DOS or PLOT_DOS_SPECIES:
        ax_dos = plt.subplot(1, 1, 1)
        ax_dos.set_title("DOS")

    #######################

    if PLOT_BANDS:
        print("Plotting %i band segments..." % len(band_segments))

        if output_x_axis:
            ax_bands.axhline(0, color=(1.0, 0.0, 0.0), linestyle=":")

        band_data, labels, e_shift = read_bands(
            band_segments, band_totlength, max_spin_channel
        )
        # start = time()
        for iband, segment in enumerate(band_data.values()):
            for spin in range(max_spin_channel):
                sb = segment[spin]
                ax_bands.plot(sb["xvals"], sb["band_energies"], color=sb["color"])
                if PLOT_BANDS_MULLIKEN:
                    scatters = plot_mulliken_bands(
                        ax_bands, iband, spin, species, atomic_numbers, PLOT_SOC, structure, sb
                    )
        # end = time()
        # print("Timing", end - start)

        if PLOT_BANDS_MULLIKEN:
            lg = ax_bands.legend(
                scatters, species, scatterpoints=1, fontsize=12, loc="lower right"
            )
            for lh in lg.legendHandles:
                lh.set_alpha(1)
                lh.set_sizes([100])

        tickx, tickl = [], []
        for xpos, l in labels:
            ax_bands.axvline(xpos, color="k", linestyle=":")
            tickx += [xpos]
            if l == "Gamma" or l == "G":
                l = "$\\Gamma$"
            tickl += [l]
            print("| %8.3f %s" % (xpos, repr(l)))

        ax_bands.set_xlim(labels[0][0], labels[-1][0])
        ax_bands.set_xticks(tickx)
        ax_bands.set_xticklabels(tickl)
        ax_bands.set_ylim(emin, emax)

    #######################
    maxdos = 0.0
    energy_lim = [100000, -100000]

    if PLOT_DOS_SPECIES:
        dos_species = read_species_dos(species, max_spin_channel)
        maxdos = dos_species["maxdos"]
        energy_lim = dos_species["energy_lim"]

    if PLOT_DOS:
        energy, dos, maxdos, energy_lim = read_total_dos()

    spinsgns = [1.0]
    spinlabels = [""]
    if max_spin_channel == 2:
        spinsgns = [1.0, -1.0]
        spinlabels = ["up", "down"]

    if PLOT_DOS_REVERSED:
        ax_dos.axhline(0, color=(1.0, 0.0, 0.0), linestyle=":")
        ax_dos.axvline(0, color=(0.5, 0.5, 0.5))

        if PLOT_DOS:
            for ispin in range(max_spin_channel):
                ax_dos.plot(dos[:, ispin] * spinsgns[ispin], energy + e_shift, color="k")

        if PLOT_DOS_SPECIES:
            for s, a in zip(species, atomic_numbers):
                for ispin, (spinsgn, spinlabel) in enumerate(zip(spinsgns, spinlabels)):
                    s_energy = dos_species[s][ispin][:, 0]
                    species_dos = dos_species[s][ispin][:, 1]
                    ax_dos.plot(
                        species_dos * spinsgn,
                        s_energy + e_shift,
                        linestyle="-",
                        label=f"{s} {spinlabel}",
                        color=colors[a - 1],
                    )
                    if show_l_components:
                        l_dos = dos_species[s][ispin][:, 2:]
                        for l in range(l_dos.shape[1]):
                            label = f"{s} (l={l}) {spinlabel}"
                            ax_dos.plot(
                                l_dos[:, l] * spinsgn,
                                s_energy + e_shift,
                                linestyle="--",
                                label=label,
                            )

        if maxdos_output > 0:
            # If the user has specified a maximum DOS value, use it
            ax_dos.set_xlim(np.array([min(spinsgns[-1], 0.0) - 0.05, 1.00]) * maxdos_output)
        else:
            # Otherwise use the maximum DOS value read in
            ax_dos.set_xlim(np.array([min(spinsgns[-1], 0.0) - 0.05, 1.05]) * maxdos)
        if CUSTOM_YLIM:
            ax_dos.set_ylim(emin, emax)
        else:
            ax_dos.set_ylim(energy_lim[0], energy_lim[1])

    else:  # not PLOT_DOS_REVERSED
        if PLOT_DOS or PLOT_DOS_SPECIES:
            ax_dos.axvline(0, color="k", ls="--")
            ax_dos.axhline(0, color=(0.5, 0.5, 0.5))
            ax_dos.set_xlabel(r"$\varepsilon - \mu$ (eV)")

        if PLOT_DOS_SPECIES:
            for s in species:
                for ispin, (spinsgn, spinlabel) in enumerate(zip(spinsgns, spinlabels)):
                    s_energy = dos_species[s][ispin][:, 0]
                    species_dos = dos_species[s][ispin][:, 1]
                    l_dos = dos_species[s][ispin][:, 2:]
                    ax_dos.plot(
                        s_energy + e_shift,
                        species_dos * spinsgn,
                        linestyle="-",
                        label=f"{s} {spinlabel}",
                    )
                    for l in range(l_dos.shape[1]):
                        label = f"{s} (l={l}) {spinlabel}"
                        ax_dos.plot(
                            s_energy + e_shift,
                            l_dos[:, l] * spinsgn,
                            linestyle="--",
                            label=label,
                        )

        if PLOT_DOS:
            for ispin in range(max_spin_channel):
                ax_dos.plot(
                    energy + e_shift, dos[:, ispin] * spinsgns[ispin], label="Total DOS"
                )

            ax_dos.set_xlim(energy[0], energy[-1])
            if CUSTOM_YLIM:
                ax_dos.set_ylim(emin, emax)
            else:
                if maxdos_output > 0:
                    # If the user has specified a maximum DOS value, use that instead
                    ax_dos.set_ylim(
                        np.array([min(spinsgn[-1], 0.0) - 0.05, 1.00]) * maxdos_output
                    )
                else:
                    # Otherwise use the maximum DOS value read in
                    ax_dos.set_ylim(np.array([min(spinsgns[-1], 0.0) - 0.05, 1.05]) * maxdos)

    if PLOT_DOS_SPECIES:
        if not no_legend:
            ax_dos.legend(bbox_to_anchor=legend_offset, loc="upper left")

    #######################

    matplotlib.rcParams["savefig.dpi"] = print_resolution
    matplotlib.rcParams["font.size"] = font_size

    print()
    print(
        f"The resolution for saving figures is set to {matplotlib.rcParams['savefig.dpi']} dpi."
    )

    def on_q_exit(event):
        if event.key == "q":
            sys.exit(0)

    plt.connect("key_press_event", on_q_exit)
    plt.savefig("aimsplot.png")
    plt.show()
