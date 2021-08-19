import click
import click_config_file

import montecarlodata.settings as settings
from montecarlodata.collector.fields import DEFAULT_COLLECTION_REGION
from montecarlodata.collector.management import CollectorManagementService
from montecarlodata.tools import validate_json_callback, add_common_options

# Shared command verbiage
PROFILE_VERBIAGE = 'If not specified, the one in the Monte Carlo CLI profile is used'

# Options shared across commands
REGION_OPTIONS = [
    click.option('--aws-region', required=False, default=DEFAULT_COLLECTION_REGION, show_default=True,
                 help='AWS region where the collector is deployed or intended to be deployed.')
]
DEPLOYMENT_OPTIONS = [
    click.option('--aws-profile', required=False, help=f'AWS profile. {PROFILE_VERBIAGE}.'),
    click.option('--params', required=False, default=None, callback=validate_json_callback,
                 help="""
                  Parameters key,value pairs as JSON. If a key is not specified the existing (or default) value is used.
                  \b
                  \n
                  E.g. --params '{"CreateEventInfra":"True"}'
                  """),  # \b disables wrapping
    *REGION_OPTIONS
]


@click.group(help='Manage the data collector.')
def collector():
    """
    Group for any collector related subcommands
    """
    pass


@collector.command(help='Get link to the latest template. For initial deployment or manually upgrading.')
@click.pass_obj
@add_common_options(REGION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def get_template(ctx, aws_region):
    """
    Get the latest template for this account
    """
    CollectorManagementService(config=ctx['config'], aws_region_override=aws_region).echo_template()


@collector.command(help='Opens browser to CF console with a quick create link. For initial deployment.')
@click.pass_obj
@click.option('--dry', required=False, default=False, show_default=True, is_flag=True, help='Echos quick create link.')
@add_common_options(REGION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def open_link(ctx, aws_region, dry):
    """
    Open browser with a quick create link for deploying a data collector
    """
    CollectorManagementService(config=ctx['config'], aws_region_override=aws_region).launch_quick_create_link(dry=dry)


@collector.command(help='Deploy a data collector stack.')
@click.pass_obj
@add_common_options(DEPLOYMENT_OPTIONS)
@click.option('--stack-name', required=True, help='The name that is associated with the CloudFormation stack. '
                                                  'Must be unique in the region.')
@click.option('--enable-termination-protection/--no-enable-termination-protection', default=False, show_default=True,
              help='Enable termination protection for this stack.')
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def deploy(ctx, aws_profile, aws_region, params, stack_name, enable_termination_protection):
    """
    Deploy a collector for this account
    """
    CollectorManagementService(config=ctx['config'], aws_profile_override=aws_profile,
                               aws_region_override=aws_region).deploy_template(stack_name=stack_name,
                                                                               termination_protection=enable_termination_protection,
                                                                               new_params=params)


@collector.command(help='Upgrade to the latest version.')
@click.pass_obj
@add_common_options(DEPLOYMENT_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def upgrade(ctx, aws_profile, aws_region, params):
    """
    Upgrade the collector for this account
    """
    CollectorManagementService(config=ctx['config'], aws_profile_override=aws_profile,
                               aws_region_override=aws_region).upgrade_template(new_params=params)
