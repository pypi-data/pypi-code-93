#!/usr/bin/env python

import datetime
import collections

import click
from tabulate import tabulate
import dateutil.parser

status_to_color = {
    'COMPLETED': 'green',
    'QUEUED': 'yellow',
    'INITIALIZING': 'yellow',
    'LAUNCHING': 'yellow',
    'RUNNING': 'yellow',
    'FAILED': 'red',
    'FINISHED': 'green',
}


def print_filelist(files, details=False):
    if not files:
        click.echo("Not found")
        return
    table = []
    for file in files:
        if details:
            sz = int(file.get('file_size', -1))
            if sz > 1024 * 1024:
                sz = "%.0f MB" % (int(sz) // 1024 // 1024)
            elif sz > 1024:
                sz = "%.0f KB" % (int(sz) // 1024)
            elif sz > 0:
                sz = "%.0f B" % sz
            else:
                sz = click.style('NOT FOUND', fg='yellow')

            table.append((file['file_name'], file['remote_path'], sz))
        else:
            table.append((file['file_name'], file['remote_path'], ""))
    tbl = tabulate(table, headers=['file_name', 'remote path', ''])
    click.echo(tbl)


def get_steps_table(job, color=True):
    step_list = []
    pending_steps = collections.defaultdict(int)
    for step in job.get('steps', []):
        dt_start = ''
        duration = '-'
        if step.get('date_started'):
            dt_start = dateutil.parser.parse(step['date_started'])
            dt_start = dt_start.replace(tzinfo=None)

            if step['date_completed']:
                dt_end = dateutil.parser.parse(step['date_completed'])
            else:
                dt_end = datetime.datetime.utcnow()
            dt_end = dt_end.replace(tzinfo=None)
            duration = (dt_end - dt_start).total_seconds()
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration = '%02d:%02d:%02d' % (int(hours), int(minutes), int(seconds))
            dt_start = dt_start.strftime("%H:%M")
            status = step['status']
            if color:
                col = status_to_color.get(status, '')
                status = click.style(status, fg=col, bold=True)
            step_list.append(
                (step['step_name'], step.get('step_identifier', ''), dt_start, duration, status)
            )
        else:
            pending_steps[step['step_name']] += 1

    for step_name in sorted(pending_steps):
        count = pending_steps[step_name]
        txt = step_name
        if count > 1:
            txt += " (x%s)" % count
        step_list.append((txt, '', '', '', 'PENDING'))
    steps_txt = tabulate(step_list, headers=['step', 'identifier', 'started', 'duration', 'status'])
    return steps_txt
