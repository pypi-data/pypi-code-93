from ase.io import read, write
from ase.calculators.aims import Aims
import re
import numpy as np
from pathlib import Path


CWD = Path(".")


def write_control(species_dir, relax, bands, hse06, dos):
    """
    Checks and writes control.in template.
    """
    if hse06:
        xc = {"xc": "hse06 0.11", "hse_unit": "bohr", "hybrid_xc_coeff": 0.25}
        if bands:
            xc["exx_band_structure_version"] = "1"
    else:
        xc = {"xc": "pbe"}

    calc = Aims(
        **xc,
        relativistic="atomic_zora scalar",
        species_dir=species_dir,
    )

    try:
        c = read(CWD / "geometry.in", format="aims")
        print("-- Found geometry.in file")
    except:
        print("**ERROR**: No control.in file generated: No geometry.in found!")
        raise

    is_periodic = all(c.pbc)
    needs_spin = np.any(c.get_initial_magnetic_moments())
    try:
        needs_xc, needs_ks, needs_species_default = check_control(is_periodic)
        # print(needs_xc, needs_ks, needs_species_default)
        if needs_species_default:
            print("-- Found control.in, but no species: Only attaching species")
            calc.write_species(c)
        else:
            print("-- Not attaching species_default (found some)")
    except:
        output = []
        print("-- Creating new control.in file.")
        path = CWD
        if is_periodic:
            r_lattice = np.linalg.norm(2.0 * np.pi * c.cell.reciprocal(), axis=1)
            # print(r_lattice)
            k_grid = tuple(np.ceil(r_lattice * 6).astype(int))
            calc.set(k_grid=k_grid)
        if relax:
            calc.set(relax_geometry="trm 5e-3")
            if is_periodic:
                calc.set(relax_unit_cell="full")
        if dos:
            output += [
                "dos_tetrahedron -20 10 15001",
                "species_proj_dos_tetrahedron -20 10 15001",
            ]
        if bands and is_periodic:
            print(f"-- Bravais Lattice: {c.cell.get_bravais_lattice().longname}")
            print(f"  {c.cell.get_bravais_lattice().description()}")
            bands = prepare_bandinput(c.get_cell())
            output += bands
        if output:
            calc.set(output=output)
        if needs_spin:
            calc.set(spin="collinear")
        c_file = path / "control.in"
        calc.write_control(c, c_file.as_posix())
        calc.write_species(c, c_file.as_posix())


def prepare_bandinput(cell, density=30):
    """
    Prepares the band information needed for the FHI-aims control.in file.

    Parameters:

    max_points_per_path: int
        Number of kpoints per band path
    density: int
        Number of kpoints per Angstrom. Default: 35
    """
    from ase.dft.kpoints import resolve_kpt_path_string, kpoint_convert

    bp = cell.bandpath()
    # print(cell.get_bravais_lattice())
    r_kpts = resolve_kpt_path_string(bp.path, bp.special_points)

    linesAndLabels = []
    for labels, coords in zip(*r_kpts):
        dists = coords[1:] - coords[:-1]
        lengths = [np.linalg.norm(d) for d in kpoint_convert(cell, skpts_kc=dists)]
        points = np.int_(np.round(np.asarray(lengths) * density))
        # I store it here for now. Might be needed to get global info.
        linesAndLabels.append([points, labels[:-1], labels[1:], coords[:-1], coords[1:]])

    bands = []
    for segs in linesAndLabels:
        for points, lstart, lend, start, end in zip(*segs):
            bands.append(
                "band {:9.5f}{:9.5f}{:9.5f} {:9.5f}{:9.5f}{:9.5f} {:4} {:3}{:3}".format(
                    *start, *end, points, lstart, lend
                )
            )

    # print(bands)
    return bands


def get_and_make_path(path_string):
    re_relax = re.compile(r"^relaxation-[0-9]{2}$")
    path = Path(path_string)
    if path.exists():
        my_number = 0
        dirlist = [x for x in CWD.iterdir() if x.exists() and re_relax.match(x.as_posix())]
        for d in dirlist:
            try:
                tmp = d.as_posix().split("-")
                current_number = int(tmp[1])
                if current_number > my_number:
                    my_number = current_number
            except:
                pass
        path_string += f"-{my_number+1:02d}"
        path = Path(path_string)

    path.mkdir()
    return path


def check_control(is_periodic):
    try:
        has_xc = False
        xc = re.compile(r"^\s*xc\s+")
        has_ks = False
        ks = re.compile(r"^\s*k_grid\s+")
        has_species_default = False
        control_file = open("control.in", "r")
        print("Found control.in file")
        for line in control_file:
            if xc.match(line):
                has_xc = True
            elif ks.match(line):
                has_ks = True
            elif "#  FHI-aims code project" in line:
                has_species_default = True
        needs_xc = not has_xc
        needs_ks = not has_ks and is_periodic
        needs_species_default = not has_species_default
        return needs_xc, needs_ks, needs_species_default

    except IOError:
        raise


# def dry_run():
#    try:
#        os.mkdir("dry_run")
#    except:
#        pass
#    copyfile("control.in", "dry_run/control.in")
#    copyfile("geometry.in", "dry_run/geometry.in")
#    os.chdir("dry_run")
#    src = open("control.in", "r")
#    fline = "dry_run\n"
#    oline = src.readlines()
#    oline.insert(0, fline)
#    src.close()
#    src = open("control.in", "w")
#    src.writelines(oline)
#    src.close()
#    os.system("{} > parse.out 2>error.out".format(AIMS_SERIAL))
#    if os.stat("error.out").st_size == 0:
#        print("Ready for calculation")
#    else:
#        os.system("cat parse.out")
#    os.chdir("../.")
#    rmtree("dry_run")
