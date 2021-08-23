import click
import numpy as np
from ase.io import read, write
from ase.build.supercells import make_supercell
from ase.build import find_optimal_cell_shape


@click.command()
@click.argument("super_matrix", nargs=-1)
@click.option(
    "--filein",
    type=click.Path(exists=True),
    default="geometry.in",
    show_default=True,
    help="File of input structure",
)
@click.option("--format", type=str, default=None)
@click.option(
    "--scaled",
    type=bool,
    default=True,
    help="If output in sclaed coodinates",
    show_default=True,
)
@click.option(
    "--fileout",
    default="geometry-supercell.in",
    show_default=True,
    help="File name for supercell structure",
)
@click.option(
    "--to-cubic-with-natoms", type=int, help="Convert cell to most cubic with N_ATOMS."
)
def supercell(super_matrix, filein, fileout, format, scaled, to_cubic_with_natoms):
    """Create supercell from SUPER_MATRIX (3 or 9 elements)"""
    try:
        prim = read(filein, format=format)
    except StopIteration:
        click.echo(f'\n***ERROR***: Could not identify format of input file "{filein}"')
        click.echo('-- Please specify the format of input file by "--format".')
        click.echo(
            "-- For available formats c.f.: https://wiki.fysik.dtu.dk/ase/ase/io/io.html"
        )
        return

    if not all(prim.get_pbc()):
        click.echo("\nLoaded structure is not periodic.")
        return

    click.echo(f"\n{'Read structure from:':35}: {filein}")
    click.echo(f"{'Chemical formula':35}: {prim.get_chemical_formula()}")

    if to_cubic_with_natoms:
        click.echo(
            f"\nTry to find most cubic supercell with {to_cubic_with_natoms} atoms."
        )
        click.echo("(This may take some time ...)")
        to_cubic_with_natoms /= len(prim)  # ASE looks for number of unit cells.
        P = find_optimal_cell_shape(prim.cell, to_cubic_with_natoms, "sc", verbose=True)
    elif len(super_matrix) == 3:
        P = np.diag([int(i) for i in super_matrix])
    elif len(super_matrix) == 9:
        P = np.array([int(i) for i in super_matrix], dtype=np.double).reshape(3, 3)
    else:
        click.echo("The size of SUPER_MATRIX should be either 3 or 9.")
        return

    superatom = make_supercell(prim, P)
    click.echo(f"{'Number of atoms in original cell':35}: {len(prim)}")
    click.echo(f"{'Number of atoms in supercell':35}: {len(superatom)}")
    write(fileout, superatom, format=format, scaled=scaled)
    click.echo(f"{'Supercell written to file':35}: {fileout}\n")
