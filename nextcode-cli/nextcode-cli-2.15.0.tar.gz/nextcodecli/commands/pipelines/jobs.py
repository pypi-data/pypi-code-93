#!/usr/bin/env python

import click
import dateutil
import json
from tabulate import tabulate
from textwrap import dedent
from nextcodecli.utils import dumps, abort
from nextcodecli.pipelines.cmdutils import status_to_color


@click.command(help="List running jobs. Use switches to filter.")
@click.option('--mine', 'is_mine', is_flag=True, help='List jobs from me')
@click.option('--user', 'user_name', help='User to filter for')
@click.option('--all', 'is_all', is_flag=True, help='Do not only list running jobs')
@click.option('--latest', 'is_latest', is_flag=True, help='View the top 10 latest submitted jobs')
@click.option('--raw', 'is_raw', is_flag=True, help='Dump raw json for further processing')
@click.option('--page', 'is_page', is_flag=True, help='Page results')
@click.option('--status', 'status', default=None, help='Filter status')
@click.option('--start-date', 'start_date', default=None, help='Only show jobs after this date')
@click.option(
    '--end-date',
    'end_date',
    default=None,
    help='Only show jobs before (and not including) this date',
)
@click.option('--num', default=50, help='Maximum number of jobs to return')
@click.option(
    '--filter',
    'job_filter',
    default='',
    help='Filter for jobs, with format KEY=VALUE,' 'KEY2=VALUE2',
)
@click.option(
    '--fields',
    'add_fields',
    default='',
    help='Additional fields you wish to view, '
    'separated by comma. Also supports '
    'removing default fields by adding a - '
    'to the beginning of the fieldname.',
)
@click.pass_context
def jobs(
    ctx,
    is_mine,
    user_name,
    is_all,
    is_latest,
    is_raw,
    is_page,
    status,
    start_date,
    end_date,
    num,
    job_filter,
    add_fields,
):

    svc = ctx.obj.service
    session = svc.session
    fields = [
        'job_id',
        'user_name',
        'date_submitted',
        'duration',
        'pipeline_name',
        'sample_name',
        'region',
        'status',
    ]

    rm_missing = []
    if add_fields:
        try:
            for f in add_fields.split(','):
                if f[0] == '-':
                    try:
                        fields.remove(f[1:])
                    except ValueError:
                        rm_missing.append(f[1:])
                elif f not in fields:
                    fields.append(f)
            if rm_missing:
                rm_err = "Error: Field(s) {} not in default fields, ignored.".format(
                    ','.join(sorted(rm_missing))
                )
                click.echo(click.style(rm_err, fg='red'))
        except Exception:
            abort("Fields are incorrectly formatted")
    data = {'field': fields, 'start_date': start_date, 'end_date': end_date}
    if status:
        data['status'] = status.upper()
        if is_mine or is_latest or is_all:
            abort("You cannot combine --status with other filter flags")

    if is_mine:
        data['user_name'] = svc.current_user['preferred_username']
        data['status'] = 'ALL'
    elif user_name:
        data['user_name'] = user_name
        data['status'] = 'ALL'
    elif is_latest or is_all:
        data['status'] = 'ALL'
    data['limit'] = num
    if job_filter:
        try:
            data.update({i.split('=')[0]: i.split('=')[1] for i in job_filter.split(',')})
        except Exception as e:
            abort("Invalid filter format: KEY=VALUE expected, separated by comma.")
    resp = session.get(session.url_from_endpoint('jobs'), json=data)
    try:
        resp.raise_for_status()
    except Exception as e:
        abort(json.dumps(resp.json(), indent=4))
    jobs = resp.json()['jobs']
    if is_raw:
        click.echo(dumps(jobs))
        return

    if is_mine:
        click.echo("All my jobs:")
    elif is_latest:
        click.echo("Latest jobs:")
    elif is_all:
        click.echo("All jobs:")
    else:
        click.echo("Currently running jobs:")
    if jobs:
        err = set()
        jobs_list = []
        for j in jobs:
            job_list = []
            det = j.get('details', {})
            if det and isinstance(det, dict):
                j = dict(list(det.items()) + list(j.items()))
                j.pop('details')
            date_submitted = None
            for f in fields:
                try:
                    v = j[f]
                    if isinstance(v, dict):
                        v = dedent(json.dumps(v, indent=4, separators=(',', ':'))[1:-1])
                    elif isinstance(v, list):
                        v = '\n'.join(
                            dedent(json.dumps(h, indent=4, separators=(',', ':'))[1:-1]) for h in v
                        )
                    elif f == 'date_submitted':
                        date_submitted = dateutil.parser.parse(v)
                        v = dateutil.parser.parse(v).strftime("%Y-%m-%d %H:%M")
                    elif f == 'duration' and v:
                        hours, remainder = divmod(v, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        v = '%02d:%02d:%02d' % (int(hours), int(minutes), int(seconds))
                    elif f == 'status':
                        col = status_to_color.get(v, '')
                        v = click.style(v, fg=col, bold=True)
                    elif f == 'spot':
                        v = "Yes" if v else "No"
                        spot_instance = (j.get('instances') or [{}])[0].get("is_spot")
                        if v == "Yes" and not spot_instance:
                            v += click.style(" NO", fg='red')
                    job_list.append(v)
                except KeyError:
                    err.add(f)
            if det.get("old_job_id"):
                job_list[0] = '{} ({})'.format(j['job_id'], det.get("old_job_id"))
            jobs_list.append(job_list)
        [fields.remove(j) for j in err]
        if is_latest:
            jobs_list = jobs_list[:10]
        tbl = tabulate(jobs_list, headers=fields)
        if len(jobs_list) > 30 and is_page:
            click.echo_via_pager(tbl)
        else:
            click.echo(tbl)
            click.echo("{} jobs found".format(len(jobs_list)))
        if err:
            out = "Error: Field(s) {} not found, skipped.".format(','.join(sorted(err)))
            click.echo(click.style(out, fg='red'))
    else:
        click.echo(
            "No jobs found. Run 'nextcode pipelines jobs --latest' "
            "to view the latest completed jobs"
        )
