#!/usr/bin/env python

import sys
import click
import time
import dateutil
import datetime
from tabulate import tabulate
import requests

from nextcodecli.pipelines.jobs import find_job, download_output_file
from nextcodecli.pipelines.cmdutils import get_steps_table, print_filelist, status_to_color
from nextcodecli.utils import dumps, abort, print_tab, print_warn, print_error

INIT_STATUSES = ('QUEUED', 'INITIALIZING', 'LAUNCHING')


def has_failed_steps(job_resource):
    for step in job_resource.get('steps', []):
        if step['status'] == 'FAILED':
            return True
    return False


@click.command(
    cls=click.Group,
    invoke_without_command=True,
    help="View or manage individual jobs. Call with [job_id] or latest to "
    "view your latest submitted job",
)
@click.argument('job_id', required=True)
@click.pass_context
def job(ctx, job_id):
    if job_id != 'latest':
        try:
            job_id = int(job_id)
        except ValueError:
            abort("job_id should be a number or 'latest', not '%s'" % job_id)
    job_resource = find_job(ctx.obj.service, job_id)
    if not job_resource:
        abort("Job not found")

    ctx.obj.job = job_resource
    ctx.obj.job_id = job_id
    if ctx.invoked_subcommand is None:
        ctx.invoke(view)
        click.echo(job.get_help(ctx))


@job.command(help="View information about the job")
@click.option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@click.pass_context
def view(ctx, is_raw):
    job_resource = ctx.obj.job
    session = ctx.obj.session
    if is_raw:
        click.echo(dumps(job_resource))
        return
    else:
        status = job_resource['status']
        for k in (
            'job_id',
            'date_submitted',
            'date_completed',
            'pipeline_name',
            'sample_name',
            'description',
        ):
            print_tab(k, job_resource[k])

        mr = ""
        if job_resource['details'].get('submitter'):
            if job_resource['details']['submitter']['user_name'] != job_resource['user_name']:
                mr = " (submitted by %s)" % job_resource['details']['submitter']['user_name']
        print_tab('user_name', job_resource['user_name'] + mr)
        instance_id = '-'
        if len(job_resource['instances']) > 0:
            instance = job_resource['instances'][0]
            instance_id = instance['instance_id']
            if instance['is_spot']:
                instance_id += " (spot)"
        print_tab('instance_id', instance_id)
        print_tab('region', job_resource['region'])
        print_tab('output location', job_resource['output_config']['output_path'])
        details = job_resource['details']
        if details.get('build_source', 'ami') != 'ami':
            print_tab(
                'build source',
                "%s | %s" % (details.get('build_source'), details.get('build_context')),
            )
        if job_resource['details'].get('old_job_id'):
            print_tab('Rerun of Job', details.get('old_job_id'))

        col = status_to_color.get(status, '')
        if details.get('new_job_id'):
            status += " (rerun in job %s)" % job_resource['details'].get('new_job_id')

        print_tab('status', click.style(str(status), fg=col, bold=True))
        if status != 'FINISHED':
            click.echo('')
            click.echo(get_steps_table(job_resource))
            if has_failed_steps(job_resource):
                click.secho(
                    "\nJob has failed steps. You can analyze this with the 'steps' " "subcommand",
                    fg='red',
                )
        else:
            duration = dateutil.parser.parse(
                job_resource['date_completed']
            ) - dateutil.parser.parse(job_resource['date_submitted'])
            duration = str(duration).split('.')[0]
            print_tab('duration', duration)
            num_uncompleted = len(
                [s for s in job_resource.get('steps', []) if s['status'] != 'COMPLETED']
            )
            if num_uncompleted:
                print_warn(
                    "\nJob has %s/%s uncompleted steps. This might indicate that "
                    "there was a problem with the job."
                    % (num_uncompleted, len(job_resource['steps']))
                )
                click.echo("Please investigate using the 'steps' and 'logs' subcommands")
        messages = job_resource.get('messages')
        if messages:
            click.echo("\nMessages:")
            table = []
            for message in messages:
                table.append((message['event'].get('step_name'), message['event'].get('text')))
            tbl = tabulate(table, headers=['step name', 'message'])
            click.echo(tbl)

        click.echo("\nInput files:")
        print_filelist(job_resource.get('input'))
        if job_resource.get('output'):
            click.echo("\nOutput files:")
            print_filelist(job_resource.get('output'))

    click.echo('')
    job_id = job_resource['job_id']
    if job_resource['status'] == 'FAILED' and not has_failed_steps(job_resource):
        click.secho(
            "\nJob failed but no steps failed. "
            "Please analyze logs with 'nextcode pipelines job %s logs userdata'" % job_id,
            fg='red',
        )
        click.echo(
            "Hint: You might find the cause with one of these commands\n"
            "nextcode pipelines job {job_id} logs userdata | grep -C 5 \"Caused by\"\n"
            "nextcode pipelines job {job_id} logs userdata | grep -C 5 \"ERROR\"\n".format(
                job_id=job_id
            )
        )

    if job_resource['status'] not in INIT_STATUSES:
        click.echo("\nAvailable logs (via logs subcommand argument):")
        url = session.links(job_resource)['logs']
        resp = session.get(url)
        resp.raise_for_status()
        log_urls = resp.json()
        for url in session.links(log_urls):
            click.echo(url)
        click.echo('')
    elif job_resource['status'] == 'QUEUED':
        print_warn(
            "Job is queued. "
            "You can force-start it with 'nextcode pipelines job %s launch'" % job_id
        )
        seconds_queued = (
            datetime.datetime.utcnow() - dateutil.parser.parse(job_resource['submit_date'])
        ).total_seconds()
        if seconds_queued > 120:
            click.secho(
                "Job has been queued for %.0f minutes. You might be able to see why with "
                "'nextcode pipelines job %s events'\n" % (seconds_queued / 60, job_id),
                bold=True,
            )


