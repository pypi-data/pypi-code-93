import click
from phcli.ph_admin import pg
from phcli.ph_admin.ph_models import Scope, Role


@click.group("scope", short_help='权限管理工具')
def main():
    pass


@click.command("create", short_help='创建权限')
@click.option("-n", "--name", help="权限名", prompt="权限名")
@click.option("-d", "--description", help="权限描述", prompt="权限描述")
@click.option("-s", "--scopePolicy", help="权限策略", prompt="权限策略")
@click.option("-o", "--owner", multiple=True, help="附加角色")
def create_scope(**kwargs):
    kwargs['scopePolicy'] = kwargs.pop('scopepolicy')

    owners = []
    for owner in kwargs['owner']:
        for owner in pg.query(Role(), name=owner):
            owners.append(owner.id)
    kwargs['owner'] = owners

    result = pg.insert(Scope(**kwargs))
    click.secho('添加成功'+str(result), fg='green', blink=True, bold=True)
    pg.commit()


@click.command("update", short_help='更新权限')
def update_scope():
    click.secho('未实现', fg='red', blink=True, bold=True)
    pass


@click.command("list", short_help='列举权限')
def list_scope():
    for scope in pg.query(Scope()):
        click.secho(str(scope), fg='green', blink=True, bold=True)


@click.command("get", short_help='查找权限')
@click.option("-n", "--name", help="权限名", default=None)
def get_scope(**kwargs):
    for scope in pg.query(Scope(**kwargs)):
        click.secho(str(scope), fg='green', blink=True, bold=True)


@click.command("delete", short_help='删除权限')
@click.option("-n", "--name", help="权限名", prompt="权限名")
def delete_scope(**kwargs):
    for scope in pg.delete(Scope(**kwargs)):
        click.secho(str(scope), fg='green', blink=True, bold=True)
    pg.commit()


main.add_command(create_scope)
main.add_command(update_scope)
main.add_command(list_scope)
main.add_command(get_scope)
main.add_command(delete_scope)
