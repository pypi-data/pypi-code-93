import click
import numpy as np
from ase.io import read
from clims.phonopy_interface import initialize_phonopy, post_process_phonopy


@click.command()
@click.option("--displacement", default=0.01, help="Displacement of atoms (AA).")
@click.option("--supercell", help="Supercell matrix (9 elements)", nargs=9)
@click.option("--filein", help="Input geometry file", default="geometry.in")
def clims_initialize_phonopy(displacement, supercell, filein):
    """
    Simple interface to phonopy to generate geometries with displaced atoms needed
    for the finite difference calculation of phonons DOS.
    """
    supercell_matrix = np.array([int(x) for x in supercell]).reshape((3, 3))
    structure = read(filein)
    initialize_phonopy(structure, supercell_matrix=supercell_matrix)


@click.command()
@click.option(
    "--mesh", default=[20, 20, 20], help="q-point mesh for phonopy", nargs=3, type=int
)
@click.option(
    "--outfile",
    default="aims.out",
    help="FHI-aims output file. All files should have the same name in the subfolders",
)
def clims_post_process_phonopy(mesh, outfile):
    """
    Simple interface to phonopy for post-processing the calculated forces to obtain
    the phonon DOS.
    """
    post_process_phonopy(mesh=mesh, outfile=outfile)
