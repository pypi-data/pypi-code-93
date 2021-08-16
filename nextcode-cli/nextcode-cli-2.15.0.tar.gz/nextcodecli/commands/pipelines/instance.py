#!/usr/bin/env python

import os, sys
import collections
import json
import uuid
import datetime
from operator import itemgetter
import subprocess
import tempfile
import click
import boto3
import dateutil

from nextcodecli.utils import (
    get_logger,
    dumps,
    abort,
    print_tab,
    print_error,
    print_warn,
    print_success,
)
from nextcodecli.pipelines.plot import write_instance_metrics_plot


class WXNCSecureShellError(Exception):
    pass


WORKER_NOT_READY_MSG = (
    "Could not connect to worker- the worker might not be up yet.\n" "Try again in a few minutes."
)
JOB_NOT_LAUNCHED_MSG = "Job has not instance."
BASTION_UNREACHABLE_MSG = (
    "Can not connect to worker - "
    "bastion host is not defined for profile.\n"
    "Check with your administrator whether SSH access "
    "to pipeline workers is enabled."
)


log = get_logger(__file__)


@click.group(help="Manage the worker EC2 instance (developer-only)")
@click.pass_context
def instance(ctx):
    instances = ctx.obj.job.get('instances')
    if not instances:  # None or [ ].
        abort(JOB_NOT_LAUNCHED_MSG)
    else:
        ctx.obj.instance_id = instances[0]['instance_id']


def get_instance_for_job(session, job_resource):
    link = session.links(job_resource)['instances']
    resp = session.get(link)
    resp.raise_for_status()
    try:
        instance_url = resp.json()[0]['links']['self']
    except IndexError:
        return None
    resp = session.get(instance_url)
    job_instance = resp.json()

    current_url = job_instance['links']['current']
    job_instance['current'] = {}
    try:
        resp = session.get(current_url)
        resp.raise_for_status()
        job_instance['current'] = resp.json()
    except Exception:
        pass

    # ! backwards-compatible hack since the details used to be a string from the API
    try:
        job_instance['details'] = json.loads(job_instance.get('details', '{}'))
    except Exception:
        pass
    return job_instance


@instance.command(
    'refresh',
    help="Force update the status of the job to reflect"
    "Instance tags. This is meant for local development",
)
@click.option('-s', '--status', help='Manually update the status of the job')
@click.pass_context
def instance_refresh(ctx, status):
    """This is only meant for local development or in cases where the sqs worker lambda
    is not correctly updating the status of the job in the pipelines-service.
    The duct-tools process on the worker updates the tag of the ec2 machine as well as
    notify the SQS service and we can poll for this flag to manually update the status
    in the pipelines-service.
    """
    session = ctx.obj.session
    job_resource = ctx.obj.job
    job_status = job_resource['status']
    events_url = job_resource['links']['events']
    if status:
        instance_status = status
    else:
        instance_resource = get_instance_for_job(session, job_resource)
        if not instance_resource or not instance_resource['current']:
            abort("Instance not found")

        current = instance_resource['current']
        instance_status = None
        for tag in current['Tags']:
            if tag['Key'] == 'job-status':
                instance_status = tag['Value']

    if instance_status != job_status:
        click.echo(
            "Instance has status '%s' and job has status '%s'" % (instance_status, job_status)
        )
        # create a 'fake' event to trigger the job to switch to the desired status
        # normally this event would come from the sqs worker lambda but in our localhost
        # case that lambda is not servicing the api
        event_guid = str(uuid.uuid4())
        event_name = ''
        if instance_status in ('RUNNING',):
            event_name = 'job_started'
        elif instance_status in ('FINISHED', 'FAILED', 'CANCELLED'):
            event_name = 'job_completed'
        body = {
            'event_name': event_name,
            'event_guid': event_guid,
            'event': {'status': instance_status},
            'date_time': datetime.datetime.utcnow().isoformat(),
        }
        resp = session.post(events_url, json=body)
        resp.raise_for_status()
        click.echo("Job status has been updated to '%s'" % instance_status)
    else:
        click.echo("Job status '%s' matches instance status" % job_status)


