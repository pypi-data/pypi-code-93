import json
import click
import requests
from time import strftime, gmtime
from trood.cli import utils
from trood.cli.utils import get_em_ulr


@click.group()
def space():
    pass


@space.command()
@click.pass_context
def ls(ctx):
    result = requests.get(
        get_em_ulr('api/v1.0/spaces/?only=id,name,alias,url'),
        headers={"Authorization": utils.get_token(ctx=ctx)}
    )

    namespace_phase = requests.get(
        get_em_ulr('api/v1.0/spaces/phase'),
        headers={"Authorization": utils.get_token(ctx=ctx)}
    ).json()

    data = result.json()
    for r in data:
        r['phase'] = namespace_phase[r['name']] if r['name'] in namespace_phase else "Unknown"

    if result.status_code == 200:
        utils.list_table(data)


@space.command()
@click.argument('space_id')
@click.pass_context
def rm(ctx, space_id):
    click.confirm(f'Do you want to remove space #{space_id} ?', abort=True)
    result = requests.delete(
        get_em_ulr(f'api/v1.0/spaces/{space_id}/'),
        headers={"Authorization": utils.get_token(ctx=ctx)}
    )

    if result.status_code == 204:
        click.echo(f'Space #{space_id} removed successfully!')


@space.command()
@click.argument('name')
@click.option('--template', default='default')
@click.pass_context
def create(ctx, name: str, template: str):
    response = requests.get(
        get_em_ulr(f'api/v1.0/market/spaces/{template}/'),
        headers={"Authorization": utils.get_token(ctx=ctx)},
    )

    if response.status_code == 200:
        data = response.json()
        prompts = {}

        for k, v in data['prompts'].items():
            is_password = v['type'] == 'password'
            prompts[k] = click.prompt(v['question'], hide_input=is_password, confirmation_prompt=is_password)

        result = requests.post(
            get_em_ulr('api/v1.0/spaces/'),
            headers={"Authorization": utils.get_token()},
            json={'name': name, 'template': template, 'prompts': prompts}
        )

        if result.status_code == 201:
            data = result.json()
            click.echo(f'Space {data["data"]["url"]} created successfully! ')
        elif result.status_code == 400:
            data = result.json()
            click.echo(data['msg'])
    else:
        click.echo(f'Cant create space from [{template}] template')


@space.command()
@click.argument('namespace')
@click.argument('path', type=click.Path(exists=True, file_okay=True))
@click.pass_context
def load_data(ctx, namespace, path): 
    click.echo("Your data is loading, please wait ...")

    try:
        result = requests.get(
            f"https://{namespace}.saas.trood.ru/authorization/api/v1.0/login/trood",
            headers={"Authorization":  utils.get_token(ctx=ctx)}
        )
        result.raise_for_status()
        fixtures = utils.get_fixtures(path)
        loader = utils.DataLoader(namespace, token=utils.get_token(ctx=ctx), verbose=ctx.obj.get('VERBOSE'))
        loader.apply_all(fixtures)
    except requests.HTTPError as err:
        click.echo(f"Authentication failed.\n Error: {err}")

@click.argument('space_alias')
@click.argument('comment', default='')
@click.argument('name', default=f'Backup {strftime("%b %d, %Y", gmtime())}')
@click.pass_context
def backup(ctx, space_alias, name, comment):
    if ctx and not ctx.obj.get('FORCE'):
        click.confirm(f'Do you want to create a backup of "{space_alias}"?', abort=True)

    result = requests.get(get_em_ulr(f'api/v1.0/spaces/?rql=eq(alias,{space_alias})'), headers={"Authorization": utils.get_token(ctx=ctx)})
    spaces = json.loads(result.text)
    space_id = None
    if spaces:
        space_id = spaces[0]['id']

    if not space_id:
        click.echo(f'Error while creating the backup: space "{space_alias}" does not exist', err=True)
    else:
        result = requests.post(
            get_em_ulr('api/v1.0/backups/'),
            headers={"Authorization": utils.get_token(ctx=ctx)},
            json={'space': space_id, 'name': name, 'comment': comment}
        )

        if result.status_code == 201:
            click.echo(f'Backup of space "{space_alias}" was successfuly created')
        else:
            click.echo(f'Error while creating the backup: {result.content}', err=True)
