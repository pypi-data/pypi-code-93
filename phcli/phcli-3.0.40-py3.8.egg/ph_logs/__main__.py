# -*- coding: utf-8 -*-

import click
from phcli.ph_logs.phEmrErrlog.__main__ import emr_errlogs
from phcli.ph_logs.phLogs.__main__ import main

@click.group("logs", short_help='针对日志的操作')
def main():
    """
    抽取查看log日志
    """
    pass

main.add_command(emr_errlogs)
main.add_command(main)

if __name__ == '__main__':
    main()
