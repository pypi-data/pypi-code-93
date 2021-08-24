import invoke


@invoke.task
def flake(ctx):
    """Execute flake code checks"""
    ctx.run((
        'flake8 --max-line-length=127'
        ' --inline-quotes="single"'
        ' --multiline-quotes="single"'
        ' --docstring-quotes="double"'
    ))
