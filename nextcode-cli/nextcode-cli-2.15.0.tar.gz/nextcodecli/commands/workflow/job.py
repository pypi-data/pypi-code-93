#!/usr/bin/env python

import sys
import click
from click import echo, secho, pass_context, command, argument, option
import dateutil
from tabulate import tabulate
import datetime
import time
import subprocess
from urllib.parse import urlsplit, urljoin

from nextcode.services.workflow import INIT_STATUSES
from nextcode.exceptions import ServerError
from nextcode.config import get_default_profile

from nextcodecli.utils import dumps, print_tab, print_warn, print_error, output_pretty_json, abort
from nextcodecli.commands.workflow import status_to_color
from nextcodecli.workflow.cmdutils import get_processes_table, process_status_to_color


def check_for_broken_job(job):
    status = job.status
    # jobs can trigger scale-out in a cluster which might take 2-3 minutes to finalize
    max_diff = 300.0
    # jobs with dedicated storage_type can take 5-6 minutes to start so let's wait 10 minutes to be sure
    if job.details['launch_config']['storage_type'] == 'dedicated':
        max_diff = 600.0
    if status != 'PENDING':
        return False
    diff = (datetime.datetime.utcnow() - job.submit_date).total_seconds()
    if diff >= max_diff:
        secho(
            "\nJob has been in status '%s' for %.0f seconds. Something might be wrong."
            % (status, diff),
            fg='yellow',
        )
        cmd = ['nextcode', 'workflow', 'job', str(job.job_id), 'inspect']
        echo("\nExecuting %s..." % ' '.join(cmd))
        subprocess.call(cmd)
        return True
    return False


@command(
    cls=click.Group,
    invoke_without_command=True,
    help="View or manage individual jobs. Call with [job_id] or latest to "
    "view your latest submitted job",
)
@argument('job_id', required=True)
@pass_context
def job(ctx, job_id):
    if ctx.obj.job is None:
        ctx.obj.job = ctx.obj.service.find_job(job_id)
        ctx.obj.job_id = ctx.obj.job.job_id
    if ctx.invoked_subcommand is None:
        ctx.invoke(view)
        echo(job.get_help(ctx))


