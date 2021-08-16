# -*- coding: utf-8 -*-

import click
from phcli.ph_admin.ph_partner import main as partner_main
from phcli.ph_admin.ph_user import main as user_main
from phcli.ph_admin.ph_role import main as role_main
from phcli.ph_admin.ph_user import main as scope_main


@click.group("admin", short_help='管理员管理工具')
def main():
    """
    本脚本用于管理用户系统，如公司，用户，角色等
    """
    pass


main.add_command(partner_main)
main.add_command(user_main)
main.add_command(scope_main)
main.add_command(role_main)


if __name__ == '__main__':
    main()
