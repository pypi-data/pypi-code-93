import click


@click.command("setproject")
@click.argument('project', nargs=1)
@click.pass_context
def cli(ctx, project):
    """
    Set the current project.

    This command will set the project context in the client and save it
    into the current profile. A project is required to run any gor query
    or to inspect already run queries.
    """
    ctx.obj.client.profile.project = project
    click.secho("Project has been set to: {}".format(project), bold=True)