@job.command(help="View job messages")
@click.option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@click.pass_context
def messages(ctx, is_raw):
    job_resource = ctx.obj.job
    session = ctx.obj.session
    messages = job_resource.get('messages') or []
    if is_raw:
        click.echo(dumps(messages))
        return
    if not messages:
        print_warn("No messages found")
        return
    click.echo("Messages from job %s:" % job_resource['job_id'])
    table = []
    for message in messages:
        dt = dateutil.parser.parse(message['date_time'])
        table.append(
            (
                dt.strftime("%H:%M:%S"),
                message['event'].get('step_name'),
                message['event'].get('text'),
            )
        )
    tbl = tabulate(table, headers=['timestamp', 'step name', 'message'])
    click.echo(tbl + '\n')


@job.command(
    help="View the submission manifest for the job. Note that this is not the same file as a local "
    "job.json file that was used to submit the job via the cli."
)
@click.option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@click.option(
    '--generate', is_flag=True, help='Attempt to generate a job.json file that the CLI can use'
)
@click.pass_context
def manifest(ctx, is_raw, generate):
    job_resource = ctx.obj.job
    details = job_resource['details']
    if generate:
        keys_to_remove = ['submitter', 'files', 'sample_name']
        details["samples"] = [{"files": details["files"], "name": details["sample_name"]}]
        details["iam_profiles"] = {"download": "", "upload": ""}
        for k in keys_to_remove:
            if k in details:
                del details[k]
        for k, v in details.copy().items():
            if v is None:
                del details[k]
        click.echo(dumps(details))
    elif is_raw:
        click.echo(dumps(details))
    else:
        for k in sorted(details):
            v = details[k]
            if isinstance(v, dict) or isinstance(v, list):
                v = dumps(v)
                for l in v.split('\n'):
                    print_tab(k, l)
                    if k:
                        k = ''

            else:
                print_tab(k, v)


@job.command(help="Cancel a running job.")
@click.pass_context
def cancel(ctx):
    session = ctx.obj.session
    job_resource = ctx.obj.job
    job_id = job_resource['job_id']
    jobs = session.get(
        session.url_from_endpoint('jobs'), json={'job_id': job_id, 'field': []}
    ).json()['jobs']
    if not jobs:
        abort("Job '%s' not found" % job_id)
    job_url = session.links(jobs[0])['self']
    resp = session.delete(job_url)
    # pylint: disable=E1101
    if resp.status_code == requests.codes.ok:
        print_warn("Job %s has been cancelled" % job_id)
        if resp.json().get('error'):
            print_error(resp.json()['error'])
    elif resp.status_code == requests.codes.bad_request:
        print_warn("Error cancelling job %s" % job_id)
        print_error(resp.json()['error']['description'])
        return
    resp.raise_for_status()


@job.command(help="Force a queued job to launch.")
@click.option('-s', '--spot', 'is_spot', is_flag=True, help='Force a spot instance')
@click.option('-d', '--dedicated', 'is_dedicated', is_flag=True, help='Force a dedicated instance')
@click.pass_context
def launch(ctx, is_spot, is_dedicated):
    session = ctx.obj.session
    job_resource = ctx.obj.job
    if job_resource['status'] != 'QUEUED':
        abort("Job is in state '%s' which is not 'QUEUED'" % job_resource['status'])
    if len(job_resource['instances']) > 0:
        abort("Job already has worker instances assigned")
    instances_url = job_resource['links']['instances']
    data = {}
    if is_spot:
        data = {'spot': True}
    elif is_dedicated:
        data = {'dedicated': True}
    resp = session.post(instances_url, json=data)
    if resp.status_code == 404:
        print_error(
            "Could not launch instance. This probably means that there are too many"
            " jobs running. If the problem persists please seek help."
        )
        print_error("Error from server: %s" % resp.json()['error']['description'])
        return

    resp.raise_for_status()
    print_warn("Job worker is launching...")


