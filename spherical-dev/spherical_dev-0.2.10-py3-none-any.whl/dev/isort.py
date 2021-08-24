import invoke


@invoke.task(
    help={
        'check-only': 'Perform check and show errors without actual fix.',
    },
)
def isort(ctx, check_only=False):
    """Check and optionally fix import sorting"""
    ctx.run(
        'isort -m 3 --lai 2 --tc '
        f'{"-c " if check_only else ""}'
        '--sg "alembic/*" .',
    )
