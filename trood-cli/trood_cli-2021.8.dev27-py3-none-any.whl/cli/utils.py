import os
import keyring
import click
from tabulate import tabulate
import requests
import json


def get_em_ulr(path):
    host = os.environ.get("EM", "em.trood.com")
    return f'https://{host}/{path}'

def save_token(token):
    keyring.set_password("trood/em", "active", token)


def get_token(ctx: click.Context = None) -> str:
    if ctx:
        token = ctx.obj.get('TOKEN')

        if token:
            return f'Token {token}'

    try:
        token = keyring.get_password("trood/em", "active")

        if token:
            return f'Token {token}'
        else:
            click.echo(f'You need to login first.')
    except Exception:
        click.echo(f'Keychain not supported, use --token flag for authorization')


def clean_token():
    keyring.delete_password("trood/em", "active")


def list_table(items):
    if len(items):
        headers = items[0].keys()

        data = [i.values() for i in items]

        click.echo(tabulate(data, headers=headers))
        click.echo()
    else:
        click.echo('----------------- nothing to show')


def get_fixtures(fixtures_path):
    with open(fixtures_path) as json_file:
        fixtures = json.load(json_file)
    return fixtures


class DataLoader:
    def __init__(self, namespace, token, verbose=False):
        self.namespace = namespace
        self.headers = {'Authorization': token}
        self.verbose = verbose

    def get_record_url(self, data, service):
        if service == "custodian":
            return f'https://{self.namespace}.saas.trood.ru/custodian/data/{data["object"]}/'
        elif service != "custodian":
            return f'https://{self.namespace}.saas.trood.ru/{service}/api/v1.0/fixtures/'

    def apply_all(self, fixtures):
        for fixture in fixtures:
            service = fixture['target']
            for data in fixture["fixture"]:
                if data["type"] == "migration":
                    self.apply_migrations(data)
                elif data["type"] == "record":
                    self.upload_records(data, service)

    def apply_migrations(self, data):
        result = requests.post(
            f'https://{self.namespace}.saas.trood.ru/custodian/migrations/',
            json=data["migration"],
            headers=self.headers
        )
        if result.status_code == 200:
            click.echo(f"Migration {data['migration']['id']} is uploaded.")
        elif result.status_code == 400 and result.json()["error"]["Code"] == "duplicated_value_error":
            click.echo(f"Duplicate. Migration {data['migration']['id']} is already applied.")
        else:
            click.echo(f"Failed to upload migration {data['migration']['id']}.")
            if self.verbose:
                click.echo(result.json())

    def upload_records(self, data, service):
        result = requests.post(
            self.get_record_url(data, service),
            json=data["data"],
            headers=self.headers
        )
        if result.status_code == 200 and service == "custodian":
            click.echo(f"Records of {data['object']} are uploaded.")
        elif result.status_code == 200:
            click.echo(f"Records for {service} are uploaded.")

        elif result.status_code != 200 and service == "custodian":
            click.echo(f"Failed to upload {data['object']} records.")
            if self.verbose:
                click.echo(result.json())

        elif result.status_code != 200:
            click.echo(f"Failed to upload records for {service}.")
            if self.verbose:
                click.echo(result.json())
