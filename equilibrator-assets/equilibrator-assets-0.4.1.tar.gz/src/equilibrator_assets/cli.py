# The MIT License (MIT)
#
# Copyright (c) 2018 Institute for Molecular Systems Biology, ETH Zurich.
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""Define the command line interface (CLI) for generating assets."""


import logging
import os
from os.path import join
from tempfile import mkdtemp

import click
import click_log
from equilibrator_cache import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import compounds, metanetx, registry, thermodynamics


logger = logging.getLogger()
click_log.basic_config(logger)
Session = sessionmaker()


try:
    NUM_PROCESSES = len(os.sched_getaffinity(0))
except (AttributeError, OSError):
    logger.warning(
        "Could not determine the number of cores available - assuming 1."
    )
    NUM_PROCESSES = 1
ERROR_LOG = join(mkdtemp(prefix="equilibrator_assets_"), "error")
DEFAULT_DATABASE_URL = "sqlite:///compounds.sqlite"
DEFAULT_BIGG_METABOLITE_URL = (
    "http://bigg.ucsd.edu/static/namespace/bigg_models_metabolites.txt"
)


@click.group()
@click.help_option("--help", "-h")
@click_log.simple_verbosity_option(
    logger,
    default="INFO",
    show_default=True,
    type=click.Choice(["CRITICAL", "ERROR", "WARN", "INFO", "DEBUG"]),
)
def cli():
    """Command line interface to populate and update the equilibrator cache."""
    pass


@cli.command()
@click.help_option("--help", "-h")
@click.option(
    "--db-url",
    metavar="URL",
    default=DEFAULT_DATABASE_URL,
    show_default=True,
    help="A string interpreted as an rfc1738 compatible database URL.",
)
@click.option(
    "--update/--no-update",
    default=True,
    show_default=True,
    help="Check the MetaNetX FTP server for updated tables.",
)
@click.option(
    "--batch-size",
    type=int,
    default=1000,
    show_default=True,
    help="The size of batches of compounds to transform at a time.",
)
@click.argument(
    "working_dir",
    metavar="<METANETX PATH>",
    type=click.Path(exists=True, file_okay=False, writable=True),
)
@click.argument(
    "additional-compounds",
    metavar="<ADDITIONAL COMPOUNDS>",
    type=click.Path(exists=True, dir_okay=False),
)
def init(
    working_dir: click.Path,
    additional_compounds: click.Path,
    db_url: str,
    update: bool,
    batch_size: int,
):
    """Drop any existing tables and populate the database using MetaNetX."""
    engine = create_engine(db_url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)
    if update:
        logger.info("Updating MetaNetX content.")
        metanetx.update_tables(str(working_dir))
    logger.info("Parsing compound cross-references.")
    chem_xref = metanetx.load_compound_cross_references(str(working_dir))
    logger.info("Populating registries.")
    registry.populate_registries(session, chem_xref)
    logger.info("Loading compound properties.")
    chem_prop = metanetx.load_compound_properties(str(working_dir))
    logger.info("Populating compounds.")
    compounds.populate_compounds(session, chem_prop, chem_xref, batch_size)
    logger.info("Populating additional compounds.")
    compounds.populate_additional_compounds(session, additional_compounds)
    logger.info("Filling in missing InChIs from KEGG.")
    compounds.fetch_kegg_missing_inchis(session)


@cli.command()
@click.help_option("--help", "-h")
@click.option(
    "--db-url",
    metavar="URL",
    default=DEFAULT_DATABASE_URL,
    show_default=True,
    help="A string interpreted as an rfc1738 compatible database URL.",
)
@click.option(
    "--kegg/--no-kegg",
    default=True,
    show_default=True,
    help="By default, calculate thermodynamic information for compounds "
    "contained in KEGG only.",
)
@click.option(
    "--batch-size",
    type=int,
    default=1000,
    show_default=True,
    help="The size of batches of compounds to transform at a time.",
)
@click.option(
    "--error-log",
    type=click.Path(dir_okay=False, writable=True),
    default=ERROR_LOG,
    show_default=True,
    help="The base file path for error output.",
)
def structures(db_url: str, kegg: bool, batch_size: int, error_log: click.Path):
    """
    Calculate atom bags and molecular masses for compounds missing those.

    Use openbabel to calculate the atom bags and molecular masses of all
    the compounds that are missing these values.

    """
    engine = create_engine(db_url)
    session = Session(bind=engine)

    logger.info("Filling in missing masses and atom bags.")
    compounds.fill_missing_values(
        session, only_kegg=kegg, batch_size=batch_size, error_log=str(error_log)
    )


@cli.command()
@click.help_option("--help", "-h")
@click.option(
    "--db-url",
    metavar="URL",
    default=DEFAULT_DATABASE_URL,
    show_default=True,
    help="A string interpreted as an rfc1738 compatible database URL.",
)
@click.option(
    "--batch-size",
    type=int,
    default=100,
    show_default=True,
    help="The size of batches of compounds considered at a time.",
)
@click.option(
    "--error-log",
    type=click.Path(dir_okay=False, writable=True),
    default=ERROR_LOG,
    show_default=True,
    help="The base file path for error output.",
)
@click.option(
    "--error-log",
    type=click.Path(dir_okay=False, writable=True),
    default=ERROR_LOG,
    show_default=True,
    help="The base file path for error output.",
)
def dissociation_constants(
    db_url: str, batch_size: int, error_log: click.Path
) -> None:
    """Calculate and store thermodynamic information for compounds."""
    engine = create_engine(db_url)
    session = Session(bind=engine)

    # populate the "exception" compounds (i.e. ones where ChemAxon fails)
    thermodynamics.populate_compound_exception(session)

    # populate all other compounds using ChemAxon
    thermodynamics.populate_dissociation_constants(
        session, batch_size=batch_size, error_log=str(error_log)
    )

    thermodynamics.populate_magnesium_dissociation_constants(session)


@cli.command()
@click.help_option("--help", "-h")
@click.option(
    "--db-url",
    metavar="URL",
    default=DEFAULT_DATABASE_URL,
    show_default=True,
    help="A string interpreted as an rfc1738 compatible database URL.",
)
def microspecies(
    db_url: str,
) -> None:
    """Calculate and store thermodynamic information for compounds."""
    engine = create_engine(db_url)
    session = Session(bind=engine)
    thermodynamics.populate_microspecies(session)


if __name__ == "__main__":
    cli()
