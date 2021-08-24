import click
import json
import sys
from sdccli.printer import print_list, print_item


_item_keys = ["accessKey", "enabled"]


@click.group(name='access-key', short_help='Sysdig access key operations')
def access_key():
    pass


@access_key.command(name='add', short_help="Create a new access key")
@click.pass_obj
def add(cnf):
    ok, res = cnf.sd.create_access_key()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res['customerAccessKey'], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@access_key.command(name='list', short_help="List all access keys")
@click.pass_obj
def lst(cnf):
    ok, res = cnf.sd.list_access_keys()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_list(res['customerAccessKeys'], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@access_key.command(name='disable', short_help="Disable an access key")
@click.argument('access_key', nargs=1)
@click.pass_obj
def disable(cnf, access_key):
    """
    ACCESS_KEY: the access key to be disabled.
    """
    ok, res = cnf.sd.disable_access_key(access_key)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res['customerAccessKey'], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@access_key.command(name='enable', short_help="Enable an access key")
@click.argument('access_key', nargs=1)
@click.pass_obj
def enable(cnf, access_key):
    """
    ACCESS_KEY: the access key to be enabled.
    """
    ok, res = cnf.sd.enable_access_key(access_key)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res['customerAccessKey'], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)
