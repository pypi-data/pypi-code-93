#!/usr/bin/env python

import os
import click
import requests
import subprocess
import hjson

from nextcode.packagelocal import package_and_upload
from nextcodecli.pipelines.jobs import post_job
from nextcodecli.utils import dumps, abort, print_warn, print_error


@click.command(help="Run a pipeline job. Pass in a manifest file for the job definition.")
@click.argument('job_filename', required=True)
@click.option('--local', 'local_folders', help='Run your local etl-pipelines folder in the worker')
@click.option(
    '--git',
    'git_branch',
    help='Run a specific git branch (or tag or sha), overriding the job manifest',
)
@click.option(
    '--pipeline-definition', help='Override the service pipeline definition with a local file'
)
@click.option(
    '--skip-definition',
    is_flag=True,
    default=False,
    help='Skip the pipeline definition validation.',
)
@click.option(
    '-f',
    '--force-start',
    is_flag=True,
    default=False,
    help='Start the worker immediately instead of going through the queue',
)
@click.option(
    '--test',
    'is_test',
    is_flag=True,
    default=False,
    help='Do not actually submit the job but just test basic validation',
)
@click.option('-q', '--nowait', help='Do not execute the watch command for a running pipeline')
@click.pass_context
def run(
    ctx,
    job_filename,
    local_folders,
    git_branch,
    pipeline_definition,
    skip_definition=False,
    force_start=False,
    is_test=False,
    nowait=False,
):
    svc = ctx.obj.service
    session = ctx.obj.session
    if not os.path.exists(job_filename):
        abort("Job filename '%s' not found" % job_filename)

    pipeline_definition_contents = None
    if pipeline_definition:
        path = os.path.expanduser(pipeline_definition)
        print_warn("Uploading local definition from {}".format(path))
        try:
            with open(path, 'r') as f:
                pipeline_definition_contents = hjson.load(f)
        except Exception as e:
            print_error(e)
            abort("Error loading pipeline definition: %s" % pipeline_definition)
    if skip_definition:
        print_warn("Skipping pipeline definition")
        pipeline_definition_contents = {}

    build_source = None
    build_context = None

    if local_folders:
        local_packages = []
        for local_folder in local_folders.split(','):
            project_path = os.path.expanduser(local_folder)
            if project_path.endswith('/'):
                project_path = project_path[:-1]
            project_path = os.path.abspath(project_path)

            project_name = 'etl-pipelines'

            # ! special case for duct tools upload
            if 'duct-tools' in project_path:
                project_name = project_path.split('/')[-1]

            p = package_and_upload(svc, project_name, project_path)
            local_packages.append(p)

        build_source = 'url'
        build_context = ','.join(local_packages)
    elif git_branch:
        build_source = 'git'
        build_context = git_branch

    try:
        manifest = None
        try:
            with open(job_filename, 'r') as f:
                manifest = hjson.load(f)
        except Exception as e:
            raise RuntimeError("Manifest file '%s' is invalid: %s" % (job_filename, e))

        responses = post_job(
            session,
            manifest,
            build_source,
            build_context,
            pipeline_definition_contents,
            force_start=force_start,
            is_test=is_test,
        )
    except Exception as e:
        print_error('ERROR posting job: %s' % str(e))
        raise
    # pylint: disable=E1101
    for resp in responses:
        if resp.status_code not in (requests.codes.ok, requests.codes.created):
            try:
                print_error(
                    "Error creating job: %s"
                    % (resp.json()['error']['description'] or resp.json()['message'])
                )
            except Exception:
                print_error(resp.text)
        else:
            click.echo(
                "Job for sample {} submitted. View job with: "
                "nextcode pipelines job {} view".format(
                    resp.json().get('sample_name', ''), resp.json().get('job_id')
                )
            )

    if is_test:
        try:
            formatted_json = dumps(resp.json())
            click.echo("Response:")
            click.echo(formatted_json)
        except Exception:
            click.echo(resp.text)
        click.secho("This was just a test. No job was actually submitted", fg='yellow', bold=True)
        return

    if not nowait:
        # typical case of single job
        if len(responses) == 1 and 200 <= responses[0].status_code <= 201:
            job_id = resp.json()['job_id']
            cmd = ['nextcode', 'pipelines', 'job', str(job_id), 'watch']
            click.echo("Executing %s..." % ' '.join(cmd))
            subprocess.call(cmd)
