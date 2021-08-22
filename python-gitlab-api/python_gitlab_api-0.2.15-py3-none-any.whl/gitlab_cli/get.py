"""REST Entities CLI

Wrappers to gitlab.resources classes to expose command lines entrypoints.

This package is meant to be usable and used in a Gitlab-CI pipeline, so if there is a standard GitLab-CI environmental
variable which can be used as default for the entities, it should be used.

Environmental variables are the same exposed by Gitlab-CI
See <https://docs.gitlab.com/ee/ci/variables/predefined_variables.html>

The only required enviromental variable is CI_API_V4_URL, which needs to be set, and it is not psosible (so far) to be
passed as CLI

Arguments are taken as normal CLI paramters, or by environmental variables.

Attribute to filter the request are passed as "K=V" strings on the CLI.

Examples:
    $ get-releases order_by=released_at
    $ get-releases order_by=released_at --only-latest
    $ get-releases ---only-latest


This module exposes entities as CLI entry points, not complex queries.

This means that it should not publish things like 'get user by username', which is implemented by the Users entity, by
passing the 'username=USERNAME' parameter.
The correct way to implement it is by calling the entity with
such parameter:
    get-users username=$GITLAB_USER_LOGIN
"""
from typing import Iterable
from typing import Dict

import click

from gitlab import utils
from gitlab import resources

from . import data

# From this point functions will reflect the name of the entities, with the same capitalisation. This breaks the
# snake-case rule, hence invalid-name is disabled to enable the entity name matching
# pylint: disable=invalid-name


def prepare_attrs(parameters: Iterable[str]) -> Dict:
    """Get a dictionary of paramters from an iterables of 'K=V' strings
    """
    return {p.split('=')[0]:p.split('=')[1] for p in  parameters}

@click.command()
@click.argument('parameter', nargs=-1, type=str)
@click.option('--project-id', type=int, envvar='CI_PROJECT_ID')
@click.option('--tag-name', type=str)
def Release(parameter: Iterable[str], project_id: int, tag_name: str):
    """Read a specific Release entity"""
    attrs = prepare_attrs(parameter)
    result = resources.Release(data.ENDPOINT, project_id, tag_name).read(attrs)

    utils.ppjson(result)

@click.command()
@click.argument('parameter', nargs=-1, type=str)
@click.option('--only-latest', default=False, is_flag=True)
@click.option('--project-id', type=int, envvar='CI_PROJECT_ID')
def Releases(parameter: Iterable[str], only_latest: bool, project_id):
    """Read Releases entity"""
    attrs = prepare_attrs(parameter)
    result = resources.Releases(data.ENDPOINT, project_id).read(attrs)

    if only_latest:
        result = result[0]

    utils.ppjson(result)


@click.command()
@click.argument('parameter', nargs=-1, type=str)
@click.option('--user-id', type=int, envvar='GITLAB_USER_ID')
def User(parameter: Iterable[str], user_id: int):
    """Read a specific User entity"""
    attrs = prepare_attrs(parameter)
    result = resources.User(data.ENDPOINT, user_id).read(attrs)
    utils.ppjson(result)


@click.command()
@click.argument('parameter', nargs=-1, type=str)
@click.option('--project-id', type=int, envvar='CI_PROJECT_ID')
def Project(parameter: Iterable[str], project_id: int):
    """Read a specific Project entity"""
    attrs = prepare_attrs(parameter)
    result = resources.Project(data.ENDPOINT, project_id).read(attrs)
    utils.ppjson(result)


@click.command()
@click.argument('parameter', nargs=-1, type=str)
def Projects(parameter: Iterable[str]):
    """Read Projects entity"""
    attrs = prepare_attrs(parameter)
    result = resources.Projects(data.ENDPOINT).read(attrs)
    utils.ppjson(result)


@click.command()
@click.argument('parameter', nargs=-1, type=str)
@click.option('--group-id', required=True, type=int)
def GroupWikis(parameter: Iterable[str], group_id: int):
    """Read Releases entity"""
    attrs = prepare_attrs(parameter)
    result = resources.GroupWikis(data.ENDPOINT, group_id).read(attrs)
    utils.ppjson(result)


@click.command()
@click.argument('parameter', nargs=-1, type=str)
@click.option('--group-id', required=True, type=int)
@click.option('--slug', type=str)
def GroupWiki(parameter: Iterable[str], group_id: int, slug: str):
    """Read Releases entity"""
    attrs = prepare_attrs(parameter)
    result = resources.GroupWiki(data.ENDPOINT, group_id, slug).read(attrs)
    utils.ppjson(result)
