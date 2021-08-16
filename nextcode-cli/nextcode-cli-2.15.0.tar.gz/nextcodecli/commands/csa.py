import sys, os
import click
from click import command, argument, pass_context, secho, echo
import logging
from tabulate import tabulate

import nextcode
from nextcode.utils import random_string
from nextcode.csa import CSASession
from nextcode.exceptions import AuthServerError, CSAError

from nextcodecli.utils import abort, dumps, print_tab
from nextcodecli.csa_import import process_sample, parse

log = logging.getLogger(__name__)


@click.group()
@click.option(
    '-u',
    '--username',
    envvar='CSA_USERNAME',
    prompt=True,
    help="User in the CSA instance, typically administrator",
)
@click.option(
    '-p',
    '--password',
    envvar='CSA_PASSWORD',
    prompt=True,
    help="Password for user",
    hide_input=True,
)
@pass_context
def cli(ctx, username, password):
    """
    Manage CSA users

    Requires the CSA admin username and passwords, which you can put into envivonment as CSA_USERNAME and CSA_PASSWORD
    """
    client = nextcode.Client()
    root_url = client.profile.root_url
    session = CSASession(root_url, username, password)
    log.info("Managing users on CSA server %s..." % session.csa_url)
    ctx.obj.session = session


@command(help="Create a user in the CSA instance")
@argument('user_name', nargs=1)
@argument('password', nargs=1)
@pass_context
def create_user(ctx, user_name, password):
    try:
        ctx.obj.session.create_user(user_name, password)
    except CSAError as ex:
        abort(ex)
    secho("User '%s' has been created" % (user_name), bold=True)


@command(help="Add a user to a project")
@argument('user_name', nargs=1)
@argument('project', nargs=1)
@click.option('-r', '--role', default="researcher", help='Role for this user')
@pass_context
def add_to_project(ctx, user_name, project, role):
    try:
        ctx.obj.session.add_user_to_project(user_name, project, role)
    except CSAError as ex:
        abort(ex)
    secho("User '%s' has been added to project %s" % (user_name, project), bold=True)


@command(help="Get a list of all projects in the CSA instance")
@click.option('-r', '--raw', 'is_raw', is_flag=True)
@pass_context
def projects(ctx, is_raw):
    projects = ctx.obj.session.get_project_names()
    if is_raw:
        echo(dumps(projects))
    else:
        table = tabulate([[p] for p in projects], headers=["Project Name"])
        echo(table)


@command(help="Get information about a CSA project")
@argument('project_name', nargs=1)
@click.option('-r', '--raw', 'is_raw', is_flag=True)
@pass_context
def project(ctx, project_name, is_raw):
    project = ctx.obj.session.get_project(project_name)
    if is_raw:
        echo(dumps(project))
        return

    print_tab("Name", project["name"])
    print_tab("Key", project["key"])
    print_tab("ID", project["id"])
    print_tab("Org", project["organization_key"])
    print_tab("State", project["state"])
    print_tab("Ref", project["reference_version"])
    try:
        credentials = ctx.obj.session.get_s3_credentials_for_project(project_name)
    except Exception as ex:
        abort(ex)
    buckets = []
    for bucket, creds in credentials.items():
        if not creds["project_name"]:
            bucket += " (system)"
        buckets.append(bucket)

    print_tab("S3 Buckets", ", ".join(buckets))


@click.command("import")
@click.argument("manifest_file", nargs=1)
@click.argument("project_name", nargs=1)
@click.option('-r', '--random', 'random_pn', is_flag=True, help="Randomize PN")
@pass_context
def import_sample(ctx, manifest_file, project_name, random_pn):
    if not os.path.isfile(manifest_file):
        abort(f"Could not open manifest file {manifest_file}")
    project = ctx.obj.session.get_project(project_name)
    if not project:
        abort(f"Project {project_name} not found")
    org_key = project['organization_key']

    manifest = parse(manifest_file)
    for sample_id, sample in manifest.items():
        subject_id = sample["subject_id"]
        if random_pn:
            sample_id += "-{}".format(random_string())
            subject_id = sample_id
        contents = {
            'sample': sample,
            'org_key': org_key,
            'sample_id': sample_id,
            'subject_id': subject_id,
            'project_name': project_name,
            'skip_processing_state': False,
        }
        process_sample(ctx.obj.session, contents)


@command(help="Create a new CSA project")
@argument('project_name', nargs=1)
@click.option(
    '-o', '--org', default="internal_org", help='Organization that the project belongs to'
)
@click.option('-r', '--ref', default="hg38", help='Reference data version')
@pass_context
def create_project(ctx, project_name, org, ref):
    existing_project = ctx.obj.session.get_project(project_name)
    if existing_project:
        abort(f"Project {project_name} already exists")
    try:
        ret = ctx.obj.session.create_project(project_name, org, ref)
    except CSAError as ex:
        abort(ex)
    secho(f"Project {project_name} has been created.")


cli.add_command(create_user)
cli.add_command(add_to_project)
cli.add_command(projects)
cli.add_command(project)
cli.add_command(import_sample)
cli.add_command(create_project)