@job.command(help="Investigate a running job for problems")
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@pass_context
def inspect(ctx, is_raw):
    workflow_job = ctx.obj.job
    try:
        curr_status = workflow_job.inspect()
    except ServerError as e:
        abort(e)

    if is_raw:
        echo(dumps(curr_status))
        return
    print_tab('Job id', workflow_job.job_id)
    job_status = workflow_job.status or 'N/A'
    print_tab('Job status', job_status)
    print_tab('Status message', workflow_job.status_message)
    latest_event = curr_status['latest_event']
    event_too_old = False
    if latest_event:
        dt = dateutil.parser.parse(latest_event)
        dt = dt.replace(tzinfo=None)
        diff = datetime.datetime.utcnow() - dt
        diff_txt = " (%s ago)" % str(diff).split('.')[0]
        if diff < datetime.timedelta(minutes=5):
            col = 'green'
            event_too_old = False
        else:
            col = 'red'
            event_too_old = True
        diff_txt = click.style(diff_txt, fg=col)
        latest_event += diff_txt
    print_tab('Latest event', latest_event)
    print_tab('Executor Pod name', workflow_job.details.get('pod_name'))
    executor_pod = None
    for pod in curr_status['pods']:
        if pod['metadata']['labels']['app-name'] == 'nextflow-executor':
            executor_pod = pod
            break
    if not executor_pod:
        if job_status in ('PENDING', 'STARTED'):
            secho("Nextflow executor pod not Found. This job is not running!", fg='red')
    else:

        node_name = executor_pod['spec']['node_name']
        print_tab('Executor node name', node_name)
        secho("\nExecutor Pod State:", bold=True)

        if executor_pod['status']['container_statuses']:
            pod_state = executor_pod['status']['container_statuses'][0]['state']
            _keys = ['running', 'terminated', 'waiting']
            keys = []
            for k in _keys:
                if pod_state.get(k):
                    keys.append(k)
            output_pretty_json(pod_state, keys=keys)
        elif executor_pod['status']['conditions']:
            output_pretty_json(executor_pod['status'], ['conditions'])

        echo(
            "Hint: You can view latest logs from this pod with: 'nextcode workflow job {} logs pod'".format(
                workflow_job.job_id
            )
        )

    secho("\nProcess Pod State:", bold=True)
    table = []
    for pod in curr_status['pods']:
        if pod == executor_pod:
            continue
        container_status = None
        pod_status = pod['status']
        container_statuses = pod_status['container_statuses']
        if container_statuses:
            pod_state = container_statuses[0]['state']
        else:
            pod_state = {}

        for k, v in pod_state.items():
            if v:
                container_status = k
                if k.lower() == 'terminated':
                    container_status = "%s (%s at %s)" % (k, v['reason'], v['finished_at'])
        p = [
            pod['metadata']['name'],
            container_status,
            pod['spec']['node_name'],
            pod['metadata']['labels'].get('taskName', 'N/A'),
        ]
        table.append(p)
    if not table:
        echo("No process pods found")
    else:
        tbl = tabulate(table, headers=['name', 'state', 'node', 'process'])
        echo(tbl)
        echo(
            "\nHint: You can find the corresponding processes with: 'nextcode workflow job {} processes -o wide'".format(
                workflow_job.job_id
            )
        )

    if job_status == 'COMPLETED':
        secho("\nThis job appears to have completed successfully", fg='green', bold=True)
    elif job_status in ('STARTED', 'PENDING'):
        if not executor_pod:
            secho("\nThis job appears to be broken", fg='red', bold=True)
        else:
            try:
                if executor_pod['status']['container_statuses'][0]['state']['running']:
                    if event_too_old:
                        secho(
                            "\nJob appears to be running but it has been a long time since last heartbeat was received",
                            fg='red',
                            bold=True,
                        )
                    else:
                        secho("\nThis job appears to be running properly", fg='green', bold=True)
                else:
                    secho("\nThis job appears to be broken", fg='red', bold=True)
            except Exception:
                secho("\nThis job appears to be broken", fg='red', bold=True)
    else:
        secho("\nJob is not in running state (%s)" % job_status, bold=True)

    if executor_pod and job_status == 'PENDING':
        cmd = ['nextcode', 'workflow', 'job', str(workflow_job.job_id), 'logs', 'pod']
        echo("\nExecuting %s..." % ' '.join(cmd))
        subprocess.call(cmd)
        return


@job.command(help="Display estimated cost of the job")
@option('--recalculate', 'recalculate', is_flag=True, help="Recalculate the cost for the Job")
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@pass_context
def cost(ctx, recalculate, is_raw):
    workflow_job = ctx.obj.job
    cost_detail = workflow_job.cost(recalculate)
    if cost_detail:
        if is_raw:
            echo(dumps(cost_detail))
            return

        print_tab("cost", f"{cost_detail['cost']:.2f} {cost_detail['currency']}")
        cad = datetime.datetime.strptime(cost_detail["calculation_date"], '%Y-%m-%dT%H:%M:%S.%f')
        print_tab("calculated_at", cad.strftime('%Y-%m-%d %H:%M:%S'))
        print_tab("cost_model", cost_detail["cost_model"])
        print_tab("MODEL DETAILS", "")
        print_tab("lines_ok", cost_detail["details"]["lines"]["processed"])
        print_tab("lines_bad", cost_detail["details"]["lines"]["bad"])
        print_tab("lines_skipped", cost_detail["details"]["lines"]["skipped"])
        print_tab("full_price", cost_detail["details"]["price"]["full_price"])
        print_tab("total_price", cost_detail["details"]["price"]["total_price"])

    else:
        print_error(f"Could not get cost for job {workflow_job.job_id}")


