import click
from phcli.ph_ec2.init_conf.__main__ import ec2_init


@click.group("ec2", short_help='ec2系列命令')
def main():
    """
    本脚本用于执行ec2系列命令
    """
    pass


main.add_command(ec2_init)


if __name__ == '__main__':
    main()