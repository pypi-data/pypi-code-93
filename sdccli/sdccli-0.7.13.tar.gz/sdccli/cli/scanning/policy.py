import click
import json
import sys
from sdccli.printer import print_list, print_item


_item_keys = ["id", "name", "comment", "rules"]
_list_keys = ["id", "name", "comment"]


@click.group(name='policy', short_help='Policy operations')
def policy():
    pass


@policy.command(name='add', short_help="Add a policy")
@click.argument('name', nargs=1)
@click.argument('rulesfile', type=click.Path(exists=True), nargs=1)
@click.option('--comment', nargs=1, help="A human-readable description.")
@click.option('--bundleid', nargs=1, help="Target bundle. If not specified, the currently active bundle will be used.")
@click.pass_obj
def add(cnf, name, rulesfile, comment, bundleid):
    """
    NAME: name for the new policy

    RULESFILE: A file with a json list of PolicyRule elements (while creating/updating a policy, new rule IDs will be created backend side)
    """
    # TODO: optionally pass the rules as string?
    try:
        with open(rulesfile) as f:
            rules = json.load(f)
    except Exception as error:
        print("Error parsing rules file (%s): %s" % (rulesfile, str(error)))
        sys.exit(1)

    ok, res = cnf.sdscanning.add_policy(name, rules, comment=comment, bundleid=bundleid)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@policy.command(name='list', short_help="List all policies")
@click.option('--bundleid', nargs=1, help="Target bundle. If not specified, the currently active bundle will be used.")
@click.pass_obj
def list(cnf, bundleid):
    ok, res = cnf.sdscanning.list_policies(bundleid=bundleid)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_list(res, _list_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@policy.command(name='get', short_help="Get a policy")
@click.argument('policyid', nargs=1)
@click.option('--bundleid', nargs=1, help="Target bundle. If not specified, the currently active bundle will be used.")
@click.pass_obj
def get(cnf, policyid, bundleid):
    """
    POLICYID: Policy ID to get
    """
    ok, res = cnf.sdscanning.get_policy(policyid, bundleid)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@policy.command(name='update', short_help="Update a policy")
@click.argument('policyid', nargs=1)
@click.argument('policyfile', type=click.Path(exists=True), nargs=1)
@click.option('--bundleid', nargs=1, help="Target bundle. If not specified, the currently active bundle will be used.")
@click.pass_obj
def upd(cnf, policyid, policyfile, bundleid):
    """
    POLICYID: Policy ID to update

    POLICYFILE: A file with a json description of the Policy
    """
    try:
        with open(policyfile) as f:
            policy = json.load(f)
    except Exception as error:
        print("Error parsing policy file (%s): %s" % (policyfile, str(error)))
        sys.exit(1)

    ok, res = cnf.sdscanning.update_policy(policyid, policy)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@policy.command(name='del', short_help="Delete a policy")
@click.argument('policyid', nargs=1)
@click.option('--bundleid', nargs=1, help="Target bundle. If not specified, the currently active bundle will be used.")
@click.pass_obj
def delete(cnf, policyid, bundleid):
    """
    POLICYID: Policy ID to delete
    """
    ok, res = cnf.sdscanning.delete_policy(policyid, bundleid=bundleid)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print("Success")
    else:
        print("Error: " + str(res))
        sys.exit(1)
