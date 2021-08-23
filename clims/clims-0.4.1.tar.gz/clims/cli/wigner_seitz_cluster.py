from clims.construct_wigner_seitz_cluster import create_ws_cell
from ase.build.supercells import make_supercell
from ase.io import read, write
import click
import numpy as np


@click.command()
@click.argument("super_matrix", nargs=-1)
@click.option(
    "--filein",
    type=click.Path(exists=True),
    default="geometry.in",
    show_default=True,
    help="File name of input structure",
)
@click.option(
    "--format", type=str, default="aims", help="Format of the in- and output file"
)
@click.option(
    "--fileout",
    default="geometry-ws-cluster.in",
    show_default=True,
    help="File name for cluster structure",
)
@click.option(
    "--translate-basis",
    type=float,
    default=[0.0, 0.0, 0.0],
    nargs=3,
    help="Translates the basis atoms by a vector (in AA). ",
)
def construct(super_matrix, translate_basis, filein, fileout, format):
    """
    Constructs a Cluster of the shape of the Wigner-Seitz Cell based on the supercell
    (of size (det(SUPER_MATRIX))) of a periodic input structure.
    """
    prim = read(filein, format=format)
    prim.positions += np.array(translate_basis)
    if not all(prim.get_pbc()):
        click.echo("\nLoaded structure is not periodic.")
        return

    click.echo(f"\n{'Read structure from:':35}: {filein}")
    click.echo(f"{'Chemical formula':35}: {prim.get_chemical_formula()}")
    if len(super_matrix) == 3:
        P = np.diag([int(i) for i in super_matrix])
    elif len(super_matrix) == 9:
        P = np.array([int(i) for i in super_matrix], dtype=np.double).reshape(3, 3)
    else:
        click.echo("\n***ERROR***: The size of SUPER_MATRIX should be either 3 or 9.")
        return
    supercell = make_supercell(prim, P, wrap=False)
    create_ws_cell(supercell)
    supercell.pbc = False
    write(fileout, supercell, format=format)
