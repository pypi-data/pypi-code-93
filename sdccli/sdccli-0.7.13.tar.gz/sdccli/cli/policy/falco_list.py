import click
import json
import sys
from sdccli.printer import print_list, print_item


_item_keys = ["id", "name", "items", "filename"]
_list_keys = ["ids", "name"]


@click.group(name='falco-list', short_help='Sysdig Secure policy falco list operations')
def falco_list():
    pass


@falco_list.command(name='add', short_help="Add a falco list")
@click.argument('name', nargs=1)
@click.option('--item', nargs=1, multiple=True, help="An item as represented in the yaml List.")
@click.pass_obj
def add(cnf, name, item):
    """
    NAME: the name of the new falco list.
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    ok, res = cnf.sdsecure.add_falco_list(name, item if item else [])

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@falco_list.command(name='list', short_help="List all falco lists")
@click.pass_obj
def lst(cnf):
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    ok, res = cnf.sdsecure.list_falco_lists()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_list(res, _list_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@falco_list.command(name='get', short_help="Get falco list")
@click.argument('falco_list', nargs=1)
@click.pass_obj
def get(cnf, falco_list):
    """
    FALCO_LIST: Falco list (id or name) to get
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    try:
        id = int(falco_list)
        ok, res = cnf.sdsecure.get_falco_list_id(id)
    except ValueError:
        ok, res = cnf.sdsecure.get_falco_lists_group(falco_list)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        if isinstance(res, list):
            for rule in res:
                print_item(rule, _item_keys)
        else:
            print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@falco_list.command(name='update', short_help="Update falco list")
@click.argument('falco_list', nargs=1)
@click.option('--item', nargs=1, multiple=True, help="An item as represented in the yaml List. I twill replace the existing items in the list.")
@click.pass_obj
def upd(cnf, falco_list, item):
    """
    FALCO_LIST: Falco list id to update
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    ok, res = cnf.sdsecure.update_falco_list(falco_list, item if item else [])

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@falco_list.command(name='del', short_help="Delete falco lists")
@click.argument('falco_lists', nargs=-1, required=True)
@click.pass_obj
def delete(cnf, falco_lists):
    """
    FALCO_LISTS: Falco list ids to delete
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    for fl in falco_lists:
        ok, res = cnf.sdsecure.delete_falco_list(fl)

        if not ok:
            print("Error: " + str(res))
            sys.exit(1)

    print("Success")
