from typing import Dict, Optional, List

import click
import click_config_file

from montecarlodata import settings
from montecarlodata.common.resources import CloudResourceService


# Shared command verbiage
PROFILE_VERBIAGE = 'If not specified, the one in the Monte Carlo CLI profile is used'


@click.group(help='Display information about resources.')
def discovery():
    """
    Group for any discovery related subcommands
    """
    pass


@discovery.command(help='List details about EMR clusters in a region.')
@click.option('--aws-profile', help=f'AWS profile. {PROFILE_VERBIAGE}', required=False)
@click.option('--aws-region', help=f'AWS region. {PROFILE_VERBIAGE}', required=False)
@click.option('--only-log-locations', help='Display only unique log locations', is_flag=True, default=False)
@click.option('--created-after', help='Display clusters created after date (e.g. 2017-07-04T00:01:30)', required=False)
@click.option('--state', help='Cluster states', required=False, type=click.Choice(['active', 'terminated', 'failed']),
              multiple=True)
@click.option('--no-grid',
              help='Do not display as grid and print as results are available, useful when the cluster list is large',
              is_flag=True, default=False)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
@click.pass_obj
def list_emr_clusters(ctx: Dict, aws_profile: Optional[str] = None, aws_region: Optional[str] = None,
                      only_log_locations: Optional[bool] = False, created_after: Optional[str] = None,
                      state: Optional[List] = None, no_grid: Optional[bool] = False) -> None:
    CloudResourceService(config=ctx['config'], aws_profile_override=aws_profile, aws_region_override=aws_region) \
        .list_emr_clusters(only_log_locations=only_log_locations, created_after=created_after, states=state,
                           no_grid=no_grid)