@job.command(help="View information about the job")
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@pass_context
def view(ctx, is_raw):
    workflow_job = ctx.obj.job
    if is_raw:
        echo(dumps(workflow_job.job))
        return

    print_tab('job_id', workflow_job.job_id)
    pipeline_name = workflow_job.pipeline_name
    if not pipeline_name:
        pipeline_name = "(custom)"
    print_tab('pipeline_name', pipeline_name)
    print_tab('project', workflow_job.project_name)
    if workflow_job.description:
        print_tab('description', workflow_job.description)
    submit_date = workflow_job.submit_date
    print_tab('submitted', submit_date.strftime('%Y-%m-%d %H:%M:%S'))
    complete_date = workflow_job.complete_date or datetime.datetime.utcnow()
    if workflow_job.complete_date:
        print_tab('completed', complete_date.strftime('%Y-%m-%d %H:%M:%S'))
    print_tab('duration', str(complete_date - submit_date).split('.')[0])
    cost = "<Cost hasn't been calculated for this job>"
    if workflow_job.cost_amount:
        cost = f"{workflow_job.cost_amount:.2f} {workflow_job.cost_currency}"
    print_tab('cost', cost)
    print_tab('context', getattr(workflow_job, 'context', ''))

    print_tab('nextflow ID', workflow_job.run_id)
    print_tab(
        'nextflow Pod',
        "%s (%s)"
        % (workflow_job.details.get('pod_name'), workflow_job.details.get('pod_namespace')),
    )
    print_tab('work dir', workflow_job.work_dir)
    print_tab('script_name', workflow_job.script_name)
    print_tab('revision', (workflow_job.revision or '(latest)'))
    print_tab('user', workflow_job.user_name)
    status = workflow_job.status or 'N/A'
    col = status_to_color.get(status, '')
    st = str(status)
    if workflow_job.status_message:
        st += " - {}".format(workflow_job.status_message)
    st = click.style(st, fg=col, bold=True)
    print_tab('status', st)

    txt = ", ".join(
        [
            "{}: {}".format(k.capitalize(), v)
            for k, v in workflow_job.details.get('process_stats', {}).items()
        ]
    )
    txt = "{}".format(txt)
    print_tab('processes', txt)

    if status in ('STARTED', 'ERROR'):
        limit = 50
        processes = workflow_job.processes(limit=limit)
        echo("Running Processes:")
        echo(get_processes_table(processes))
        if len(processes) == limit:
            secho(
                "Note: Only showing the latest {} non-completed processes".format(limit), bold=True
            )
        for p in processes:
            if p['status'] == 'FAILED':
                cmd = "nextcode workflow job %s process %s view|pod|logs" % (
                    workflow_job.job_id,
                    p['process_id'],
                )
                echo("Inspect failed process with: %s" % click.style(cmd, bold=True))

    check_for_broken_job(workflow_job)


@job.command(help="Get nextflow events for this job")
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@option('-e', '--event', 'event_name', help='Filter events on name')
@option('-p', '--process', 'process_name', help='Filter events on process')
@option('-n', '--num', default=50, help='Maximum number of events to return')
@pass_context
def events(ctx, is_raw, event_name, process_name, num):
    events = ctx.obj.job.events(num)
    if event_name:
        events = [e for e in events if e['event'].startswith(event_name)]
    if process_name:
        events = [
            e
            for e in events
            if e and (e.get('trace', {}) or {}).get('name', '').startswith(process_name)
        ]

    if is_raw:
        print(dumps(events))
        return

    echo("Events for job {}:".format(ctx.obj.job.job_id))
    headers = ['first_event_date', 'last_event_date', 'event', 'process', 'status']
    table = []
    for event in events:
        dt = dateutil.parser.parse(event['event_date'])
        try:
            last_dt = dateutil.parser.parse(event['last_event_date'])
        except Exception:
            last_dt = '-'
        row = [
            dt,
            last_dt,
            event['event'],
            (event.get('trace') or {}).get('name'),
            ((event.get('trace') or {}).get('status') or ""),
        ]
        if (event['num_events'] or 1) > 1:
            row[-1] += ' ( x%s )' % event['num_events']
        table.append(row)

    tbl = tabulate(table, headers=headers)
    echo(tbl)


