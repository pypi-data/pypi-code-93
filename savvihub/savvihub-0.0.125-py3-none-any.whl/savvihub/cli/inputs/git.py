import os
import tempfile
from typing import Optional

import inquirer
import typer
import requests

from savvihub.api.file_object import DownloadableFileObject
from savvihub.api.uploader import Uploader
from savvihub.cli.constants import PROJECT_TYPE_CLI_DRIVEN
from savvihub.cli.exceptions import ExitException
from savvihub.cli.typer import Context


def git_ref_callback(ctx: Context, git_ref: str) -> Optional[str]:
    if ctx.project.type == PROJECT_TYPE_CLI_DRIVEN:
        return None

    if git_ref:
        git_ref = git_ref.strip()
        if ctx.git_repo and not ctx.git_repo.check_revision_in_remote(git_ref):
            raise ExitException(f'Git commit {git_ref} does not exist in a remote repository.')
        return git_ref

    if ctx.git_repo is None:
        raise ExitException('Run it inside a git-initialized directory or set --git-ref option.')

    return ctx.git_repo.commit_ref


def git_branch_callback(ctx: Context, git_branch: str) -> Optional[str]:
    if ctx.project.type == PROJECT_TYPE_CLI_DRIVEN:
        return None

    if git_branch:
        return git_branch

    if ctx.git_repo is None:
        raise ExitException('Run it inside a git-initialized directory or set --git-branch option.')

    return ctx.git_repo.branch


def git_diff_callback(ctx: Context, git_diff_url: str) -> Optional[str]:
    if ctx.project.type == PROJECT_TYPE_CLI_DRIVEN:
        return None

    assert ctx.params['git_ref']
    if ctx.params['ignore_git_diff']:
        return None

    diff_file = None
    if git_diff_url:
        if git_diff_url.startswith('https://') or git_diff_url.startswith('http://'):
            diff_file = tempfile.NamedTemporaryFile(suffix='.patch')
            d = DownloadableFileObject(git_diff_url, os.path.dirname(diff_file.name), os.path.basename(diff_file.name))
            session = requests.Session()
            session.headers = ctx.authenticated_client.auth_header
            d.download(session=session)
            diff_file.seek(0)
    else:
        if ctx.git_repo is None:
            return None

        typer.echo(f'Run experiment with revision {ctx.git_repo.commit_ref[:7]} ({ctx.git_repo.branch})')
        typer.echo(f'Commit: {ctx.git_repo.get_commit_message(ctx.git_repo.commit_ref)}')
        if not ctx.git_repo.is_head:
            typer.echo('Your current revision does not exist in remote repository. '
                       'SavviHub will use latest remote branch revision hash and uncommitted diff.')
        typer.echo('')

        has_diff, diff_status = ctx.git_repo.get_current_diff_status(ctx.git_repo.commit_ref)
        if has_diff:
            typer.echo('Diff to be uploaded: ')

            uncommitted_files = diff_status.get('uncommitted')
            untracked_files = diff_status.get('untracked')

            if uncommitted_files:
                typer.echo('  Changes not committed')
                typer.echo('\n'.join([f'    {x}' for x in uncommitted_files]))
                typer.echo('')
            if untracked_files:
                typer.echo(f'  Untracked files:')
                typer.echo('\n'.join([f'    {x}' for x in untracked_files]))
                typer.echo('')

            answer = inquirer.prompt([inquirer.List(
                'question',
                message='Run experiment with diff?',
                choices=[
                    ('[1] Run experiment with uncommitted and untracked changes.', 1),
                    ('[2] Run experiment with uncommitted changes.', 2),
                    ('[3] Run experiment without any changes.', 3),
                    ('[4] Abort.', 4),
                ],
            )], raise_keyboard_interrupt=True)['question']

            if answer == 1:
                diff_file = ctx.git_repo.get_current_diff_file(ctx.git_repo.commit_ref, with_untracked=True)
            elif answer == 2:
                diff_file = ctx.git_repo.get_current_diff_file(ctx.git_repo.commit_ref, with_untracked=False)
            elif answer == 3:
                pass
            else:
                raise ExitException('Aborted.')

    if diff_file:
        typer.echo('Generating diff patch file...')
        uploaded = Uploader.upload(
            ctx.authenticated_client,
            local_path=diff_file.name,
            volume_id=ctx.project.volume_id,
            remote_path=os.path.basename(diff_file.name),
            progressable=typer.progressbar,
        )
        diff_file_path = uploaded.path
        diff_file.close()

        ctx.store['git_diff_uploaded_path'] = diff_file_path

    return git_diff_url
