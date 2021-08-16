#!/usr/bin/env python
import os
from click import echo, secho, pass_context, command, argument, option

import hjson
import logging
import subprocess


from nextcode.credentials import generate_credential_struct, creds_to_dict
from nextcode.packagelocal import package_and_upload
from nextcode.exceptions import ServerError, UploadError

from nextcodecli.utils import abort

log = logging.getLogger(__name__)


@command()
@argument('pipeline_name', required=False)
@argument('project_name', required=False)
@option('-p', '--parameters', help="Parameters for the run", multiple=True)
@option('-s', '--script', help="Git link to a workflow (only for custom)")
@option('-c', '--context', help="Optional context string")
@option('-r', '--revision', help="Git SHA to run")
@option('--profile', help="Nextflow configuration profile to use")
@option('--local', 'local_folder', help='Run a local nextflow folder')
@option('-f', '--file', 'job_filename', help='Run a manifest file')
@option(
    '-t',
    '--trace',
    is_flag=True,
    help='Inject trace directives to get more debugging information in nextflow log',
)
@option(
    '-q', '--nowait', is_flag=True, help='Do not execute the watch command for a running pipeline'
)
@option('-d', '--description', help='A human readable description of the job')
@option('--storage_type', help="Overrides the pipeline storage type for the run")
@option(
    '--dedicated_storage_size',
    help="Overrides the pipeline dedicated storage size for the run. "
    "format: <num><binary_prefix> ex: 2400Gi",
)
@option(
    '--keep_resources',
    is_flag=True,
    help="Instructs the workflow service to exempt resources created for the workflow run from being automatically "
    "cleaned up after the run has finished.",
)
@option(
    '--mount_job',
    multiple=True,
    help='Makes the workflow service mount the working directory of Job id=<value> into this job under folder '
         '/job/<value>. Can be specified multiple times.',
    type=int
)
@option('-c', '--credentials', help="Credentials to forward to workflow-service", multiple=True)
@option('--executor_memory_mb', help='Override the memory limit of the nextflow executor')
@option('--scheduler_name', help="Overrides the scheduler to use for the run")
@option('-e', '--features', help="Extra parameters to pass to workflow-service to turn features on/off", multiple=True)
@pass_context
def run(
    ctx,
    pipeline_name,
    project_name,
    parameters,
    script,
    context,
    revision,
    profile,
    local_folder,
    job_filename,
    nowait,
    trace,
    description,
    storage_type,
    dedicated_storage_size,
    keep_resources,
    mount_job,
    credentials,
    executor_memory_mb,
    scheduler_name,
    features
):
    """
    Start a new nextflow job.

    Specify a named workflow and project or a manifest via --file.

    You can override all parameters in the file on the command-line via '-p key1=val1 -p key2=val2'

    If you are running against a debug server that allows direct script execution you
    can use 'custom' for pipeline_name.
    """

    manifest = {}
    params = {}
    credentials_map = creds_to_dict(credentials)
    if job_filename:
        with open(job_filename, 'r') as f:
            manifest = hjson.load(f)
        pipeline_name = pipeline_name or manifest.get('pipeline_name')
        project_name = project_name or manifest.get('project_name')
        script = script or manifest.get('script')
        revision = revision or manifest.get('revision')
        profile = profile or manifest.get('profile')
        context = context or manifest.get('context')
        params = manifest.get('params', {})
        if not credentials_map:  # If credentials were not passed via th commandline
            credentials_map = manifest.get('credentials', {})
        storage_type = storage_type or manifest.get('storage_type')
        dedicated_storage_size = dedicated_storage_size or manifest.get('dedicated_storage_size')

    credentials_struct = generate_credential_struct(credentials_map)

    features = {f.split('=')[0]:f.split('=')[-1] for f in features}

    try:
        override_params = {}
        for p in parameters:
            lst = p.split("=", 1)
            override_params[lst[0]] = lst[1].strip()
    except Exception:
        abort("Override parameters are badly formed. Expected '-p k1=v1 -p k2=v2'")

    for k, v in override_params.items():
        params[k] = v

    log.info(
        "Running pipeline '%s' on project '%s' with parameters %s and features %s",
        pipeline_name,
        project_name,
        dict(params),
        dict(features)
    )

    if mount_job:
        log.info(f"Mounting the working directory of the following jobs: {mount_job}")

    if not project_name:
        abort("You must specify PROJECT_NAME")
    if pipeline_name == 'custom' or not pipeline_name:
        if not script and not local_folder:
            abort(
                "If you are executing a custom script the you must specify a script or local folder"
            )
        pipeline_name = None
        if script and local_folder:
            abort("You cannot specify both a script and local folder")

    elif script or local_folder:
        abort("You cannot specify a script or local folder if you are running a named workflow")

    build_source = 'builtin'
    build_context = pipeline_name
    if local_folder:
        path = os.path.abspath(os.path.expanduser(local_folder))
        try:
            p = package_and_upload(ctx.obj.service, 'local_workflow', path)
        except UploadError as ex:
            abort(ex)
        build_source = 'url'
        build_context = p
    elif script:
        build_source = 'git'
        build_context = script

    try:
        job = ctx.obj.service.post_job(
            pipeline_name,
            project_name,
            params,
            script,
            revision or None,
            build_source,
            build_context,
            profile,
            trace,
            context=context,
            description=description,
            credentials=credentials_struct,
            storage_type=storage_type,
            dedicated_storage_size=dedicated_storage_size,
            keep_resources=keep_resources,
            mount_jobs=mount_job,
            executor_memory_mb=int(executor_memory_mb) if executor_memory_mb else None,
            scheduler_name=scheduler_name,
            features=features
        )
    except ServerError as e:
        abort(str(e))

    secho('Job %s has been submitted' % job.job_id, bold=True)

    if not nowait:
        job_id = job.job_id
        cmd = ['nextcode', 'workflow', 'job', str(job_id), 'watch']
        echo("Executing %s..." % ' '.join(cmd))
        subprocess.call(cmd)
