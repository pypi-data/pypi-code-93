import click
from phcli.ph_auto_setup.emr_operation.__main__ import emr_operation
from phcli.ph_auto_setup.emr_operation.__main__ import put_id2ssm
from phcli.ph_auto_setup.ec2_operation.__main__ import ec2_operation

@click.group("auto_setup", short_help='自动化操作EMR集群，EC2实例系列命令')
def main():
    """
    本脚本用于执行自动化操作EMR集群，EC2实例系列命令
    """
    pass


main.add_command(emr_operation)
main.add_command(ec2_operation)
main.add_command(put_id2ssm)



if __name__ == '__main__':
    main()