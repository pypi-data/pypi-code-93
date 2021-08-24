import os
import pathlib
import shutil

import invoke
import pkg_resources


PRE_COMMIT_FILE = '.pre-commit-config.yaml'


@invoke.task
def create_git_hooks_config(ctx, force=False):
    """Internal subtask to create default pre-commit config"""
    if os.path.exists(PRE_COMMIT_FILE) and not force:
        raise invoke.Exit('config already exists', 1)
    with open(PRE_COMMIT_FILE, 'wb') as dst:
        src = pkg_resources.resource_stream(
            __package__,
            'configs/pre-commit-config.yaml',
        )
        shutil.copyfileobj(src, dst)
    exclude = pathlib.Path('.git') / 'info' / 'exclude'
    if exclude.exists():
        exclude_text = exclude.read_text()
        if 'pre-commit-config.yaml' not in exclude_text:
            exclude_text += '/.pre-commit-config.yaml' + os.linesep
            exclude.write_text(exclude_text)


@invoke.task(
    help={
        'force': 'Replace any existing git hooks with the pre-commit script.',
    },
)
def install_git_hooks(ctx, force=False):
    """Generate pre push and pre commit scripts in .git directory of project"""
    create_git_hooks_config(ctx, force=force)
    ctx.run(
        ' '.join((
            'pre-commit install',
            '--allow-missing-config',
            '--hook-type pre-commit',
            '--hook-type pre-push',
            '--overwrite' if force else '',
        )),
    )
