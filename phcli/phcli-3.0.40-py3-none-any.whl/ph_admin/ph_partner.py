import click
from phcli.ph_admin import pg
from phcli.ph_admin.ph_models import Partner


@click.group("partner", short_help='公司管理工具')
def main():
    """
    公司管理工具
    """


@click.command("create", short_help='创建公司')
@click.option("-n", "--name", help="公司名", prompt="公司名")
@click.option("-a", "--address", help="公司地址", prompt="公司地址")
@click.option("-p", "--phoneNumber", help="公司电话", prompt="公司电话")
@click.option("-w", "--web", help="公司官网", prompt="公司官网")
def create_partner(**kwargs):
    kwargs['phoneNumber'] = kwargs.pop('phonenumber')
    result = pg.insert(Partner(**kwargs))
    click.secho('添加成功'+str(result), fg='green', blink=True, bold=True)
    pg.commit()


@click.command("update", short_help='更新公司')
def update_partner():
    click.secho('未实现', fg='red', blink=True, bold=True)
    pass


@click.command("list", short_help='列举公司')
def list_partner():
    for p in pg.query(Partner()):
        click.secho(str(p), fg='green', blink=True, bold=True)


@click.command("get", short_help='查找公司')
@click.option("-n", "--name", help="公司名", default=None)
@click.option("-a", "--address", help="公司地址", default=None)
@click.option("-p", "--phoneNumber", help="公司电话", default=None)
@click.option("-w", "--web", help="公司官网", default=None)
def get_partner(**kwargs):
    kwargs['phoneNumber'] = kwargs.pop('phonenumber')
    for p in pg.query(Partner(**kwargs)):
        click.secho(str(p), fg='green', blink=True, bold=True)


@click.command("delete", short_help='删除公司')
@click.option("-n", "--name", help="公司名", prompt="公司名")
def delete_partner(**kwargs):
    for p in pg.delete(Partner(**kwargs)):
        click.secho(str(p), fg='green', blink=True, bold=True)
    pg.commit()


main.add_command(create_partner)
main.add_command(update_partner)
main.add_command(list_partner)
main.add_command(get_partner)
main.add_command(delete_partner)
