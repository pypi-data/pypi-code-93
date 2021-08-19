import click
import click_config_file

import montecarlodata.settings as settings
from montecarlodata.common.resources import CloudResourceService
from montecarlodata.errors import complain_and_abort
from montecarlodata.integrations.info.status import OnboardingStatusService
from montecarlodata.integrations.onboarding.data_lake.events import EventsOnboardingService
from montecarlodata.integrations.onboarding.data_lake.glue_athena import GlueAthenaOnboardingService
from montecarlodata.integrations.onboarding.data_lake.hive import HiveOnboardingService
from montecarlodata.integrations.onboarding.data_lake.presto import PrestoOnboardingService
from montecarlodata.integrations.onboarding.data_lake.spark import SparkOnboardingService, \
    SPARK_HTTP_MODE_CONFIG_TYPE, SPARK_DATABRICKS_CONFIG_TYPE, SPARK_BINARY_MODE_CONFIG_TYPE
from montecarlodata.integrations.onboarding.fields import HIVE_MYSQL_CONNECTION_TYPE, GLUE_CONNECTION_TYPE, \
    S3_METADATA_EVENT_TYPE, S3_QL_EVENT_TYPE, HIVE_S3_CONNECTION_TYPE
from montecarlodata.integrations.onboarding.operations.connection_ops import ConnectionOperationsService
from montecarlodata.integrations.onboarding.warehouse.warehouses import WarehouseOnboardingService
from montecarlodata.tools import add_common_options, validate_json_callback

# Options shared across commands
ROLE_OPTIONS = [
    click.option('--role', help='Assumable role ARN to use for accessing AWS resources.', required=False),
    click.option('--external-id', help='An external id, per assumable role conditions.', required=False),
]
S3_OPTIONS = [
    click.option('--bucket', help='S3 Bucket where query logs are contained.', required=True),
    click.option('--prefix', help='Path to query logs.', required=True),
    *ROLE_OPTIONS
]
EVENT_OPTIONS = [
    click.option('--enable/--disable', 'toggle', help='Enable or disable events. Enables if not specified.',
                 default=True)
]
DATABASE_OPTIONS = [
    click.option('--host', help='Hostname.', required=True),
    click.option('--user', help='Username with access to the database.', required=True),
    click.option('--database', help='Name of database.', required=True),
    click.password_option('--password', help='User\'s password.', prompt='Password for user', required=True)
]

CONNECTION_OPTIONS = [
    click.option('--connection-id', help='ID for the connection.', required=True, type=click.UUID)
]

# Shared command verbiage
METADATA_VERBIAGE = 'For metadata'
QL_VERBIAGE = 'For query logs'
SQL_VERBIAGE = 'For health queries'
EVENT_VERBIAGE = 'For tracking data freshness and volume at scale. Requires s3 notifications to be configured first'
REGION_VERBIAGE = 'If not specified the region the collector is deployed in is used'
WAREHOUSE_VERBIAGE = 'For metadata, query logs and metrics'


@click.group(help='Manage or integrate an asset with Monte Carlo.')
def integrations():
    """
    Group for any integration related subcommands
    """
    pass


@integrations.command(help=f'Setup a Hive metastore integration (MySQL). {METADATA_VERBIAGE}.')
@click.pass_obj
@click.option('--port', help='HTTP port.', default=3306, type=click.INT, show_default=True)
@click.option('--use-ssl', help='Use SSL to connect (using AWS RDS certificates).', required=False, is_flag=True,
              default=False, show_default=True)
@click.option('--catalog', help='Presto catalog name. For using multiple hive clusters with Presto. '
                                'Uses \'hive\' if not specified.', required=False)
