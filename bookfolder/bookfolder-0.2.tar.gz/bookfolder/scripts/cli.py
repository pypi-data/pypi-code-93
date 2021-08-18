"""
Command line interface for the bookfolder app.
"""

import click

from bookfolder.formatter import CSVFormatter
from bookfolder.pattern_creator import PatternCreator


@click.group()
@click.argument("image", type=click.Path(exists=True))
@click.option("--measurement-interval",
              help="Height of one pixel in the IMAGE in millimeters",
              default=0.25,
              type=click.FLOAT)
@click.option("--start-page",
              help="The page number of the first sheet in the pattern",
              default=1,
              type=click.INT)
@click.pass_context
def cli(ctx, image, measurement_interval, start_page):
    """
    Generate a bookfolding pattern from IMAGE

    Each color of pixels in the image must correspond to one fold depth in the
    scuplture, with each horizontal pixel corresponding to one sheet of paper
    in the book and each vertical pixel to one MEASUREMENT_INTERVAL along the
    edge of the book.
    """
    ctx.ensure_object(dict)

    pattern_creator = PatternCreator(image, measurement_interval, start_page)
    sheets = pattern_creator.sheets()
    ctx.obj["sheets"] = sheets
    ctx.obj["pattern_creator"] = pattern_creator


@cli.command()
@click.pass_context
def csv_pattern(ctx):
    """
    Show the pattern in csv format
    """
    sheets = ctx.obj["sheets"]
    formatter = CSVFormatter(sheets)
    click.echo(formatter.format())


@cli.command()
@click.pass_context
@click.argument("output_file", type=click.Path())
def pdf_pattern(ctx, output_file):
    """
    Save the pattern as a PDF file
    """
    pattern_creator = ctx.obj["pattern_creator"]
    pattern_creator.save_pdf(output_file)
    click.echo("Wrote the pattern to {}".format(output_file))


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    # pylint: disable=unexpected-keyword-arg
    cli(obj={})