@job.command(help="View input and output files with file size information")
@click.option('-r', '--raw', 'is_raw', is_flag=True, help='Dump raw json response')
@click.pass_context
def files(ctx, is_raw):
    session = ctx.obj.session
    job_resource = ctx.obj.job
    files = session.get(session.links(job_resource)['files']).json()

    if is_raw:
        print(dumps(files))
    else:
        click.echo("\nInput files:")
        print_filelist(files.get('input'), details=True)
        if files.get('output'):
            click.echo("\nOutput files:")
            print_filelist(files.get('output'), details=True)


@job.command(help="Try to find error logs generated by the job")
@click.pass_context
def errors(ctx):
    session = ctx.obj.session
    job_resource = ctx.obj.job
    log_urls = session.links(session.get(session.links(job_resource)['logs']).json())
    print_warn("Searching for errors...")
    log_group = 'pipelines_userdata'
    filters_to_try = ['Command error', 'Caused by', 'ERROR']
    logs = ""
    for log_filter in filters_to_try:
        url = log_urls[log_group]
        if log_filter:
            url += '?filter=%s' % log_filter
        resp = session.get(url)
        if resp.status_code != 200:
            print_error(resp.json()['error']['description'])
            return
        logs = resp.text
        if logs:
            break
    if logs:
        click.echo(logs)
        click.echo("\n%s loglines found" % (logs.count('\n')))
    else:
        print_error(
            "No identifiable error logs found. You can keep searching with "
            "'nextcode pipelines job %s logs userdata'" % job_resource['job_id']
        )


@job.command(help="View logs associated with a job. Choose the log group to stream.")
@click.argument('log_group', default='')
@click.option('--filter', 'log_filter', help='Filter logs on text')
@click.pass_context
def logs(ctx, log_group, log_filter):
    session = ctx.obj.session
    job_resource = ctx.obj.job

    log_urls = session.links(session.get(session.links(job_resource)['logs']).json())
    if log_group.lower().startswith('error'):
        print_warn("Searching for errors...")
        log_group = 'pipelines_userdata'
        log_filter = 'Command error'
    found_log_group = None
    for url in log_urls:
        if log_group and str(log_group) in url:
            found_log_group = url
    if not found_log_group:
        abort(
            "Log Group '%s' is not available."
            " Choose from:\n  %s" % (log_group, "\n  ".join(log_urls.keys()))
        )
    click.echo("Viewing log group '%s'" % found_log_group)
    url = log_urls[found_log_group]
    if log_filter:
        url += '?filter=%s' % log_filter
    resp = session.get(url)
    if resp.status_code != 200:
        abort(resp.json()['error']['description'])
    logs = resp.text
    if not logs:
        print_warn("No logs found")
        return

    click.echo(logs)
    click.echo("\n%s loglines found" % (logs.count('\n')))


@job.command(help="View events triggered by the job.")
@click.option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@click.option('--event', '-e', 'event_name', help='Filter by event name')
@click.option('--step', '-s', 'step_name', help='Filter by step name')
@click.pass_context
def events(ctx, is_raw, event_name=None, step_name=None):
    job_resource = ctx.obj.job
    session = ctx.obj.session
    event_url = session.links(job_resource)['events']
    url = event_url
    if event_name or step_name:
        url = event_url + '?'
        if event_name:
            url = url + 'event_name=%s&' % event_name
        if step_name:
            url = url + 'step_name=%s' % step_name

    resp = session.get(url)
    events = resp.json()
    # for backwards compatibility
    if event_name:
        events = [e for e in events if e.get('event_name') == event_name]
    if step_name:
        events = [e for e in events if e['event'].get('step_name') == step_name]
    if is_raw:
        click.echo(dumps(events))
        return
    lst = []
    for event in events:
        dt = dateutil.parser.parse(event['date_time'])
        step_name = event['event'].get('step_name')
        details = event['event'].get('text')
        lst.append([dt.strftime("%H:%M:%S"), event['event_name'], step_name, details])
    click.echo(tabulate(lst, headers=['date', 'event', 'step', 'details']))