@job.command(help="Retry a failed job.")
@pass_context
def resume(ctx):
    workflow_job = ctx.obj.job
    job_id = workflow_job.job_id
    echo("Resuming failed job %s..." % job_id)
    try:
        workflow_job.resume()
    except ServerError as e:
        abort(e)
    cmd = ['nextcode', 'workflow', 'job', str(job_id), 'watch']
    echo("Executing %s..." % ' '.join(cmd))
    subprocess.call(cmd)


@job.command(help="View parameters for this job.")
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@pass_context
def params(ctx, is_raw):
    workflow_job = ctx.obj.job
    params = ctx.obj.session.get(workflow_job.links['params']).json()
    if is_raw:
        echo(dumps(params))
        return
    echo("Parameters for job {}:".format(ctx.obj.job.job_id))
    for k, v in params.items():
        vv = v
        if isinstance(vv, str) and len(vv) > 100:
            vv = vv[:100] + "..."
        print_tab(k, vv)


@job.command(help="View logs associated with a job. Choose the log group to stream.")
@argument('log_group', default='')
@option('--filter', 'log_filter', help='Filter logs on text')
@pass_context
def logs(ctx, log_group, log_filter):
    workflow_job = ctx.obj.job
    if not log_group:
        log_groups = workflow_job.log_groups()
        echo(
            "The following log groups are available for job %s:\n  %s"
            % (workflow_job.job_id, "\n  ".join(log_groups.keys()))
        )
        sys.exit(1)
    try:
        logs = workflow_job.logs(log_group, log_filter)
    except Exception as ex:
        abort(ex)
    if not logs:
        print_warn("No logs found")
        return

    echo(logs)
    echo("\n%s loglines found" % (logs.count('\n')))


@job.command(help="Information about Nextflow processes for this job")
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@option('-p', '--process', 'process_name', help='Only show a particular process')
@option('-n', '--num', 'limit', default=100, help='Number of processes to show')
@option('-a', '--all', 'is_all', is_flag=True, default=False, help='Also show completed processes')
@option('-s', '--status', 'status', default=None, help='Filter process status')
@option(
    '-o',
    '--output',
    type=click.Choice(['normal', 'wide', 'json']),
    default='normal',
    help='Format output',
)
@pass_context
def processes(ctx, is_raw, process_name, output, limit, is_all, status):
    workflow_job = ctx.obj.job
    processes = workflow_job.processes(limit=limit, is_all=is_all, status=status)
    if process_name:
        processes = [p for p in processes if p['name'].startswith(process_name)]
    is_raw = is_raw or (output == 'json')
    if is_raw:
        echo(dumps(processes))
        return

    txt = click.style(
        ", ".join(
            [
                "{}: {}".format(k.capitalize(), v)
                for k, v in workflow_job.details.get('process_stats', {}).items()
            ]
        ),
        bold=True,
    )
    txt = "Processes by status for job {}: {}".format(workflow_job.job_id, txt)
    echo(txt)

    if len(processes) == 0 and not is_all:
        secho(
            "No running processes found. Use the '--all' flag to show completed processes",
            bold=True,
        )
        return
    if not is_all:
        echo("\nNon-completed processes:")
    else:
        echo("\nProcesses:")
    echo(get_processes_table(processes, is_wide=(output == 'wide')))
    if len(processes) == limit:
        msg = "Note: Only showing the latest {} non-completed processes".format(limit)
        if is_all or status:
            msg = "Note: Only showing the latest {} processes".format(limit)
        secho(msg, bold=True)


@job.command(
    cls=click.Group,
    invoke_without_command=True,
    help="Information about a specific nextflow process",
)
@argument('process_id', required=True)
@pass_context
def process(ctx, process_id):
    processes = ctx.obj.job.processes(process_id)
    if not processes:
        abort("Process %s not found in job %s" % (process_id, ctx.obj.job.job_id))
    ctx.obj.process = processes[0]

    if ctx.invoked_subcommand is None:
        ctx.invoke(view)
        echo(job.get_help(ctx))


