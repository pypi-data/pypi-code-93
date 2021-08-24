###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
#
# The command line tools use the click and click-log packages for easier development
#
import logging
import os

import click
import click_log

from .analysis_data import AnalysisData
from .ap_info import cache_ap_info

logger = logging.getLogger("apd")
click_log.basic_config(logger)


@click.command()
@click.argument("cache_directory")
@click.argument("working_group")
@click.argument("analysis")
@click_log.simple_verbosity_option(logger)
def cmd_cache_ap_info(cache_directory, working_group, analysis):
    logger.debug(
        "Caching information for %s/%s to %s", working_group, analysis, cache_directory
    )
    cache_ap_info(cache_directory, working_group, analysis)


@click.command()
@click.argument("working_group")
@click.argument("analysis")
@click.option(
    "--cache_directory",
    default=os.environ.get("APD_CACHE", None),
    help="Specify location of the cached analysis data files",
)
@click.option("--tag", default=None, help="Tag to filter datasets", multiple=True)
@click.option(
    "--value",
    default=None,
    help="Tag value used if the name is specified",
    multiple=True,
)
@click.option(
    "--eventtype", default=None, help="eventtype to filter the datasets", multiple=True
)
@click.option("--year", default=None, help="year to filter the datasets", multiple=True)
@click.option("--polarity", default=None, help="polarity to filter the datasets")
@click_log.simple_verbosity_option(logger)
def cmd_list_pfns(
    working_group, analysis, cache_directory, tag, value, eventtype, year, polarity
):

    # Dealing with the cache
    if not cache_directory:
        cache_directory = "/tmp/apd_cache"
        logger.debug("Cache directory not set, using %s", cache_directory)
    if not os.path.exists(cache_directory):
        logger.debug(
            "Caching information for %s/%s to %s",
            working_group,
            analysis,
            cache_directory,
        )
        cache_ap_info(cache_directory, working_group, analysis)

    # Loading the data and filtering/displaying
    datasets = AnalysisData(working_group, analysis, metadata_cache=cache_directory)
    for f in datasets(
        tag=tag, value=value, eventtype=eventtype, year=year, polarity=polarity
    ):
        click.echo(f)
