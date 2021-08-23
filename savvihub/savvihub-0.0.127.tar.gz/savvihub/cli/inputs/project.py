import os
from typing import Optional

import inquirer
import typer

from savvihub.api.exceptions import NotFoundAPIException
from savvihub.api.uploader import Uploader
from savvihub.api.zipper import Zipper
from savvihub.cli.commands.volume import parse_remote_volume_path
from savvihub.cli.constants import PROJECT_TYPE_CLI_DRIVEN, PROJECT_TYPE_VERSION_CONTROL
from savvihub.cli.exceptions import ExitException, InvalidGitRepository
from savvihub.cli.git import GitRepository
from savvihub.cli.typer import Context


def eval_project_type(project, project_type: str) -> bool:
    if project.type != project_type:
        raise ExitException(f'Project `{project.name}` type `{project.type}` does not match with `{project_type}`')
    return True


def project_name_callback(ctx: Context, project_name: str) -> str:
    organization_name = ctx.params['organization_name']
    try:
        git_repo = GitRepository()
        owner, repo_name, _ = git_repo._get_github_repo()
        if project_name:
            try:
                ctx.project = ctx.authenticated_client.project_read(organization_name, project_name)
            except NotFoundAPIException:
                raise ExitException(f'Project `{project_name}` does not exist in the organization `{organization_name}`.')

            if ctx.project.cached_git_owner_slug == owner and ctx.project.cached_git_repo_slug == repo_name:
                ctx.git_repo = git_repo
        else:
            projects = ctx.authenticated_client.project_list(organization_name).results
            matched_projects = []
            for project in projects:
                if project.cached_git_owner_slug == owner and project.cached_git_repo_slug == repo_name:
                    matched_projects.append(project)

            if len(matched_projects) == 1:
                ctx.project = matched_projects[0]
                ctx.git_repo = git_repo
            elif len(matched_projects) > 1:
                ctx.project = inquirer.prompt([inquirer.List(
                    'project',
                    message='Select project',
                    choices=[(p.name, p) for p in matched_projects],
                )], raise_keyboard_interrupt=True).get('project')
                ctx.git_repo = git_repo
            else:
                ctx.project = inquirer.prompt([inquirer.List(
                    'project',
                    message='Select project',
                    choices=[(p.name, p) for p in projects],
                )], raise_keyboard_interrupt=True).get('project')

        return ctx.project.name

    except InvalidGitRepository:
        if project_name:
            try:
                project = ctx.authenticated_client.project_read(organization_name, project_name)
                if eval_project_type(project, PROJECT_TYPE_CLI_DRIVEN):
                    ctx.project = project
            except NotFoundAPIException:
                raise ExitException(f'Project `{project_name}` does not exist in the organization `{organization_name}`.')
            return project_name
        else:
            projects = ctx.authenticated_client.project_list(organization_name).results
            if not projects:
                raise ExitException(f'No project found in organization `{organization_name}`')

            if len(projects) == 1:
                project = projects[0]
                if eval_project_type(project, PROJECT_TYPE_CLI_DRIVEN):
                    ctx.project = project
            else:
                project = inquirer.prompt([inquirer.List(
                    'project',
                    message='Select project',
                    choices=[(p.name, p) for p in projects],
                )], raise_keyboard_interrupt=True).get('project')
                if eval_project_type(project, PROJECT_TYPE_CLI_DRIVEN):
                    ctx.project = project
            return ctx.project.name


def local_project_callback(ctx: Context, local_project_url: str) -> Optional[str]:
    if ctx.project.type == PROJECT_TYPE_VERSION_CONTROL:
        return None

    if local_project_url:
        volume_id, dataset_version, path = parse_remote_volume_path(local_project_url)
        try:
            file = ctx.authenticated_client.volume_file_read(volume_id, path)
        except NotFoundAPIException:
            raise ExitException(f'Volume file not found: {local_project_url}')
        ctx.store['local_project_uploaded_path'] = file.path
        return file.path
    else:
        # Create zip file in the parent of the current working directory
        cwd = os.path.abspath(os.getcwd())
        zip_path = os.path.abspath(os.path.join(os.path.join(cwd, os.pardir), f'{ctx.project.name}.zip'))
        zipper = Zipper(zip_path, 'w')
        zipper.zipdir(cwd, zipper)
        zipper.close()

        typer.echo('Upload the zipped local project')
        uploaded = Uploader.upload(
            ctx.authenticated_client,
            local_path=zipper.filename,
            volume_id=ctx.project.volume_id,
            remote_path=os.path.basename(zipper.filename),
            progressable=typer.progressbar
        )
        local_project_path = uploaded.path

        os.remove(zipper.filename)

        ctx.store['local_project_uploaded_path'] = local_project_path

        return zipper.filename


project_name_option = typer.Option(None, '--project', callback=project_name_callback,
                                   help='If not present, uses git repository name of the current directory.')