@process.command('view', help="View nextflow process details")
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@pass_context
def process_view(ctx, is_raw):
    process = ctx.obj.process
    if is_raw:
        echo(dumps(process))
        return

    try:
        node_name = process['details']['node']['metadata']['name']
    except Exception:
        node_name = 'N/A'
    print_tab('job_id', process['job_id'])
    print_tab('process_id', process['process_id'])
    print_tab('name', process['name'])
    print_tab('pod', process['native_id'])
    print_tab('node', node_name)
    print_tab('process_hash', process['process_hash'])
    status = click.style(
        process['status'], fg=process_status_to_color.get(process['status'], 'white')
    )
    print_tab('status', status)
    print_tab('submit_date', process['submit_date'])
    print_tab('complete_date', process['complete_date'])
    print_tab('status_date', process['status_date'])
    print_tab('exit_code', process['exit_code'])
    print_tab('container', process['container'])


@process.command('logs', help="View pod logs for nextflow process (if the pod is still available)")
@pass_context
def process_logs(ctx):
    process = ctx.obj.process
    try:
        logs = ctx.obj.session.get(process['links']['logs'])
    except ServerError as e:
        abort(e)

    print("Logs from pod '%s':" % process['native_id'])
    print(logs.text)


@process.command('pod', help="View saved pod information for nextflow process from the process run")
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@pass_context
def process_pod(ctx, is_raw):
    process = ctx.obj.process
    if not process['details']:
        abort(
            "Process has no associated information. This could mean that the process has not started"
        )
    pod = (process['details'] or {}).get('pod', {})
    if is_raw:
        echo(dumps(pod))
        return

    echo(
        "Showing pod information for pod {} in job {} from when the process was run...".format(
            process["process_id"], ctx.obj.job.job_id
        )
    )
    keys = [
        'name',
        'namespace',
        'creation_timestamp',
        'labels',
        'image',
        'state',
        'resources.limits',
    ]
    output_pretty_json(pod, keys=keys)


@process.command(
    'node', help="View saved node information for nextflow process from the process run"
)
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@pass_context
def process_node(ctx, is_raw):
    process = ctx.obj.process
    node = process['details'].get('node', {})
    if is_raw:
        echo(dumps(node))
        return
    echo(
        "Showing node information for pod {} in job {} from when the process was run...".format(
            process["process_id"], ctx.obj.job.job_id
        )
    )
    keys = ['name', 'creation_timestamp', 'labels', 'capacity', 'node_info']
    output_pretty_json(node, keys=keys)


@process.command('events', help="Get nextflow events for this process")
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@pass_context
def process_events(ctx, is_raw):
    process = ctx.obj.process
    events = ctx.obj.session.get(process['links']['events']).json()['events']

    if is_raw:
        print(dumps(events))
        return

    headers = ['first_event_date', 'last_event_date', 'event', 'process', 'status']
    table = []
    for event in events:
        dt = dateutil.parser.parse(event['event_date'])
        try:
            last_dt = dateutil.parser.parse(event['last_event_date'])
        except Exception:
            last_dt = '-'
        row = [
            dt,
            last_dt,
            event['event'],
            (event.get('trace') or {}).get('name'),
            ((event.get('trace') or {}).get('status') or ""),
        ]
        if (event['num_events'] or 1) > 1:
            row[-1] += ' ( x%s )' % event['num_events']
        table.append(row)

    tbl = tabulate(table, headers=headers)
    echo(tbl)


@job.command(help="Cancel a running job")
@pass_context
def cancel(ctx):
    workflow_job = ctx.obj.job
    try:
        status_message = workflow_job.cancel()
    except ServerError as e:
        abort(e)
    secho("Job has been cancelled. Response was: %s" % status_message, bold=True)


