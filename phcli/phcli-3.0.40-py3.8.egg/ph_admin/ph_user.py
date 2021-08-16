import click
import hashlib
from datetime import datetime
from phcli.ph_admin.ph_models import Account, Role, Partner


@click.group("user", short_help='用户管理工具')
def main():
    pass


@click.command("create", short_help='创建用户')
@click.option("-n", "--name", help="用户名", prompt="用户名")
@click.option("-p", "--password", help="用户密码", prompt="用户密码", hide_input=True, confirmation_prompt=True)
@click.option("--phoneNumber", help="用户电话", prompt="用户电话")
@click.option("-r", "--defaultRole", help="默认角色", prompt="默认角色", default='test')
@click.option("-e", "--email", help="用户邮箱", prompt="用户邮箱")
@click.option("-E", "--employer", help="所属公司", prompt="所属公司", default='test')
@click.option("--firstName", help="名", prompt="名")
@click.option("--lastName", help="姓", prompt="姓")
def create_user(**kwargs):
    from phcli.ph_admin import pg
    kwargs['phoneNumber'] = kwargs.pop('phonenumber')
    kwargs['defaultRole'] = kwargs.pop('defaultrole')
    kwargs['firstName'] = kwargs.pop('firstname')
    kwargs['lastName'] = kwargs.pop('lastname')

    sha256 = hashlib.sha256()
    sha256.update(kwargs['password'].encode('utf-8'))
    kwargs['password'] = sha256.hexdigest()
    default_role = kwargs.pop('defaultRole')
    employer = kwargs.pop('employer')

    roles = pg.query(Role(), name=default_role)
    role = roles[0] if roles else None
    if role:
        kwargs['defaultRole'] = role.id

    employers = pg.query(Partner(), name=employer)
    employer = employers[0] if employers else None
    if employer:
        kwargs['employer'] = employer.id

    account = pg.insert(Account(**kwargs))
    if role:
        role.accountRole.append(str(account.id))
        role.modified = datetime.now()
        pg.update(role)

    if employer:
        employer.employee.append(str(account.id))
        employer.modified = datetime.now()
        pg.update(employer)

    click.secho('添加成功'+str(account), fg='green', blink=True, bold=True)
    pg.commit()


@click.command("update", short_help='更新用户')
@click.option("-n", "--name", help="用户名", prompt="用户名")
@click.option("-p", "--password", help="用户密码", default=None, hide_input=True, confirmation_prompt=True)
@click.option("--phoneNumber", help="用户电话", default=None)
@click.option("-R", "--defaultRole", help="默认角色", default=None)
@click.option("-e", "--email", help="用户邮箱", default=None)
@click.option("-E", "--employer", help="所属公司", default=None)
@click.option("--firstName", help="名", default=None)
@click.option("--lastName", help="姓", default=None)
def update_user(**kwargs):
    from phcli.ph_admin import pg
    kwargs['phoneNumber'] = kwargs.pop('phonenumber')
    kwargs['defaultRole'] = kwargs.pop('defaultrole')
    kwargs['firstName'] = kwargs.pop('firstname')
    kwargs['lastName'] = kwargs.pop('lastname')

    if kwargs['password']:
        sha256 = hashlib.sha256()
        sha256.update(kwargs['password'].encode('utf-8'))
        kwargs['password'] = sha256.hexdigest()

    user = pg.query(Account(), name=kwargs['name'])
    user = user[0] if user else None
    if not user:
        click.secho('用户不存在: '+str(kwargs['name']), fg='red', blink=True, bold=True)
        return

    default_role = kwargs.pop('defaultRole')
    if default_role:
        new_role = pg.query(Role(), name=default_role)
        new_role = new_role[0] if new_role else None
        if not new_role:
            click.secho('角色不存在: '+default_role, fg='yellow', blink=True, bold=True)

        if user.defaultRole:
            old_role = pg.query(Role(), id=user.defaultRole)
            old_role = old_role[0] if old_role else None
        else:
            old_role = None

        # 修改的名字和原有的一样，判定为没变化
        if new_role and old_role and new_role.id == old_role.id:
            click.secho('角色无变化, name='+new_role.name, fg='yellow', blink=True, bold=True)
        else:
            if old_role:
                old_role.accountRole.remove(user.id)
                old_role.modified = datetime.now()
                pg.update(old_role)
                user.defaultRole = None

            if new_role:
                new_role.accountRole.append(user.id)
                new_role.modified = datetime.now()
                pg.update(new_role)
                user.defaultRole = new_role.id

    employer = kwargs.pop('employer')
    if employer:
        new_employer = pg.query(Partner(), name=employer)
        new_employer = new_employer[0] if new_employer else None
        if not new_employer:
            click.secho('公司不存在: '+employer, fg='yellow', blink=True, bold=True)

        if user.employer:
            old_employer = pg.query(Partner(), id=user.employer)
            old_employer = old_employer[0] if old_employer else None
        else:
            old_employer = None

        # 修改的名字和原有的一样，判定为没变化
        if new_employer and old_employer and new_employer.id == old_employer.id:
            click.secho('公司无变化, name='+new_employer.name, fg='yellow', blink=True, bold=True)
        else:
            if old_employer:
                old_employer.employee.remove(user.id)
                old_employer.modified = datetime.now()
                pg.update(old_employer)
                user.employer = None

            if new_employer:
                new_employer.employee.append(user.id)
                new_employer.modified = datetime.now()
                pg.update(new_employer)
                user.employer = new_employer.id

    user = pg.update(user)
    click.secho('更新成功'+str(user), fg='green', blink=True, bold=True)
    pg.commit()


@click.command("list", short_help='列举用户')
def list_user():
    from phcli.ph_admin import pg
    for a in pg.query(Account()):
        click.secho(str(a), fg='green', blink=True, bold=True)


@click.command("get", short_help='查找用户')
@click.option("-n", "--name", help="用户名", default=None)
@click.option("--phoneNumber", help="用户电话", default=None)
@click.option("-e", "--email", help="用户邮箱", default=None)
@click.option("--firstName", help="名", default=None)
@click.option("--lastName", help="姓", default=None)
def get_user(**kwargs):
    from phcli.ph_admin import pg
    for a in pg.query(Account(**kwargs)):
        click.secho(str(a), fg='green', blink=True, bold=True)


@click.command("delete", short_help='删除用户')
@click.option("-n", "--name", help="用户名", prompt="用户名")
def delete_user(**kwargs):
    from phcli.ph_admin import pg
    for user in pg.delete(Account(**kwargs)):
        if user.defaultRole:
            old_role = pg.query(Role(), id=user.defaultRole)
            old_role = old_role[0] if old_role else None
            if old_role:
                old_role.accountRole.remove(user.id)
                old_role.modified = datetime.now()
                pg.update(old_role)

        if user.employer:
            old_employer = pg.query(Partner(), id=user.employer)
            old_employer = old_employer[0] if old_employer else None
            if old_employer:
                old_employer.employee.remove(user.id)
                old_employer.modified = datetime.now()
                pg.update(old_employer)

        click.secho('删除成功'+str(user), fg='green', blink=True, bold=True)
    pg.commit()



main.add_command(create_user)
main.add_command(update_user)
main.add_command(list_user)
main.add_command(get_user)
main.add_command(delete_user)
