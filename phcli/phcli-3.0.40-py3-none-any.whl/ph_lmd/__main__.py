# -*- coding: utf-8 -*-

import click
from phcli.ph_lmd.model.__main__ import model
from phcli.ph_lmd.ph_deploy import deploy


@click.group("lmd", short_help='自动化部署一系列 Lambda 技术栈')
def main():
    """
    本脚本用于快速打包和部署 AWS Lambda 和 API Gateway
    """
    pass


main.add_command(model)
main.add_command(deploy)

if __name__ == '__main__':
    main()
