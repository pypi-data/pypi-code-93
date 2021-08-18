import subprocess

import inquirer
import typer
from terminaltables import AsciiTable

from savvihub.cli.exceptions import ExitException
from savvihub.cli.inputs.organization import organization_name_option
from savvihub.cli.typer import Typer, Context

project_app = Typer()


@project_app.callback()
def main():
    """
    View projects and pull source codes
    """


@project_app.command(user_required=True)
def list(
    ctx: Context,
    organization_name: str = organization_name_option,
):
    """
    Display a list of projects
    """
    projects_response = ctx.authenticated_client.project_list(organization_name)
    table = AsciiTable([
        ['NAME', 'TYPE', 'REPO'],
        *[[p.name, p.type, p.cached_git_http_url_to_repo or 'N/A']
          for p in projects_response.results],
    ])
    table.inner_column_border = False
    table.inner_heading_row_border = False
    table.inner_footing_row_border = False
    table.outer_border = False

    typer.echo(table.table)


@project_app.command(user_required=True)
def pull(
    ctx: Context,
    organization_name: str = organization_name_option,
):
    """
    Download the project source code
    """
    projects = ctx.authenticated_client.project_list(organization_name).results
    if not projects:
        raise ExitException(f'No version-control project found in organization `{organization_name}`')

    projects = [p for p in projects if p.type == 'version-control']

    if len(projects) == 1:
        project_name = projects[0].name
    else:
        project = inquirer.prompt([inquirer.List(
            'project',
            message='Select project',
            choices=[(p.name, p) for p in projects],
        )], raise_keyboard_interrupt=True).get('project')
        project_name = project.name

    project = ctx.authenticated_client.project_read(organization_name, project_name)
    github_token_response = ctx.authenticated_client.github_token()

    dirname = project.cached_git_repo_slug
    try:
        subprocess.check_output(['git', 'clone', f'https://{github_token_response.token}@github.com/{project.cached_git_owner_slug}/{project.cached_git_repo_slug}.git'])
    except subprocess.CalledProcessError:
        dirname = f'savvihub-{project.cached_git_repo_slug}'
        typer.echo(f'Falling back to \'{dirname}\'...')
        subprocess.check_output(['git', 'clone', f'https://{github_token_response.token}@github.com/{project.cached_git_owner_slug}/{project.cached_git_repo_slug}.git', dirname])

    subprocess.check_output(['rm', '-rf', f'{dirname}/.git'])
