# -*- coding: utf-8 -*-

import click
from phcli.ph_logs.phLogs import *
from phcli.ph_aws.ph_s3 import PhS3

@click.command("log", short_help='查看生产环境的运行日志')
@click.option('--follow/--no-follow', '-f', default=False,
              help='流式打印日志(暂不支持)')
@click.argument('job_id', nargs=1)
def main(follow, job_id):
    """
    本脚本用于查看生产环境的运行日志
    """
    phs3 = PhS3(access_key=PH_CLI_ACCESS_KEY, secret_key=PH_CLI_SECRET_KEY)
    print(phs3.open_object(CLI_BUCKET, LOG_PATH.format(CLI_VERSION, job_id + '.log')))
    
    
    
if __name__ == '__main__':
    main()    