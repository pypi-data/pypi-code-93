import click
from phcli.ph_admin import pg
from phcli.ph_admin.ph_models import Scope, Role


@click.group("role", short_help='角色管理工具')
def main():
    pass


@click.command("create", short_help='创建角色')
@click.option("-n", "--name", help="角色名", prompt="角色名")
@click.option("-d", "--description", help="角色描述", prompt="角色描述")
@click.option("-s", "--scope", multiple=True, help="角色权限")
def create_role(**kwargs):
    scopes = []
    for scope in kwargs['scope']:
        for scope in pg.query(Scope(), name=scope):
            scopes.append(scope.id)
    kwargs['scope'] = scopes

    result = pg.insert(Role(**kwargs))
    click.secho('添加成功'+str(result), fg='green', blink=True, bold=True)
    pg.commit()


@click.command("update", short_help='更新角色')
def update_role():
    click.secho('未实现', fg='red', blink=True, bold=True)
    pass


@click.command("list", short_help='列举角色')
def list_role():
    for role in pg.query(Role()):
        click.secho(str(role), fg='green', blink=True, bold=True)


@click.command("get", short_help='查找角色')
@click.option("-n", "--name", help="角色名", default=None)
def get_role(**kwargs):
    for role in pg.query(Role(**kwargs)):
        click.secho(str(role), fg='green', blink=True, bold=True)


@click.command("delete", short_help='删除角色')
@click.option("-n", "--name", help="角色名", prompt="角色名")
def delete_role(**kwargs):
    for role in pg.delete(Role(**kwargs)):
        click.secho(str(role), fg='green', blink=True, bold=True)
    pg.commit()


main.add_command(create_role)
main.add_command(update_role)
main.add_command(list_role)
main.add_command(get_role)
main.add_command(delete_role)
