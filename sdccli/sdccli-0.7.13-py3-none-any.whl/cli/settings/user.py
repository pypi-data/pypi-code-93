import click
import json
import sys
from sdccli.printer import print_list, print_item


_item_keys = ["id", "username", "firstName", "lastName", "enabled", "systemRole", "products"]
_list_keys = ["id", "username", "firstName", "lastName", "enabled"]


@click.group(name='user', short_help='Sysdig user operations')
def user():
    pass


@user.command(name='add', short_help="Invites a new user. This should result in an email notification to the specified address.")
@click.argument('email', nargs=1)
@click.argument('first_name', nargs=1)
@click.argument('last_name', nargs=1)
@click.option('--system-role', nargs=1, default="ROLE_USER",
              help="System-wide privilege level for this user regardless of team. specify 'ROLE_CUSTOMER' "
                   "to create an Admin. If not specified, default is a non-Admin ('ROLE_USER').")
@click.pass_obj
def add(cnf, email, first_name, last_name, system_role):
    """
    EMAIL: The email address of the user that will be invited to use Sysdig Monitor
    FIRST_NAME: The first name of the user being invited
    LAST_NAME: The last name of the user being invited
    """
    ok, res = cnf.sd.create_user_invite(email, first_name=first_name, last_name=last_name, system_role=system_role)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res["user"], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@user.command(name='list', short_help="List all users")
@click.pass_obj
def list(cnf):
    ok, res = cnf.sd.get_users()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_list(res, _list_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@user.command(name='update', short_help="Update the user information")
@click.argument('email', nargs=1)
@click.option('--first-name', nargs=1, help="The first name to be set")
@click.option('--last-name', nargs=1, help="The last name to be set")
@click.option('--system-role', nargs=1, default="ROLE_USER",
              help="System-wide privilege level for this user regardless of team. specify 'ROLE_CUSTOMER' "
                   "to create an Admin.")
@click.pass_obj
def upd(cnf, email, first_name, last_name, system_role):
    """
    EMAIL: The email address of the user that will be updated.
    """
    ok, res = cnf.sd.edit_user(email, firstName=first_name, lastName=last_name, systemRole=system_role)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print("Success")
    else:
        print("Error: " + str(res))
        sys.exit(1)


@user.command(name='me', short_help="Get my user info")
@click.pass_obj
def me(cnf):
    ok, res = cnf.sd.get_user_info()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res["user"], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@user.command(name='get', short_help="Get user")
@click.argument('email', nargs=1)
@click.pass_obj
def get(cnf, email):
    """
    EMAIL: email of the user to get
    """
    ok, res = cnf.sd.get_user(email)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@user.command(name='del', short_help="Delete users")
@click.argument('emails', nargs=-1, required=True)
@click.pass_obj
def delete(cnf, emails):
    """
    EMAILS: The emails of the users to delete
    """
    for email in emails:
        ok, res = cnf.sd.delete_user(email)

        if not ok:
            print("Error: " + str(res))
            sys.exit(1)

    print("Success")
