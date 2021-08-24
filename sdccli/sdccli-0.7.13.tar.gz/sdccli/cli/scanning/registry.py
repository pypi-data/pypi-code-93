import click
import json
import sys
from sdccli.printer import print_list, print_item


_item_keys = ['registry', 'registry_user', 'registry_type', 'registry_verify', 'created_at', 'last_updated']
_list_keys = ["registry", "registry_type", "registry_user"]


@click.group(name='registry', short_help='Registry operations')
def registry():
    pass


@registry.command(name='add', short_help="Add a registry")
@click.argument('registry', nargs=1, required=True)
@click.argument('registry_user', nargs=1, required=True)
@click.argument('registry_pass', nargs=1, required=True)
@click.option('--insecure', is_flag=True, default=False, help="Allow connection to registry without SSL cert checks (ex: if registry uses a self-signed SSL certificate)")
@click.option('--registry-type', help="Specify the registry type (default='docker_v2')")
@click.option('--skip-validate', is_flag=True, help="Do not attempt to validate registry/creds on registry add")
@click.pass_obj
def add(cnf, registry, registry_user, registry_pass, insecure, registry_type, skip_validate):
    """
    REGISTRY: Full hostname/port of registry. Eg. myrepo.example.com:5000

    REGISTRY_USER: Username

    REGISTRY_PASS: Password
    """
    ok, res = cnf.sdscanning.add_registry(
        registry, registry_user, registry_pass,
        insecure=insecure,
        registry_type=registry_type,
        validate=not skip_validate)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res[0], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@registry.command(name='update', short_help="Update an existing registry")
@click.argument('registry', nargs=1, required=True)
@click.argument('registry_user', nargs=1, required=True)
@click.argument('registry_pass', nargs=1, required=True)
@click.option('--insecure', is_flag=True, default=False, help="Allow connection to registry without SSL cert checks (ex: if registry uses a self-signed SSL certificate)")
@click.option('--registry-type', default='docker_v2', help="Specify the registry type (default='docker_v2')")
@click.option('--skip-validate', is_flag=True, help="Do not attempt to validate registry/creds on registry add")
@click.pass_obj
def upd(cnf, registry, registry_user, registry_pass, insecure, registry_type, skip_validate):
    """
    REGISTRY: Full hostname/port of registry. Eg. myrepo.example.com:5000

    REGISTRY_USER: Username

    REGISTRY_PASS: Password
    """
    ok, res = cnf.sdscanning.update_registry(
        registry, registry_user, registry_pass,
        insecure=insecure,
        registry_type=registry_type,
        validate=not skip_validate)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res[0], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@registry.command(name='del', short_help="Delete a registry")
@click.argument('registries', nargs=-1, required=True)
@click.pass_obj
def delete(cnf, registries):
    """
    REGISTRIES: Full hostname/port of registries. Eg. myrepo.example.com:5000
    """
    for registry in registries:
        ok, res = cnf.sdscanning.delete_registry(registry)

        if not ok:
            print("Error: " + str(res))
            sys.exit(1)

    print("Success")


@registry.command(name='list', short_help="List all current registries")
@click.pass_obj
def list(cnf):
    ok, res = cnf.sdscanning.list_registry()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_list(res, _list_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@registry.command(name='get', short_help="Get a registry")
@click.argument('registry', nargs=1, required=True)
@click.pass_obj
def get(cnf, registry):
    """
    REGISTRY: Full hostname/port of registry. Eg. myrepo.example.com:5000
    """
    ok, res = cnf.sdscanning.get_registry(registry)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res[0], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)
