import os
import zipfile
from time import strftime, gmtime

import click
import requests

from trood.cli import utils


@click.group()
def application():
    pass


@application.command()
@click.pass_context
def ls(ctx):
    uri = 'api/v1.0/applications/?only=id,name,alias,type,subtype'
    if 'SPACE' in ctx.obj:
        uri = uri + f'&rql=eq(project,{ctx.obj["SPACE"]})'

    result = requests.get(
        utils.get_em_ulr(uri),
        headers={"Authorization": utils.get_token(ctx=ctx)}
    )

    if result.status_code == 200:
        utils.list_table(result.json())


@application.command()
@click.argument('app')
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--space', help='#id of Application`s Space you want to bundle update')
@click.pass_context
def bundle(ctx, app, path, space: str):
    if ctx and not ctx.obj.get('FORCE'):
        click.confirm(f'Do you want to publish "{path}" to #{app} application?', abort=True)

    space = space or ctx.obj.get('SPACE')

    if not space:
        raise click.BadParameter(f'Need to specify space ID for proper bundle upload', param_hint='--space', ctx=ctx)

    uri = f'api/v1.0/applications/?rql=eq(alias,{app}),eq(space,{space})'
    result = requests.get(
        utils.get_em_ulr(uri),
        headers={"Authorization": utils.get_token(ctx=ctx)}
    )

    if result.status_code != 200 or len(result.json()) == 0:
        raise click.ClickException(f'Application #{app} cant be accessed witin #{space} space.')

    app_obj = result.json()[0]

    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                fp = os.path.join(root, file)
                zp = fp.replace(path, '')

                ziph.write(filename=fp, arcname=zp)

    time = strftime("%Y-%m-%d__%H-%M-%S", gmtime())

    zipf = zipfile.ZipFile(f'{app}-{time}.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(path, zipf)
    zipf.close()

    result = requests.post(
        utils.get_em_ulr(f'api/v1.0/bundles/'),
        headers={"Authorization": utils.get_token(ctx=ctx)},
        data={'application': app_obj['id']},
        files={'file': open(f'{app}-{time}.zip', 'rb')}
    )

    if result.status_code == 201:
        click.echo(f'#{app_obj["alias"]} bundle was successfully published')
    else:
        click.echo(f'Error while publishing: {result.content}', err=True)