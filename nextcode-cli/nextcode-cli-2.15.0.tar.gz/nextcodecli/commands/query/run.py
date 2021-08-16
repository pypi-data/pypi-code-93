#!/usr/bin/env python
import click
import os
from tabulate import tabulate

from nextcode.services.query.exceptions import MissingRelations, QueryError
from nextcode.exceptions import ServerError

from ...queryapi import get_results
from ...utils import get_logger, abort, print_tab, dumps
from . import check_project

log = get_logger(name='commands.query', level='INFO')


@click.command()
@click.option('-q', '--query', 'gor_query', help='Inline query to run')
@click.option('-j', '--jobtype', 'job_type', default="default", help='Job type to run the query')
@click.option('-f', '--queryfile', 'query_file', help='File which contains GOR query')
@click.option('-o', '--output', 'output_file', help='File to write results to')
@click.option('-l', '--limit', 'limit', default=0, help='Limit the number of rows returned')
@click.option(
    '-r', '--relations', 'relations', multiple=True, help='Virtual relation mapping for query'
)
@click.option(
    '-n',
    '--nowait',
    is_flag=True,
    default=False,
    help='Run command without waiting for it to finish',
)
@click.option(
    '-d', '--details', is_flag=True, default=False, help='Show progress details for running query'
)
@click.option(
    '--raw', 'is_raw', is_flag=True, default=False, help='Raw JSON response from endpoint'
)
@click.pass_context
@check_project
def run(
    ctx, gor_query, job_type, query_file, output_file, limit, relations, nowait, details, is_raw
):
    """
    Execute a GOR query via the Query API.

    You can either run a query directly or from a file.

    This command will automatically wait for the query
    to complete and fetch results but if you are running a long
    query you can use the --nowait option and then fetch results
    via the results command.

    """
    svc = ctx.obj.service

    prepared_relations = []
    for r in relations:
        lst = r.split("=", 1)
        name = lst[0]
        filename = lst[1]
        if not os.path.exists(filename):
            abort("File '{}' not found".format(filename))
        with open(filename) as f:
            data = f.read()
        prepared_relations.append({"name": name, "data": data})
    # options: (project, query)
    if query_file:
        with open(os.path.expanduser(query_file)) as f:
            gor_query = f.read()

    if not gor_query:
        click.secho("Specify --query or --queryfile", fg='red')
        return
    qry = None
    try:
        qry = svc.execute(gor_query, relations=prepared_relations, job_type=job_type, nowait=True)
        click.secho(
            "Running query {} against project {}...".format(qry.query_id, svc.project), bold=True
        )
        if not nowait:
            qry.wait()
    except MissingRelations as ex:
        click.secho(repr(ex), fg="red")
        txt = "You can add the relations with: "
        for r in ex.relations:
            txt += "-r {}=[filename]".format(r)
        click.echo(txt)
        return
    except KeyboardInterrupt:
        if qry:
            try:
                qry.cancel()
            except QueryError:
                pass
            abort("Query {} has been cancelled".format(qry.query_id))
        return None

    if qry.failed:
        click.secho(
            "Query {} failed with message: {}".format(qry.query_id, qry.status_message), fg="red"
        )
        return
    if is_raw:
        click.echo(dumps(qry.raw))
        return

    if qry.running:
        click.echo("Query {} is now running.".format(qry.query_id))
        click.echo("View query process with: nextcode query info {}".format(qry.query_id))
        return
    click.secho(
        "Query {} completed successfully in {} ms".format(qry.query_id, qry.duration), fg="green"
    )

    get_results(qry, limit, None, None, output_file)


@click.command()
@click.argument('project', nargs=1)
@click.pass_context
def project(ctx, project):
    """
    Set the current project.

    This command will set the project context in the client and save it
    into the current profile. A project is required to run any gor query
    or to inspect already run queries.
    """
    svc = ctx.obj.service
    svc.client.profile.project = project
    click.secho("Project has been set to: {}".format(project), bold=True)


