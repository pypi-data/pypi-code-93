from tabulate import tabulate
import dateutil
import datetime
import time
import click


process_status_to_color = {
    'SUBMITTED': 'yellow',
    'STARTED': 'yellow',
    'ABORTED': 'white',
    'FAILED': 'red',
    'COMPLETED': 'green',
}


def get_limits_string(process):
    try:
        limits = process['details']['pod']['resources']['limits']
    except (IndexError, KeyError, TypeError):
        limits = {}
    if limits:
        return ", ".join(["%s: %s" % (k, v) for k, v in limits.items()])
    else:
        return ""


def get_processes_table(processes, is_color=True, is_wide=False):
    headers = ['id', 'name', 'container', 'status', 'submit_date', 'duration']
    if is_wide:
        headers.extend(['start_date', 'complete_date', 'runtime', 'limits', 'pod', 'node'])
    table = []
    for process in processes:
        submit_date = 'N/A'
        duration = process['duration']
        runtime = 'N/A'
        if process['submit_date']:
            dt = dateutil.parser.parse(process['submit_date'])
            submit_date = dt.strftime('%Y-%m-%d %H:%M:%S')
            if not duration and process['status'] == 'STARTED':
                duration = (datetime.datetime.utcnow() - dt).total_seconds() * 1000
        start_date = None
        start_date_string = 'N/A'
        complete_date = None
        complete_date_string = 'N/A'
        exit_code = ''
        if process['start_date']:
            start_date = dateutil.parser.parse(process['start_date'])
            start_date_string = start_date.strftime('%Y-%m-%d %H:%M:%S')

        if process['complete_date'] and start_date:
            complete_date = dateutil.parser.parse(process['complete_date'])
            complete_date_string = complete_date.strftime('%Y-%m-%d %H:%M:%S')
            exit_code = process['exit_code']
            runtime = complete_date - start_date
            runtime = str(runtime).split('.')[0]
        elif start_date:
            runtime = (datetime.datetime.utcnow() - start_date).total_seconds() * 1000
            runtime = datetime.timedelta(seconds=(runtime // 1000))
            runtime = str(runtime).split('.')[0]

        if exit_code:
            exit_code = click.style(' (exit code %s)' % exit_code, fg='red')
        else:
            exit_code = ''
        if duration:
            duration = datetime.timedelta(seconds=(duration // 1000))
            duration = str(duration).split('.')[0]
        node_name = 'N/A'
        try:
            node = process['details']['node']
            node_name = node['name']
            instance_type = node['labels']['beta.kubernetes.io/instance-type']
            node_name += " (%s)" % instance_type
        except (TypeError, KeyError):
            pass
        status = process['status'] + exit_code
        if is_color:
            status = click.style(status, fg=process_status_to_color.get(process['status'], 'white'))
        row = [
            process['process_id'],
            process['name'][:50],
            process['container'],
            status,
            submit_date,
            duration,
        ]
        if is_wide:
            row.extend(
                [
                    start_date_string,
                    complete_date_string,
                    runtime,
                    get_limits_string(process),
                    process['native_id'],
                    node_name,
                ]
            )
        table.append(row)

    tbl = tabulate(table, headers=headers)
    return tbl
