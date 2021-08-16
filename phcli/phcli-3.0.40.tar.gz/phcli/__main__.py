# -*- coding: utf-8 -*-

import click
from phcli.define_value import CLI_CLIENT_VERSION
from phcli.ph_max_auto.phcommand import maxauto
from phcli.ph_logs.__main__ import main as logs_main
from phcli.ph_lmd.__main__ import main as phlam_main
from phcli.ph_admin.__main__ import main as phadmin_main
from phcli.ph_sql.ph_hive.__main__ import main as phhive_main
from phcli.ph_data_clean.__main__ import main as clean_main
from phcli.ph_storage.back_up.__main__ import main as hdfs_back_up_main
from phcli.ph_storage.clean.__main__ import main as hdfs_clean_main
from phcli.ph_dag.__main__ import main as dag_main
from phcli.ph_ec2.__main__ import main as ec2_main
from phcli.ph_auto_setup.__main__ import main as auto_main

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def phcli():
    """
    Pharbers Command Line Interface.
    """


@phcli.command("version", short_help="打印版本")
def version():
    click.secho("v"+CLI_CLIENT_VERSION, fg='green', blink=True, bold=True)


phcli.add_command(logs_main)
phcli.add_command(maxauto)
phcli.add_command(phlam_main)
phcli.add_command(phadmin_main)
phcli.add_command(phhive_main)
phcli.add_command(clean_main)
phcli.add_command(hdfs_back_up_main)
phcli.add_command(hdfs_clean_main)
phcli.add_command(dag_main)
phcli.add_command(ec2_main)
phcli.add_command(auto_main)

if __name__ == '__main__':
    phcli()
