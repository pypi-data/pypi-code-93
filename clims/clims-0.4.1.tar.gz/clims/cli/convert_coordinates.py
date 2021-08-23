import click
from ase.io import read, write

@click.command()
@click.option(
    "--filein",
    type=click.Path(exists=True),
    default="geometry.in",
    show_default=True,
    help="File of input structure",
)
@click.option(
    "--fileout",
    default="geometry.out",
    show_default=True,
    help="File name for supercell structure",
)
def real2frac(filein, fileout):
    """Convert cartesian to fractional coordinates"""
    structure = read(filein)
    write(fileout,structure,format='aims',scaled=True)

@click.command()
@click.option(
    "--filein",
    type=click.Path(exists=True),
    default="geometry.in",
    show_default=True,
    help="File of input structure",
)
@click.option(
    "--fileout",
    default="geometry.out",
    show_default=True,
    help="File name for supercell structure",
)
def frac2real(filein, fileout):
    """Convert fractional to cartesian coordinates"""
    structure = read(filein)
    write(fileout,structure,format='aims',scaled=False)