@job.command(help="Monitor a running job.")
@option(
    '-o', '--output', type=click.Choice(['normal', 'wide']), default='normal', help='Format output'
)
@pass_context
def watch(ctx, output):
    workflow_job = ctx.obj.job
    try:

        status = workflow_job.status
        if not workflow_job.running:
            print_warn("Job is not in running state. Nothing to watch.")
            ctx.invoke(view)
            return

        last_status = None
        while status in INIT_STATUSES:

            status = workflow_job.status
            if status != last_status:
                sys.stdout.write("\nJob status: %s." % status)
                sys.stdout.flush()
                last_status = status

            while workflow_job.status == last_status and last_status in INIT_STATUSES:
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(5.0)
                workflow_job.refresh()
                if check_for_broken_job(workflow_job):
                    return

        if workflow_job.running:
            import curses

            stdscr = curses.initscr()
            curses.noecho()
            try:
                stdscr.clear()
                stdscr.addstr("\nJob %s is running." % workflow_job.job_id)
                n = 0
                while workflow_job.running:
                    stdscr.addstr(".")
                    time.sleep(1.0)
                    workflow_job.refresh()
                    processes_resource = workflow_job.processes()

                    stdscr.clear()
                    stdscr.addstr("\nJob %s is running." % workflow_job.job_id)
                    for i in range(n):
                        stdscr.addstr(".")
                    n += 1
                    if n > 3:
                        n = 0
                    stdscr.addstr("\n\n")
                    if not processes_resource:
                        stdscr.addstr("No processes running")
                    else:
                        steps_txt = get_processes_table(
                            processes_resource, is_color=False, is_wide=(output == 'wide')
                        )
                        try:
                            stdscr.addstr(steps_txt)
                        except Exception:
                            pass
                    stdscr.refresh()
                time.sleep(1.0)
            finally:
                curses.endwin()
            col = status_to_color.get(workflow_job.status, '')
            echo(
                "\nJob has completed in %s with status: %s"
                % (
                    str(workflow_job.duration).split('.')[0],
                    click.style(workflow_job.status, fg=col, bold=True),
                )
            )
            cmd = ['nextcode', 'workflow', 'job', str(workflow_job.job_id), 'view']
            echo("Executing %s..." % ' '.join(cmd))
            subprocess.call(cmd)

        else:
            print_error("\nUnexpected job status: %s" % workflow_job.status)
            echo("\nView job details with: 'nextcode workflow job %s view'" % workflow_job.job_id)
    except KeyboardInterrupt:
        echo(
            "\nStopped watching job. To continue run: "
            "nextcode workflow job %s watch" % workflow_job.job_id
        )
        return


@job.command()
@argument('link_type', required=True, type=click.Choice(['kibana', 'grafana']))
@pass_context
def link(ctx, link_type):
    """
    Helper that produces a link to external monitoring tools with filters
    preconfigured for this job
    """

    workflow_job = ctx.obj.job

    start_date = workflow_job.submit_date
    end_date = datetime.datetime.utcnow()
    if workflow_job.complete_date:
        end_date = workflow_job.complete_date
    end_date += datetime.timedelta(minutes=5)
    job_id = workflow_job.job['job_id']
    profile_name = get_default_profile()
    if link_type == 'kibana':
        kibana_url = ctx.obj.session.url_from_endpoint("kibana")

        start_date = start_date.isoformat()
        end_date = end_date.isoformat()
        link = (
            "{kibana_url}/discover?_g=(refreshInterval:(pause:!t,value:0),"
            "time:(from:'{start_date}',mode:absolute,to:'{end_date}'))"
            "&_a=(columns:!(kubernetes.labels.taskName,message),interval:auto,"
            "query:(language:lucene,query:'kubernetes.labels.job-id:{job_id}%20%26%26%20kubernetes.labels.started-by:workflow-service'),"
            "sort:!('@timestamp',desc))".format(
                kibana_url=kibana_url,
                start_date=start_date,
                end_date=end_date,
                job_id=job_id,
            )
        )
        echo(link)
        click.launch(link)
    elif link_type == 'grafana':
        parts = urlsplit(ctx.obj.service.base_url)
        grafana_url = urljoin('%s://%s' % (parts.scheme, parts.netloc), 'admin/grafana')

        from_timestamp = int(time.mktime(start_date.timetuple()) * 1000)
        to_timestamp = int(time.mktime(end_date.timetuple()) * 1000)
        link = (
            "{grafana_url}/d/KBmVXHXnas/workflow-service-job-details?orgId=1&"
            "from={from_timestamp}&to={to_timestamp}&"
            "var-job_id={job_id}&var-step=All&refresh=5s".format(
                grafana_url=grafana_url,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
                job_id=job_id,
            )
        )
        echo(link)
        click.launch(link)