@click.command()
@click.argument('query_id', nargs=1)
@click.option(
    '--raw', 'is_raw', is_flag=True, default=False, help='Raw JSON response from endpoint'
)
@click.pass_context
@check_project
def info(ctx, query_id, is_raw):
    """
    Retrieve information about a gor query by ID
    """
    svc = ctx.obj.service
    qry = svc.get_query(query_id)

    if is_raw:
        click.echo(dumps(qry.raw))
        return
    data = qry.raw
    print_tab("ID", data['id'])
    print_tab("Submitted", data['submit_date'])
    print_tab("User", data['user_name'])
    print_tab("Available", data['available'])
    print_tab("Template", data['template_name'] or "None (ad-hoc)")
    status = data['status']
    col = 'red'
    if status == 'DONE':
        col = 'green'
    elif status == 'RUNNING':
        col = 'yellow'
    print_tab("Status", click.style(status, fg=col, bold=True))

    if status == 'DONE':
        print_tab("Columns", data['stats']['column_count'])
        print_tab("Rows", data['stats']['line_count'])
        print_tab("Size", "%.1f MB" % (data['stats']['size_bytes'] / 1024 / 1024))
        run_time = data['stats']['end_timestamp'] - data['stats']['start_timestamp']
        queue_time = data['stats']['start_timestamp'] - data['stats']['submit_timestamp']
        print_tab("Queue Time", "%.2f sec" % (queue_time / 1000.0))
        print_tab("Run Time", "%.2f sec" % (run_time / 1000.0))
    elif status == 'FAILED':
        click.echo(data['error']['description'])


@click.command()
@click.argument('query_id', nargs=1)
@click.option(
    '-o',
    '--output',
    'output_file',
    help="Name of the output file for the results. Otherwise will dump a maximum of 100 rows to the console.",
)
@click.option(
    '-l', '--limit', 'limit', default=0, help="Maximum number of results to return (default all)"
)
@click.option(
    '-f',
    '--filter',
    'filt',
    help="GOR filter string to apply to the results. For example '-f \"chrom = 'chr1'\"",
)
@click.option(
    '-s',
    '--sort',
    'sort',
    help="Comma separated list of columns to sort on, including direction. Example: -s \"POS asc,Chrom desc\"",
)
@click.option('-j', '--json', 'is_json', is_flag=True, default=False)
@click.pass_context
@check_project
def results(ctx, query_id, output_file, limit, filt, sort, is_json):
    """
    Retrieve results from a completed GOR query.

    You can apply additional filters and sort options which
    are applied to the results before fetching.

    If output file is omitted only the first 100 lines are fetched.
    Use the --output option to fetch the entire result set.
    """
    svc = ctx.obj.service

    qry = svc.get_query(query_id)
    if not qry.done:
        abort("Query has status %s which is not DONE" % qry.status)

    get_results(qry, limit, filt, sort, output_file, is_json)


@click.command()
@click.argument('query_id', nargs=1)
@click.argument('filename', nargs=1)
@click.pass_context
@check_project
def download(ctx, query_id, filename):
    """
    Retrieve results from a completed GOR query to file.
    """
    svc = ctx.obj.service

    qry = svc.get_query(query_id)
    if not qry.done:
        abort("Query has status %s which is not DONE" % qry.status)

    line_count = qry.stats.get("line_count")
    click.secho(f"Downloading {line_count} lines to file...", bold=True)

    ret = qry.download_results(filename)
    click.secho(f"Query results have been downloaded to {ret}", bold=True)


@click.command()
@click.argument('query_id', nargs=1)
@click.pass_context
@check_project
def cancel(ctx, query_id):
    """
    Cancel a running GOR query
    """
    svc = ctx.obj.service

    qry = svc.get_query(query_id)
    try:
        qry.cancel()
    except QueryError as ex:
        abort(ex)
    click.secho("Query has been cancelled.", fg='yellow', bold=True)


