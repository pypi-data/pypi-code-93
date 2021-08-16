#!/usr/bin/env python

import json
import click
from click import echo, secho, pass_context, command, argument, option

from nextcode.exceptions import ServerError

from nextcodecli.utils import dumps, print_table, print_tab
from nextcodecli import get_version_string


@command(help="Show the status of the workflow service")
@option('-r', '--raw', 'is_raw', is_flag=True, help='Dump raw json response')
@pass_context
def status(ctx, is_raw):
    svc = ctx.obj.service
    session = ctx.obj.service.session
    profile_config = svc.client.profile
    profile_name = svc.client.profile_name
    if is_raw:
        dct = {
            'version': get_version_string(),
            'profile': profile_name,
            'profile_config': profile_config.content,
        }
        for key in ('build_info', 'app_info', 'endpoints', 'current_user'):
            dct[key] = getattr(session, key, None)
        resp = session.get(session.url_from_endpoint('pipelines'))
        resp.raise_for_status()
        dct['pipelines'] = [p['name'] for p in resp.json()['pipelines']]
        click.echo(dumps(dct))
    else:
        click.echo(get_version_string() + '\n')

        click.echo("Contacting workflow service '%s'... " % svc.base_url, nl=False)

        click.echo("Success!\n\nAPI deployment information:")
        print_table(svc.build_info)
        print_table(svc.app_info)

        click.echo('')


@command(help="Run a smoketest of the workflow service")
@option(
    '--test',
    type=click.Choice(['viewscm', 'listwork', 'nextflowinfo', 'nextflowrun']),
    default='nextflowrun',
    show_default=True,
    help="Name of the test to run",
)
@option(
    '--timeout',
    type=int,
    default=30,
    show_default=True,
    help="Number of seconds to wait for test to complete",
)
@pass_context
def smoketest(ctx, test, timeout):
    session = ctx.obj.session
    url = session.url_from_endpoint('health') + 'smoketest'
    secho("Running smoketest by calling POST %s... This might take a while." % url, bold=True)
    try:
        resp = session.post(url, json={'test': test, 'timeout': timeout})
    except ServerError as e:
        secho("Smoketest failed!", fg='red', bold=True)
        r = e.response
        if not r:
            echo(repr(e))
            return
        try:
            error = r.get('error', {})
            pod_name = error.get('pod_name')
            state = json.loads(error.get('state', '{}'))
            exit_code = state.get('_exit_code')
            print_tab("Error code", r.get('code'))
            print_tab("Error description", error.get('description'))
            if pod_name:
                print_tab("Pod name", pod_name)
            if exit_code:
                print_tab("Exit code", exit_code)
            if state:
                print_tab("Reason", state.get('_reason'))
                state_txt = ""
                try:
                    state_txt = ['%s: %s' % (k, v) for k, v in state.items() if v][0]
                except:
                    pass
                print_tab("State", state_txt)
                print_tab("Container message", state.get('_message'))

            if pod_name and not exit_code:
                echo(
                    "You can investigate this issue further by running 'kubectl describe pod %s -n gorkube'"
                    % pod_name
                )
        except Exception as e:
            raise
            echo(dumps(r))
    else:
        secho("Smoketest succeeded!", bold=True, fg='green')
        echo(
            "Nextflow pod completed successfully and produced the following output:\n%s"
            % "\n".join(resp.json()['logs'])
        )