def test_connection(host_name, ssh_cmd):
    # Helper for testing ssh connectivity.

    log.debug("SSH test command for {host}: {cmd}".format(host=host_name, cmd=ssh_cmd))
    proc = subprocess.Popen(ssh_cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderr, stdout = proc.communicate()
    log.debug(
        "SSH test command returned: exit code: {code}stdout:{stdout}, stderr:{stdout}".format(
            code=proc.returncode, stdout=stdout, stderr=stderr
        )
    )
    if proc.returncode != 0:
        # sometimes errors come through stdout - who'da thunk it?
        reason = (stderr or stdout).decode().strip("\r\n")
        err_msg = (
            "Could not connect to {host_name}. Reason given:\n{reason} - "
            "Exit code: {exit_code}".format(
                host_name=host_name,
                exit_code=proc.returncode,
                reason=click.style(reason, bold=True),
            )
        )
        raise WXNCSecureShellError(err_msg)
    return proc.returncode


def initialize_ssh_keys(key_name=None):
    if key_name is None:
        log.debug("no keyname specified - trying default key")
        os.system("ssh-add")
        return
    try_paths = [os.getcwd(), "~/.ssh/"]
    for path in try_paths:
        key_file_path = "{path}/{key_name}".format(path=path, key_name=key_name)
        log.debug("Trying to add {path}".format(path=key_file_path))

        if os.path.isfile(key_file_path):
            # Ignore B605 - key_file_path is not a user-supplied variable.
            os.system("ssh-add {key_file_path}".format(key_file_path=key_file_path))
        else:
            log.debug("{path} not found or not a valid key".format(path=key_file_path))


# Display this  string if we have no idea what the error is.
SSH_ERROR_HELP = """{error_message}

Common causes for failures:

1) Feature is disabled.
   The pipeline worker ssh command is only meant for development environments.
   Please contact the administrator of your environment for further information.

2) SSH-key misconfiguration.
   The nextcode-cli requires two SSH keys to open a secure shell to the pipeline workers.
   These are:
    * The bastion SSH key
    * The pipeline worker ssh key

   Provided these keys, you should run the following commands before retrying.
    * Start the agent:
      $ eval `ssh-agent`
    * Add the keys
      $ ssh-add [path-to-bastion-SSH-key]
      $ ssh-add [path-to-pipeline-worker-SSH-key]
      """


@instance.command('ssh', help="SSH into a the running worker instance. Requires SSH key.")
@click.option(
    '-p',
    '--public',
    is_flag=True,
    help='Connect to the public IP of the instance instead of going through bastion',
)
@click.pass_context
def instance_ssh(ctx, public):
    session = ctx.obj.session
    svc = ctx.obj.service
    job_resource = ctx.obj.job
    job_id = job_resource['job_id']
    worker = get_instance_for_job(session, job_resource)
    if not worker:
        abort("Instance not found")

    if public:
        username = 'ubuntu'
        public_dns_name = worker.get('current', {}).get('PublicDnsName')
        if not public_dns_name:
            abort("Public DNS not found")
        key_name = worker.get('current', {}).get('KeyName')
        key_file = '~/.ssh/{}'.format(key_name)
        cmd = [
            'ssh',
            '-oStrictHostKeyChecking=no',
            '-i',
            key_file,
            '-t',
            '{}@{}'.format(username, public_dns_name),
        ]
        print(" ".join(cmd))
        subprocess.call(cmd)
        return

    try:
        bastion_host = svc.app_info.get('bastion_host')
        if bastion_host is None:
            raise abort(BASTION_UNREACHABLE_MSG)

        instance_id = worker['instance_id']
        if not worker['current']:
            abort(
                "Unable to connect. Instance {instance_id} has been terminated.".format(
                    instance_id=instance_id
                )
            )

        state = worker['current']['State']['Name']
        if state.lower() != 'running':
            err_str = "Instance '{instance_id}' is in state '{state}' which is not 'running'. \n"
            err_str += "Start with 'nextcode pipelines job {job_id} instance start'"
            abort(err_str.format(instance_id=instance_id, job_id=job_id, state=state.lower()))

        worker_ip_address = worker['current']['PrivateIpAddress']
        if not worker_ip_address:
            err_msg = WORKER_NOT_READY_MSG
            abort(err_msg.format(instance_id=instance_id))

        pipeline_path = '/opt/etl-pipelines/pipelines/%s' % job_resource['details']['pipeline_name']

        # Base templates for a worker and bastion ssh commands
        worker_ssh_cmd = " ssh -t {worker_options} {username}@{public_dns_name}{worker_cmd}"
        bastion_ssh_cmd = "ssh {bastion_options} -tA {bastion_host} {cmd}"
        key_name = worker.get('current', {}).get('KeyName')
        # Let's try to autodiscover the worker ssh key - it's a bit of a long shot, but it's free.
        initialize_ssh_keys(key_name)
        # While we're at it, let's attempt adding the default bastion key as well.
        initialize_ssh_keys()

        click.echo("Connecting to bastion host {host}... ".format(host=bastion_host), nl=False)

        # Create a version of the sshs string which immediately exit - for testing.
        # This allows us to give more fine-grained error messaging to the user.
        test_bastion_cmd = bastion_ssh_cmd.format(
            bastion_host=bastion_host,
            bastion_options="-oBatchMode=yes -oStrictHostKeyChecking=no",
            cmd='exit',
        )

        test_worker_ssh_cmd = worker_ssh_cmd.format(
            worker_options="-oBatchMode=yes -oStrictHostKeyChecking=no",
            username='ubuntu',
            public_dns_name=worker_ip_address,
            worker_cmd=' exit',
        )

        # Verify that we can connect, both to the bastion and the worker host.
        try:
            if test_connection('bastion host', test_bastion_cmd) == 0:
                print_success("SUCCESS")
        except WXNCSecureShellError as wex:
            if "Permission denied (publickey" in str(wex):
                raise WXNCSecureShellError(
                    "Unable to connect to bastion host due to wrong or missing SSH key"
                )
            else:
                raise
        try:
            test_connection(
                'worker instance', test_bastion_cmd.replace(' exit', test_worker_ssh_cmd)
            )
        except WXNCSecureShellError as wex:

            if "Permission denied (publickey" in str(wex):
                print_error(
                    "Unable to connect to worker due to wrong or missing SSH key",
                    "Key [{key_name}] needs to be added to your ssh-agent".format(
                        key_name=key_name
                    ),
                )
                print("Try this:")
                print("  eval `ssh-agent`")
                print("  ssh-add ~/.ssh/id_rsa")
                print("  ssh-add ~/.ssh/%s" % key_name)
                sys.exit(1)

            elif "ssh_exchange_identification: Connection closed by remote host" in str(wex):
                abort(WORKER_NOT_READY_MSG)
            else:
                raise

        worker_ssh_cmd = worker_ssh_cmd.format(
            public_dns_name=worker_ip_address,
            username='ubuntu',
            worker_options='-oStrictHostKeyChecking=no',
            worker_cmd=' /bin/bash',
        )

        # Construct the final ssh string.
        full_ssh_cmd = bastion_ssh_cmd.format(
            bastion_options='-oStrictHostKeyChecking=no',
            bastion_host=bastion_host,
            cmd=worker_ssh_cmd,
        )

        # print out the steps for reference
        try:
            click.echo("Job status:")
            for step in sorted(
                [s for s in job_resource['steps'] if s['step_identifier']],
                key=itemgetter('step_identifier'),
            ):
                print_tab(step['step_identifier'], step['step_name'])
            click.echo("# Pipeline path:\n  {pipeline_path}".format(pipeline_path=pipeline_path))
        except Exception as e:
            print_error(repr(e))

        click.echo("Connecting to worker ... ")
        exit_code = subprocess.call(full_ssh_cmd.split(" "))

        if exit_code not in [0, 127, 130]:  # Exit code 139 is Ctrl-C.
            # Exit code 127 sometimes pops up for no reason.
            raise WXNCSecureShellError(
                "Failed to connect to worker. Exit code {exit_code}".format(exit_code=exit_code)
            )
    except WXNCSecureShellError as shhex:
        abort(SSH_ERROR_HELP.format(error_message=shhex))


def start_or_stop_instance(ctx, action):
    session = ctx.obj.session
    job_resource = ctx.obj.job
    instance_resource = get_instance_for_job(session, job_resource)
    if instance_resource['details'].get('InstanceLifecycle') == 'spot':
        abort("Spot Instances cannot be started or stopped")
    if not instance_resource:
        abort("Instance not found")
    link = session.links(instance_resource)['self']
    resp = session.patch(link, json={'action': action})
    if resp.status_code != 200:
        abort("Cannot %s instance: %s" % (action, resp.json().get('message')))
    print(json.dumps(resp.json(), indent=4))
    resp.raise_for_status()


@instance.command('start', help="Start the worker instance for the job.")
@click.pass_context
def instance_start(ctx):
    start_or_stop_instance(ctx, 'start')


@instance.command('stop', help="Stop the worker instance for the job.")
@click.pass_context
def instance_stop(ctx):
    start_or_stop_instance(ctx, 'stop')


@instance.command('view', help="View instance information for the job.")
@click.option('-r', '--raw', 'is_raw', is_flag=True, help='Dump raw json response')
@click.pass_context
def instance_view(ctx, is_raw):
    """Quick and dirty instance viewer."""
    session = ctx.obj.session
    job_resource = ctx.obj.job
    instance_resource = get_instance_for_job(session, job_resource)
    if not instance_resource:
        abort("Instance not found")
    details = instance_resource['details']
    ami_details = instance_resource.get('ami_details', {})
    current = instance_resource['current']
    ami_version = None
    etl_pipelines_version = None
    for tag in ami_details.get('Tags', []):
        if tag['Key'] == 'version':
            ami_version = tag['Value']
        elif tag['Key'] == 'etl-pipelines-version':
            etl_pipelines_version = tag['Value']
    if is_raw:
        dct = {
            'instance_status_at_launch': details,
            'ami_details': ami_details,
            'current_instance_status': current,
        }
        click.echo(dumps(dct))
    else:
        rows = collections.OrderedDict()
        rows['Instance ID'] = details['InstanceId']
        rows['Instance Type'] = details['InstanceType']
        rows['SSH Key Name'] = details['KeyName']
        rows['Launch Time'] = details['LaunchTime']
        rows['AMI ID'] = details['ImageId']
        rows['AMI Version'] = ami_version
        rows['ETL Pipelines'] = etl_pipelines_version
        rows['Private IP Address'] = details['PrivateIpAddress']
        rows['Public IP Address'] = current.get('PublicIpAddress', 'N/A')
        rows['VPC ID'] = details['VpcId']
        if 'InstanceLifecycle' in details:
            rows['InstanceLifecycle'] = details['InstanceLifecycle']
        rows['Placement'] = current.get('Placement', {}).get('AvailabilityZone', 'Unknown')

        rows['Current Status'] = current.get('State', {}).get('Name', 'NOT FOUND')

        for k, v in rows.items():
            print_tab(k, v)


@instance.command('metrics', help="View metrics for instance")
@click.pass_context
@click.option('-r', '--raw', 'is_raw', is_flag=True, help='Dump raw json response')
@click.option('-a', '--all', 'is_all', is_flag=True, help='Include all steps')
@click.option('-p', '--period', 'period', default=1, help='Minutes between data points')
@click.option('-w', '--width', 'image_width', default=1920, help='Width of the output image')
@click.option('-h', '--height', 'image_height', default=1024, help='Height of the output image')
def instance_metrics(ctx, is_raw, period, is_all, image_width, image_height):
    session = ctx.obj.session
    job_resource = ctx.obj.job
    job_id = job_resource['job_id']
    instance_resource = get_instance_for_job(session, job_resource)
    if not instance_resource:
        abort("Instance not found")
    metrics_url = instance_resource['links']['metrics']
    instance_id = instance_resource['instance_id']
    data = {'period': period}
    resp = session.get(metrics_url, data=data)
    if resp.status_code != 200:
        abort("Could not get metrics for instance %s: %s" % (instance_id, resp.text))
    max_num_points = 0
    metrics = []
    for metric_name, points in resp.json().items():
        metric = {
            "metric_name": metric_name,
            "output": tempfile.NamedTemporaryFile(mode='w', delete=False),
            "num_points": 0,
        }
        metrics.append(metric)
        results = {}
        for p in points:
            dt = dateutil.parser.parse(p['date_time'])
            results[dt] = p['value']

        metric['num_points'] = num_points = len(results)
        if num_points > 0:
            click.echo("%s - %s datapoints found" % (metric_name, num_points))
            if num_points > max_num_points:
                max_num_points = num_points

            left_trim = True
            for k in sorted(results.keys()):
                if left_trim and results[k] == 0:
                    continue
                left_trim = False
                line = "%s\t%s" % (k.strftime('%Y-%m-%d %H:%M'), results[k])
                if is_raw:
                    click.echo(line)
                else:
                    metric['output'].write(line + '\n')
            metric['output'].close()

    if max_num_points == 0:
        print_warn("No metrics found for instance %s" % instance_id)
        return
    if is_raw:
        return
    file_name = write_instance_metrics_plot(
        job_id,
        instance_id,
        metrics,
        job_resource['steps'],
        image_width,
        image_height,
        max_num_points,
        is_all,
    )
    if file_name:
        click.secho("Graph will be produced here: %s" % file_name, fg='green', bold=True)
