import shutil
import subprocess

import invoke

from .node import node_install, npm_install
from .utils import check_tools


@invoke.task(node_install)
def cdk(ctx):
    if shutil.which('cdk') is not None:
        return
    npm_install(ctx, ('aws-cdk',))


@invoke.task(cdk)
def deploy(ctx):
    ctx.run('cdk --app "inv cdk.infra" bootstrap')
    ctx.run('cdk --app "inv cdk.infra" deploy --all --require-approval=never', pty=True)


@invoke.task(cdk)
def destroy(ctx):
    ctx.run('cdk --app "inv cdk.infra" destroy --all --require-approval=never', pty=True)


@check_tools('aws')
def fetch_stack_output(app, key):
    query = f"Stacks[0].Outputs[?OutputKey=='{key}'].OutputValue"
    result = subprocess.check_output(
        (
            'aws', 'cloudformation', 'describe-stacks',
            '--stack-name', app,
            '--query', query,
            '--output', 'text',
        ),
    )
    return result.decode().strip()


@invoke.task
@check_tools('aws')
def reboot_instance(ctx, app, key='instanceid'):
    instance_id = fetch_stack_output(app, key)
    ctx.run(f'aws ec2 reboot-instances --instance-ids {instance_id}')


@invoke.task
@check_tools('aws')
def shell(ctx, app, key='publicip'):
    ip = fetch_stack_output(app, key)
    ctx.run(f'ssh -oStrictHostKeyChecking=no {ip} -l ec2-user', pty=True)
