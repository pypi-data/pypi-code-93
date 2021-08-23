import click
from clims.structure import Structure
from ase.io.formats import read, ioformats


@click.command()
@click.option(
    "--filein",
    default="geometry.in",
    type=click.Path(exists=True),
    show_default=True,
    help="Name of the input file",
)
@click.option(
    "--format",
    default=None,
    show_default=True,
    help="In- and output format of structure files",
)
@click.option(
    "--symthresh", default=1e-5, help="Threshold for crystal symmetry detection"
)
@click.option("--primitive", is_flag=True, help="Write primitive to file.")
@click.option("--conventional", is_flag=True, help="Write conventional to file.")
def unit_cell_info(filein, format, symthresh, primitive, conventional):
    """
    Show some information for structure and write out the standardized primitive and
    conventional cell.
    """
    try:
        c = read(filein, format=format)
    except StopIteration:
        click.echo(f'ERROR: Could not identify format of input file "{filein}"')
        click.echo('Please specify the format of input file by "--format".')
        click.echo("Available formats are:")
        print(list(ioformats.keys()))
        return
    si = Structure(c, symthresh)
    if (conventional or primitive) and not all(c.pbc):
        click.echo(
            f'ERROR: "{filein}" is not a periodic structure. Cannot write conventional or primitive cell.'
        )
        return
    if conventional:
        click.echo("Writing conventional unit cell (refined)")
        si.write_refined()
    if primitive:
        click.echo("Writing primtive unit cell (refined)")
        si.write_primitive()
    click.echo(si)
