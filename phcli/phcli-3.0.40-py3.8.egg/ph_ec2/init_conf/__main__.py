import click
from phcli.ph_ec2.init_conf.ph_init_conf import PhEC2Init

@click.command('init', short_help='ec2 init')
def ec2_init(**kwargs):
    """
    初始化c9 hadoop和spark的conf文件
    """
    try:
        PhEC2Init.init_conf()
    except Exception as e:
        click.secho("初始化失败: " + str(e), fg='red', blink=True, bold=True)
    else:
        click.secho("初始化完成", fg='green', blink=True, bold=True)


