import click
import json
import sys
from sdccli.printer import print_list, print_item


_item_keys = ['subscription_id', 'subscription_key', "active", 'created_at', 'last_updated']
_list_keys = ["subscription_key", "active"]


@click.group(name='repo', short_help='Repository operations')
def repo():
    pass


@repo.command(name='add', short_help="Add a repository")
@click.option('--noautosubscribe', is_flag=True, help="If set, instruct the engine to disable subscriptions for any discovered tags.")
@click.option('--lookuptag', help="Specify a tag to use for repo tag scan if 'latest' tag does not exist in the repo.")
@click.argument('repo', nargs=1)
@click.pass_obj
def add(cnf, repo, noautosubscribe, lookuptag):
    """
    REPO: Input repository can be in the following formats: registry/repo
    """
    ok, res = cnf.sdscanning.add_repo(
        repo,
        autosubscribe=not noautosubscribe,
        lookuptag=lookuptag)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res[0], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@repo.command(name='list', short_help="List added repositories")
@click.pass_obj
def listrepos(cnf):
    ok, res = cnf.sdscanning.list_repos()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_list(res, _list_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@repo.command(name='get', short_help="Get a repository")
@click.argument('repo', nargs=1)
@click.pass_obj
def get(cnf, repo):
    """
    REPO: Input repository can be in the following formats: registry/repo
    """
    ok, res = cnf.sdscanning.get_repo(repo)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res[0], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@repo.command(name='del', short_help="Delete a repository from the watch list (does not delete already analyzed images)")
@click.argument('repos', nargs=-1, required=True)
@click.pass_obj
def delete(cnf, repos):
    """
    REPOS: Input repo can be in the following formats: registry/repo
    """
    for repo in repos:
        ok, res = cnf.sdscanning.delete_repo(repo)

        if not ok:
            print("Error: " + str(res))
            sys.exit(1)

    print("Success")


@repo.command(name='unwatch', short_help="Instruct engine to stop automatically watching the repo for image updates")
@click.argument('repo', nargs=1)
@click.pass_obj
def unwatch(cnf, repo):
    """
    REPO: Input repo can be in the following formats: registry/repo
    """
    ok, res = cnf.sdscanning.unwatch_repo(repo)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res[0], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@repo.command(name='watch', short_help="Instruct engine to start automatically watching the repo for image updates")
@click.argument('repo', nargs=1)
@click.pass_obj
def watch(cnf, repo):
    """
    REPO: Input repo can be in the following formats: registry/repo
    """
    ok, res = cnf.sdscanning.watch_repo(repo)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res[0], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)