@job.command(help="Download all output files into a local folder.")
@click.argument('folder', required=True)
@click.pass_context
def download(ctx, folder):
    job_resource = ctx.obj.job
    session = ctx.obj.session
    files = session.get(session.links(job_resource)['files']).json()
    output_files = files.get('output') or []
    if not output_files:
        click.secho("No output files found", fg="yellow")
    for output in output_files:
        url = output['url']
        file_size = output['file_size'] / 1024 / 1024
        if not url:
            print_warn(
                "Cannot download file '%s' from '%s'. No signed url returned from server"
                % (output['file_name'], output['remote_path'])
            )
        elif file_size < 0:
            print_warn(
                "Cannot download file '%s' from '%s'. File not found"
                % (output['file_name'], output['remote_path'])
            )
        else:
            if file_size <= 0:
                file_size_txt = "<1MB"
            else:
                file_size_txt = "%.0f MB" % file_size
            click.echo(
                "Downloading file '%s' from '%s' (%s)..."
                % (output['file_name'], output['remote_path'], file_size_txt)
            )
            download_output_file(folder, url)


@job.command(help="View job steps and status.")
@click.option('--raw', 'is_raw', is_flag=True, help='Dump raw json response from endpoint')
@click.pass_context
def steps(ctx, is_raw):
    job_resource = ctx.obj.job
    if is_raw:
        click.echo(dumps(job_resource['steps']))
        return

    click.echo(get_steps_table(job_resource))
    if not has_failed_steps(job_resource):
        return

    for step in job_resource['steps']:
        if step['status'] == 'FAILED':
            click.secho(
                "\nStep '%s' (%s) failed with exit code %s. Final loglines from stderr:"
                % (step['step_name'], step['step_identifier'], step['details']['exit_code']),
                fg='red',
            )
            for l in step['details']['error'].split('\n'):
                if l.strip():
                    click.secho(l.rstrip(), fg='red')
    click.echo("\nYou can view additional logs with the 'logs' subcommand.")


@job.command(help="Monitor a running job.")
@click.pass_context
def watch(ctx):
    # count = 100
    # items = range(count)
    # def filter(items):
    #     for item in items:
    #         if random.random() > 0.3:
    #             yield item
    # with click.progressbar(filter(items),
    #                       show_eta=False,
    #                       label='Initializing Worker Instance',
    #                       fill_char=click.style('#', fg='magenta')) as bar:
    #     while 1:
    #         time.sleep(0.02)
    #         bar.update(1)
    job_resource = ctx.obj.job
    session = ctx.obj.session
    job_url = session.links(job_resource)['self']

    try:

        status = job_resource['status']
        if status not in INIT_STATUSES + ('RUNNING',):
            print_warn("Job is not in running state. Nothing to watch.")
            ctx.invoke(view)
            return

        last_status = None
        while status in INIT_STATUSES:
            status = job_resource['status']
            if status != last_status:
                sys.stdout.write("\nJob status: %s." % status)
                sys.stdout.flush()
                last_status = status

            while job_resource['status'] == last_status and last_status in INIT_STATUSES:
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(5.0)
                job_resource = session.get(job_url).json()

        if status == 'RUNNING':
            import curses

            stdscr = curses.initscr()
            curses.noecho()
            try:
                stdscr.clear()
                stdscr.addstr("\nJob is running.")
                while job_resource['status'] == 'RUNNING':
                    stdscr.addstr(".")
                    time.sleep(1.0)
                    job_resource = session.get(job_url).json()
                    stdscr.clear()
                    steps_txt = get_steps_table(job_resource, color=False)
                    try:
                        stdscr.addstr(steps_txt)
                    except Exception:
                        pass
                    stdscr.refresh()
                time.sleep(1.0)
            finally:
                curses.endwin()
            click.echo("\nJob has completed with status: %s" % job_resource['status'])
            click.echo(
                "View with: %s"
                % (
                    click.style(
                        "nextcode pipelines job %s view" % job_resource['job_id'], bold=True
                    )
                )
            )
        else:
            print_error("\nUnexpected job status: %s" % job_resource['status'])
    except KeyboardInterrupt:
        click.echo(
            "\nStopped watching job. To continue run: "
            "nextcode pipelines job %s watch" % job_resource['job_id']
        )
        return


@job.command(help="Duplicate a job and rerun")
@click.pass_context
def duplicate(ctx):
    job_resource = ctx.obj.job
    session = ctx.obj.session
    job_url = session.links(job_resource)['self']
    resp = session.patch(job_url, json={'action': 'duplicate'})
    resp.raise_for_status()
    data = resp.json()
    new_job_id = data['details']['new_job_id']
    click.echo(data['message'])
    click.echo("Please view the new job with nextcode pipelines job %s view" % new_job_id)


from nextcodecli.commands.pipelines.instance import instance

job.add_command(instance)
