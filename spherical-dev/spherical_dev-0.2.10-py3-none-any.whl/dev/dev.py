import invoke

from .hooks import install_git_hooks


@invoke.task
def dev(ctx):
    """Configure dev environemnt"""
    ctx.run('python -m pip install --upgrade pip -e ".[dev]"')
    install_git_hooks(ctx, force=True)