@click.command()
@click.argument('query_id', nargs=1)
@click.option('--raw', 'is_raw', is_flag=True, help='Dump raw json for further processing')
@click.pass_context
@check_project
def progress(ctx, query_id, is_raw):
    """
    View the progress of a running query
    """
    svc = ctx.obj.service

    qry = svc.get_query(query_id)
    if qry.status != "RUNNING":
        abort("Query is not RUNNING")

    if is_raw:
        click.echo(dumps(qry.progress))
        return

    fields = ["job_id", "status", "fingerprint", "bytes", "lines"]

    rows = []
    for job_id, job in qry.progress.items():
        rows.append(
            [
                job_id,
                job['job-status'],
                job.get('fingerprint'),
                job.get('queryByteCount'),
                job.get('queryLineCount'),
            ]
        )
    tbl = tabulate(rows, headers=fields)
    click.echo(tbl)


@click.command()
@click.argument('query_id', nargs=1)
@click.option('--raw', 'is_raw', is_flag=True, help='Dump raw json for further processing')
@click.pass_context
@check_project
def details(ctx, query_id, is_raw):
    """
    View runtime details for a query
    """
    svc = ctx.obj.service

    qry = svc.get_query(query_id)
    url = qry.links['details']
    resp = svc.session.get(url)
    details = resp.json()['details']
    if not details:
        abort("No details found for query")

    if is_raw:
        click.echo(dumps(details))
        return
    error = details.get("error")
    if error is not None:
        abort("Error from server: %s" % error)

    request_id = details.get('requestId')
    if request_id is None:
        abort("Could not understand response from server: %s" % dumps(details))

    print_tab("requestId", request_id)
    click.secho("Tasks", bold=True)
    for task_name, task in details.get("tasks", {}).items():
        print(task_name)
        for k in sorted(task.keys()):
            print_tab(f" {k}", task[k])
        print("")


@click.command("list")
@click.option('-u', '--user', 'user_name', help='User to filter for')
@click.option('-s', '--status', 'status', default=None, help='Filter status')
@click.option(
    '-n', '--num', default=20, help='Maximum number of queries to return', show_default=True
)
@click.option('--raw', 'is_raw', is_flag=True, help='Dump raw json for further processing')
@click.option(
    '--all', 'is_all', is_flag=True, help='Fetch all queries in all projects (admin only)'
)
@click.pass_context
@check_project
def list_queries(ctx, user_name, status, num, is_raw, is_all):
    """
    List the queries that have been run by this user in the current project.

    To specify another user you can use the --user parameter but you must
    have the admin role on the server to do so. It is not possible to fetch
    queries for all users.
    """
    svc = ctx.obj.service
    if is_all and user_name:
        abort("You cannot use the --all flag and the --user parameter together")
    try:
        queries = svc.get_queries(limit=num, user_name=user_name, all=is_all)
    except ServerError as e:
        abort(e)
    if is_raw:
        click.echo(dumps([q.raw for q in queries]))
        return
    rows = []
    for qry in queries:
        rows.append(
            [
                qry.query_id,
                qry.submit_date.strftime("%Y-%m-%d %H:%M"),
                qry.status,
                qry.project_name,
                qry.user_name,
            ]
        )
    fields = ["query_id", "submitted", "status", "project", "user_name"]
    tbl = tabulate(rows, headers=fields)
    click.echo(tbl)


@click.command("wakeup")
@click.option(
    '-j',
    '--jobtype',
    'job_type',
    default="default",
    help='Job type to include with the wakeup request',
)
@click.option('-u', '--user', 'user_name', help='Optional user to include for tracking purposes')
@click.pass_context
@check_project
def wakeup(ctx, job_type, user_name):
    """
    Wake the server up.
    """
    svc = ctx.obj.service
    success = svc.wakeup(job_type, user_name)
    click.secho(f"Success: {success}", bold=True)
