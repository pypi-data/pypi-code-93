#!/usr/bin/env python

import click
from click import command, option, pass_context
from tabulate import tabulate

from nextcode.exceptions import ServerError

from nextcodecli.commands.workflow import status_to_color
from nextcodecli.utils import get_logger, abort, dumps, print_warn, print_error

log = get_logger()


@command(help="List jobs")
@option('--mine', 'is_mine', is_flag=True, help='List jobs from me')
@option('-u', '--user', 'user_name', help='User to filter for')
@option('-s', '--status', 'status', default=None, help='Filter status')
@option('-p', '--project', 'project', default=None, help='Filter by project name')
@option('--pipeline', 'pipeline', default=None, help='Filter by pipeline name')
@option('--page', 'is_page', is_flag=True, help='Page results')
@option('--running', 'is_running', is_flag=True, help='Only show jobs in pending/running state')
@option('--context', help='Filter by context')
@option(
    '--completed',
    'is_completed',
    is_flag=True,
    help='Only show jobs in failed/cancelled/completed state',
)
@option('-n', '--num', default=20, help='Maximum number of jobs to return')
@option(
    '-o',
    '--output',
    type=click.Choice(['normal', 'wide', 'json']),
    default='normal',
    help='Format output',
)
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json for further processing')
@option('--params-columns',  help='A comma-delimited list of parameter names to show as columns')
@pass_context
def jobs(
    ctx,
    is_mine,
    user_name,
    status,
    project,
    pipeline,
    is_page,
    is_running,
    context,
    is_completed,
    num,
    output,
    is_raw,
    params_columns
):
    svc = ctx.obj.service
    if is_mine:
        try:
            user_name = svc.current_user['email']
        except KeyError:
            abort("You appear not to be logged in")

    state = None
    if is_running:
        state = "running"
    elif is_completed:
        state = "completed"
    try:
        jobs = svc.get_jobs(
            user_name,
            status,
            project=project,
            pipeline=pipeline,
            limit=num,
            state=state,
            context=context,
        )
    except ServerError as e:
        abort(str(e))
    is_wide = output == 'wide'
    if is_raw or (output == 'json'):
        click.echo(dumps(jobs))
        return

    fields = [
        'job_id',
        'pipeline_name',
        'user_name',
        'project_name',
        'submit_date',
        'duration',
        'estimated_cost',
        'status',
    ]
    process_header = '#su/#ru/#fa/#ab/#co'
    if is_wide:
        fields.extend(['desc', 'context', 'complete_date', 'pod', process_header])
    if params_columns:
        for p in  params_columns.split(','):
            fields.append(f"param_{p}")
    jobs_list = []
    for job in jobs:
        job_list = []
        for f in fields:
            v = None
            if hasattr(job, f):
                v = getattr(job, f) or 'N/A'
            if f in ('submit_date', 'complete_date'):
                try:
                    v = v.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    v = ''
            elif f == 'status':
                col = status_to_color.get(v)
                v = click.style(v, fg=col, bold=True)
            elif f == 'pod':
                v = job.details.get('pod_name', v)
            elif f == process_header:
                submitted = job.details.get('process_stats', {}).get('SUBMITTED', 0)
                completed = job.details.get('process_stats', {}).get('COMPLETED', 0)
                running = job.details.get('process_stats', {}).get('STARTED', 0)
                aborted = job.details.get('process_stats', {}).get('ABORTED', 0)
                failed = job.details.get('process_stats', {}).get('FAILED', 0)
                v = f'{submitted}/{running}/{failed}/{aborted}/{completed}'
            elif f == 'desc':
                v = job.description or ""
                if len(v) > 50:
                    v = v[:47] + "..."
            elif f == 'estimated_cost':
                if not job.cost_amount:
                    v = click.style("N/A", fg='yellow', bold=True)
                else:
                    v = f"{job.cost_amount:.2f} {job.cost_currency}"
            elif f.startswith('param_'):
                param_name = f[6:]
                v = job.details.get('launch_config', {}).get('nextflow_params', {}).get(param_name)
            job_list.append(v)

        jobs_list.append(job_list)
    tbl = tabulate(jobs_list, headers=fields)
    if len(jobs_list) > 30 and is_page:
        click.echo_via_pager(tbl)
    else:
        click.echo(tbl)
