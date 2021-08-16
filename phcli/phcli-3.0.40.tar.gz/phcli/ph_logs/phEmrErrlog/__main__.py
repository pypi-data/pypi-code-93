import click
from phcli.ph_logs.phEmrErrlog.ph_emr_errlog import *

@click.command('errlogs',short_help='通过集群ID与步骤ID提取s3上错误日志')
@click.option("-c","--cluster-id",
              prompt="The cluster-id is",
              help="The cluster id"
             )
@click.option("-s","--step-id",
              prompt="The step-id is",
              help="The step id"
             )
@click.option("-n","--name",
              default=None,
              help="The log filename"
             )


def emr_errlogs(**kwargs):
    """
    对s3上的log进行抽取操作
    """
    try:
        phErrLogs(**kwargs).extractlog()
    except Exception as e:
        click.secho("操作失败: " + str(e), fg='red', blink=True, bold=True)
    else:
        click.secho("操作完成", fg='green', blink=True, bold=True)