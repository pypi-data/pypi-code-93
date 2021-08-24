import click
import json
import sys
from sdccli.printer import print_list, print_item


_item_keys = ["id", "name", "condition", "filename"]
_list_keys = ["ids", "name"]


@click.group(name='falco-macro', short_help='Sysdig Secure policy falco macro operations')
def falco_macro():
    pass


@falco_macro.command(name='add', short_help="Add a falco macro")
@click.argument('name', nargs=1)
@click.argument('condition', nargs=1)
@click.pass_obj
def add(cnf, name, condition):
    """
    NAME: the name of the new falco macro.

    CONDITION: the full condition text exactly as represented in the yaml file.
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    ok, res = cnf.sdsecure.add_falco_macro(name, condition)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@falco_macro.command(name='list', short_help="List all falco macros")
@click.pass_obj
def lst(cnf):
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    ok, res = cnf.sdsecure.list_falco_macros()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_list(res, _list_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@falco_macro.command(name='get', short_help="Get falco macro")
@click.argument('falco_macro', nargs=1)
@click.pass_obj
def get(cnf, falco_macro):
    """
    FALCO_MACRO: Falco macro (id or name) to get
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    try:
        id = int(falco_macro)
        ok, res = cnf.sdsecure.get_falco_macro_id(id)
    except ValueError:
        ok, res = cnf.sdsecure.get_falco_macros_group(falco_macro)

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


@falco_macro.command(name='update', short_help="Update falco list")
@click.argument('falco_macro', nargs=1)
@click.argument('condition', nargs=1)
@click.pass_obj
def upd(cnf, falco_macro, condition):
    """
    FALCO_LIST: Falco list id to update

    CONDITION: the full condition text exactly as represented in the yaml file.
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    ok, res = cnf.sdsecure.update_falco_macro(falco_macro, condition)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@falco_macro.command(name='del', short_help="Delete falco macro")
@click.argument('falco_macros', nargs=-1, required=True)
@click.pass_obj
def delete(cnf, falco_macros):
    """
    FALCO_MACROS: Falco macro ids to delete
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    for fm in falco_macros:
        ok, res = cnf.sdsecure.delete_falco_macro(fm)

        if not ok:
            print("Error: " + str(res))
            sys.exit(1)

    print("Success")
