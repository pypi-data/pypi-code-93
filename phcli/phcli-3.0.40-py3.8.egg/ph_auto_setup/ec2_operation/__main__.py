import click
from phcli.ph_auto_setup.ec2_operation.ph_ec2_operation import PhEc2Operation

@click.command('ec2_operation', short_help='对ec2-instance的操作')
@click.option("-n", "--name",
              prompt="The ec2 instance name is",
              help="The ec2 instance name.")
@click.option("-i", "--ide",
              prompt="The ide is",
              type=click.Choice(["jupyter", "c9"]),
              help="The ide.")
@click.option("-o", "--operation",
              prompt="The operation on jupyter is",
              type=click.Choice(["create", "delete"]),
              help="The operation on jupyter.")
def ec2_operation(**kwargs):
    """
    对jupyter的创建或删除
    """
    try:

        PhEc2Operation(**kwargs).choice_ide()
    except Exception as e:
        click.secho("操作失败: " + str(e), fg='red', blink=True, bold=True)
    else:
        click.secho("操作完成", fg='green', blink=True, bold=True)


