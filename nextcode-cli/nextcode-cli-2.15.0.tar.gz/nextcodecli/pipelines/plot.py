#!/usr/bin/env python

"""
Contains gnuplot methods for drawing graphs. Assumes macos and is generally a bit hacky.
At least we keep it all in one place.
"""
import os
import sys
import subprocess
import datetime
import dateutil.parser

import click

from ..utils import print_error


def write_instance_metrics_plot(
    job_id, instance_id, metrics, job_steps, width, height, max_num_points, is_all=False
):

    # check if gnuplot is installed
    try:
        p = subprocess.Popen(
            ['gnuplot', '-e', 'set terminal cairo'], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = p.communicate()
        if p.returncode != 0:
            raise Exception(err)
    except Exception as e:
        if sys.platform != "darwin":
            print_error("This method only supports macOS. Please use --raw option.")
            sys.exit(1)
        print_error(str(e))
        print_error("Gnuplot needs to be installed with cairo extension to view metrics.")
        click.echo("Please install with 'brew reinstall gnuplot --with-cairo'")
        sys.exit(1)
    proc = subprocess.Popen(
        ['gnuplot', '-p'], shell=True, stdin=subprocess.PIPE, close_fds=True  # Ignore B602
    )
    file_name = os.path.expanduser('~/job_%s.png' % job_id)
    try:
        os.remove(file_name)
    except Exception:
        pass

    input_string = """set datafile separator "\t"
set title "job {job_id} ({instance_id})"
set term pngcairo size {width}, {height}
set ylabel "Percent"
set xlabel "Time"
set xdata time
set timefmt "%Y-%m-%d %H:%M"
set format x "%H:%M"
set key left top
set grid
set output '{file_name}'
set yrange [0:100]
        """.format(
        job_id=job_id, instance_id=instance_id, file_name=file_name, width=width, height=height
    )
    proc.stdin.write(input_string.encode('UTF-8'))

    steps = []
    for step in job_steps:
        date_started = step.get('date_started')
        if not date_started or ('load' in step['step_name'] and not is_all):
            continue
        date_started = dateutil.parser.parse(date_started)
        date_started = date_started.replace(tzinfo=None, second=0, microsecond=0)
        steps.append((date_started, True, step['step_name'] + ' start'))
        if step.get('date_completed'):
            date_completed = dateutil.parser.parse(step.get('date_completed'))
            date_completed = date_completed.replace(tzinfo=None, second=0, microsecond=0)
            steps.append((date_completed, False, step['step_name'] + ' end'))

    arrow_commands = ""
    min_minutes = max(1, min(max_num_points / 40, 5))
    min_date = None
    for dt, is_start, name in sorted(steps):
        if min_date and dt < min_date + datetime.timedelta(minutes=min_minutes):
            dt = min_date + datetime.timedelta(minutes=min_minutes)
        min_date = dt
        col = [(3, '#000088'), (2, '#008800')][is_start]
        dt_label = dt + datetime.timedelta(seconds=90)
        arrow_commands += """set arrow from '{dt}', graph 1.0 to '{dt}', graph 0.7 ls {col1}
set label "{step}" at '{dt_label}',99 rotate right font "Arial,10" noenhanced front tc rgb "{col2}"
""".format(
            dt=dt, dt_label=dt_label, step=name, col1=col[0], col2=col[1]
        )
    arrow_commands = (arrow_commands + '\n').encode('UTF-8')
    proc.stdin.write(arrow_commands)

    plot_commands = "plot "
    for metric in metrics:
        if metric['num_points'] == 0:
            continue
        cmd = """"{filename}" using 1:2 with lines lw 2 title '{metric}', """.format(
            filename=metric['output'].name, metric=metric['metric_name']
        )
        plot_commands += cmd

    plot_commands = plot_commands[:-2]
    plot_commands = (plot_commands + '\n').encode('UTF-8')
    proc.stdin.write(plot_commands)
    return file_name