@add_common_options(DATABASE_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_hive_metastore(ctx, host, port, user, password, database, use_ssl, catalog):
    """
    Onboard a hive metastore connection (MySQL)
    """
    HiveOnboardingService(config=ctx['config']).onboard_hive_mysql(host=host, port=port, user=user, password=password,
                                                                   dbName=database, use_ssl=use_ssl, catalog=catalog)


@integrations.command(help=f'Setup a Presto SQL integration. {SQL_VERBIAGE}.')
@click.pass_obj
@click.option('--host', help='Hostname.', required=True)
@click.option('--port', help='HTTP port.', default=8889, type=click.INT, show_default=True)
@click.option('--user', help='Username with access to catalog/schema.', required=False)
@click.password_option('--password', help='User\'s password.', prompt='Password for user (enter to skip)',
                       default='', required=False)
@click.option('--catalog', help='Mount point to access data source.', required=True)
@click.option('--schema', help='Schema to access.', required=True)
@click.option('--http-scheme', help='Scheme for authentication.',
              type=click.Choice(['http', 'https'], case_sensitive=True), required=True)
@click.option('--cert-file', help='Local SSL certificate file to upload to collector.', required=False,
              type=click.Path(dir_okay=False, exists=True))
@click.option('--cert-s3', help='Object path (key) to a certificate already uploaded to the collector.',
              required=False)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_presto(ctx, host, port, user, password, catalog, schema, http_scheme, cert_file, cert_s3):
    """
    Onboard a presto sql connection
    """
    if not password:
        password = None  # make explicitly null if not set. Prompts can't be None
    if cert_file is not None and cert_s3 is not None:
        complain_and_abort('Can have a cert-file or cert-s3-path, but not both')
    PrestoOnboardingService(config=ctx['config']).onboard_presto_sql(host=host, port=port, user=user, password=password,
                                                                     catalog=catalog, schema=schema,
                                                                     http_scheme=http_scheme, cert_file=cert_file,
                                                                     cert_s3=cert_s3)


@integrations.command(help=f'Setup a Hive SQL integration. {SQL_VERBIAGE}.')
@click.pass_obj
@click.option('--host', help='Hostname.', required=True)
@click.option('--database', help='Name of database.', required=False)
@click.option('--port', help='HTTP port.', default=10000, type=click.INT, show_default=True)
@click.option('--user', help='Username with access to hive.', required=True)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_hive(ctx, host, database, port, user):
    HiveOnboardingService(config=ctx['config']).onboard_hive_sql(host=host, database=database, port=port, username=user)


@integrations.command(help=f'Setup a Presto logs integration (S3). {QL_VERBIAGE}.')
@click.pass_obj
@add_common_options(S3_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_presto_logs(ctx, bucket, prefix, role, external_id):
    """
    Onboard a presto logs (s3) connection
    """
    PrestoOnboardingService(config=ctx['config']).onboard_presto_s3(bucket=bucket, prefix=prefix,
                                                                    assumable_role=role, external_id=external_id)


@integrations.command(help=f'Setup a Hive EMR logs integration (S3). {QL_VERBIAGE}.')
@click.pass_obj
@add_common_options(S3_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_hive_logs(ctx, bucket, prefix, role, external_id):
    """
    Onboard a hive emr (s3) connection
    """
    HiveOnboardingService(config=ctx['config']).onboard_hive_s3(bucket=bucket, prefix=prefix, assumable_role=role,
                                                                external_id=external_id)


@integrations.command(help=f'Setup a Glue integration. {METADATA_VERBIAGE}.')
@click.pass_obj
@click.option('--region', help=f'Glue catalog region. {REGION_VERBIAGE}.', required=False)
@add_common_options(ROLE_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_glue(ctx, role, external_id, region):
    """
    Onboard a glue connection
    """
    GlueAthenaOnboardingService(config=ctx['config']).onboard_glue(assumable_role=role, external_id=external_id,
                                                                   aws_region=region)


@integrations.command(help=f'Setup an Athena integration. For query logs and health queries.')
@click.pass_obj
@click.option('--catalog', help='Glue data catalog. If not specified the AwsDataCatalog is used.', required=False)
@click.option('--workgroup',
              help='Workbook for running queries and retrieving logs. If not specified the primary is used.',
              required=False)
@click.option('--region', help=f'Athena cluster region. {REGION_VERBIAGE}.', required=False)
@add_common_options(ROLE_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_athena(ctx, catalog, workgroup, role, external_id, region):
    """
    Onboard an athena connection
    """
    GlueAthenaOnboardingService(config=ctx['config']).onboard_athena(catalog=catalog, workgroup=workgroup,
                                                                     assumable_role=role, external_id=external_id,
                                                                     aws_region=region)


@integrations.command(help=f'Setup a Spark integration in Thrift binary mode. {SQL_VERBIAGE}.')
@click.pass_obj
@click.option('--host', help='Hostname.', required=True)
@click.option('--database', help='Name of database.', required=True)
@click.option('--port', help='Port.', default=10000, type=click.INT, show_default=True)
@click.option('--user', help='Username with access to spark.', required=True)
@click.password_option('--password', help='User\'s password.', prompt='Password for user', required=True)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_spark_binary_mode(ctx, host, database, port, user, password):
    """
    Onboard a spark connection, thrift binary mode
    """
    SparkOnboardingService(config=ctx['config']).onboard_spark(SPARK_BINARY_MODE_CONFIG_TYPE,
                                                               host=host, database=database, port=port, username=user,
                                                               password=password)


@integrations.command(help=f'Setup a Spark integration in Thrift HTTP mode. {SQL_VERBIAGE}.')
@click.pass_obj
@click.option('--url', help='HTTP URL.', required=True)
@click.option('--user', help='Username with access to spark.', required=True)
@click.password_option('--password', help='User\'s password.', prompt='Password for user', required=True)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_spark_http_mode(ctx, url, user, password):
    """
    Onboard a spark connection, thrift http mode
    """
    SparkOnboardingService(config=ctx['config']).onboard_spark(SPARK_HTTP_MODE_CONFIG_TYPE,
                                                               url=url, username=user, password=password)


@integrations.command(help=f'Setup a Spark integration for Databricks. {SQL_VERBIAGE}.')
@click.pass_obj
@click.option('--workspace-url', help='Databricks workspace URL.', required=True)
@click.option('--workspace-id', help='Databricks workspace ID.', required=True)
@click.option('--cluster-id', help='Databricks cluster ID.', required=True)
@click.password_option('--token', help='Databricks access token.', prompt='Databricks access token', required=True)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_spark_databricks(ctx, workspace_url, workspace_id, cluster_id, token):
    """
    Onboard a spark connection, databricks
    """
    SparkOnboardingService(config=ctx['config']).onboard_spark(SPARK_DATABRICKS_CONFIG_TYPE,
                                                               workspace_url=workspace_url, workspace_id=workspace_id,
                                                               cluster_id=cluster_id, token=token)


@integrations.command(help=f'Setup a Redshift integration. {WAREHOUSE_VERBIAGE}.')
@click.pass_obj
@click.option('--port', help='HTTP port.', default=5439, type=click.INT, show_default=True)
@click.option('--name', help='Friendly name for the warehouse.', required=True)
@add_common_options(DATABASE_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_redshift(ctx, host, port, user, password, database, name):
    """
    Onboard a redshift connection
    """
    WarehouseOnboardingService(config=ctx['config']).onboard_redshift(host=host, port=port, user=user,
                                                                      password=password, dbName=database,
                                                                      warehouseName=name)


@integrations.command(help=f'Setup a Snowflake integration. {WAREHOUSE_VERBIAGE}.')
@click.pass_obj
@click.option('--user', help='User with access to snowflake.', required=True)
@click.option('--account', help='Snowflake account name.', required=True)
@click.option('--warehouse', help='Name of the warehouse for the user.', required=True)
@click.password_option('--password', help='User\'s password.', prompt='Password for user', required=True)
@click.option('--name', help='Friendly name for the warehouse.', required=True)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_snowflake(ctx, user, account, warehouse, password, name):
    """
    Onboard a snowflake connection
    """
    WarehouseOnboardingService(config=ctx['config']).onboard_snowflake(account=account, password=password, user=user,
                                                                       warehouse=warehouse, warehouseName=name)


@integrations.command(help=f'Setup a BigQuery integration. {WAREHOUSE_VERBIAGE}.')
@click.pass_obj
@click.option('--key-file', help='JSON Key file.', type=click.Path(exists=True), required=True)
@click.option('--name', help='Friendly name for the warehouse.', required=True)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_bigquery(ctx, key_file, name):
    """
    Onboard a BigQuery connection
    """
    WarehouseOnboardingService(config=ctx['config']).onboard_bq(ServiceFile=key_file, warehouseName=name)


@integrations.command(help=f'Toggle S3 metadata events for a Hive/Presto lake. {EVENT_VERBIAGE}.')
@click.pass_obj
@add_common_options(EVENT_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def toggle_hive_metadata_events(ctx, toggle):
    """
    Toggle s3 metadata events for a hive lake
    """
    EventsOnboardingService(config=ctx['config']).toggle_event_configuration(enable=toggle,
                                                                             connection_type=HIVE_MYSQL_CONNECTION_TYPE,
                                                                             event_type=S3_METADATA_EVENT_TYPE)


@integrations.command(help=f'Toggle S3 metadata events for a Glue/Athena lake. {EVENT_VERBIAGE}.')
@click.pass_obj
@add_common_options(EVENT_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def toggle_glue_metadata_events(ctx, toggle):
    """
    Toggle s3 metadata events for a glue lake
    """
    EventsOnboardingService(config=ctx['config']).toggle_event_configuration(enable=toggle,
                                                                             connection_type=GLUE_CONNECTION_TYPE,
                                                                             event_type=S3_METADATA_EVENT_TYPE)


@integrations.command(help=f'Toggle S3 query log events. {EVENT_VERBIAGE}.')
@click.pass_obj
@add_common_options(EVENT_OPTIONS)
@add_common_options(ROLE_OPTIONS)
@click.option('--type', help='Type of the integration.', type=click.Choice(['hive-emr'], case_sensitive=True),
              required=True, default='hive-emr', show_default=True)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def toggle_ql_events(ctx, toggle, role, external_id, type):
    """
    Toggle s3 query log events for a lake
    """
    EventsOnboardingService(config=ctx['config']).toggle_event_configuration(enable=toggle,
                                                                             connection_type=HIVE_S3_CONNECTION_TYPE,
                                                                             event_type=S3_QL_EVENT_TYPE,
                                                                             assumable_role=role,
                                                                             external_id=external_id,
                                                                             format_type=type)


@integrations.command(help=f'List all active integrations.', name='list')
@click.pass_obj
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def display_integrations(ctx):
    """
    Display active integrations
    """
    OnboardingStatusService(config=ctx['config']).display_integrations()


@integrations.command(help='Create an IAM role from the provided policy FILE. '
                           'The returned role ARN and external id should be used for adding lake assets.')
@click.pass_obj
@click.argument('file', type=click.Path(dir_okay=False, exists=True))
@click.option('--aws-profile', required=False,
              help='Override the AWS profile used by the CLI, which determines where the role is created. '
                   'This can be helpful when the account that manages the asset is not the same as the collector.')
def create_role(ctx, file, aws_profile):
    """
    Create a collector compatible role from the provided policy
    """
    CloudResourceService(config=ctx['config'], aws_profile_override=aws_profile).create_role(path_to_policy_doc=file)


@integrations.command(help=f'Update credentials for a connection.')
@click.pass_obj
@add_common_options(CONNECTION_OPTIONS)
@click.option('--changes', help="""
              Credential key,value pairs as JSON.
              \b
              \n
              E.g. --changes '{"user":"Apollo"}'
              """, required=True, callback=validate_json_callback)
@click.option('--skip-validation', help='Skip validating credentials.', default=False, show_default=True, is_flag=True)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def update_credentials(ctx, connection_id, changes, skip_validation):
    """
    Update credentials for a connection
    """
    ConnectionOperationsService(config=ctx['config']).update_credentials(connection_id=connection_id, changes=changes,
                                                                         should_validate=not skip_validation)


@integrations.command(help=f'Remove a connection. Deletes any associated jobs, monitors, etc.')
@click.pass_obj
@add_common_options(CONNECTION_OPTIONS)
@click.option('--no-prompt', help='Don\'t ask for confirmation.', default=False, show_default=True, is_flag=True)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def remove_connection(ctx, connection_id, no_prompt):
    """
    Remove connection by ID
    """
    ConnectionOperationsService(config=ctx['config']).remove_connection(connection_id=connection_id,
                                                                        no_prompt=no_prompt)
