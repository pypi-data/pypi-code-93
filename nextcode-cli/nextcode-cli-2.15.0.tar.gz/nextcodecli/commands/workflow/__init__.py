import sys
import click
from nextcode import get_service
from nextcode.exceptions import InvalidProfile
from nextcodecli.utils import check_profile

status_to_color = {
    'PENDING': 'yellow',
    'COMPLETED': 'green',
    'STARTED': 'yellow',
    'ERROR': 'red',
    'KILLED': 'red',
    'CANCELLED': 'white',
}


@click.group()
@click.pass_context
def cli(ctx):
    """Root subcommand for workflow functionality"""
    if ctx.obj.service is None:
        check_profile(ctx)
        ctx.obj.service = ctx.obj.client.service("workflow")
        ctx.obj.session = ctx.obj.service.session
        ctx.obj.job = None


from nextcodecli.commands.workflow.jobs import jobs
from nextcodecli.commands.workflow.job import job
from nextcodecli.commands.workflow.run import run as run_cmd
from nextcodecli.commands.workflow.projects import projects
from nextcodecli.commands.workflow.status import status, smoketest
from nextcodecli.commands.workflow.pipelines import pipelines

cli.add_command(jobs)
cli.add_command(job)
cli.add_command(run_cmd)
cli.add_command(projects)
cli.add_command(status)
cli.add_command(smoketest)
cli.add_command(pipelines)
