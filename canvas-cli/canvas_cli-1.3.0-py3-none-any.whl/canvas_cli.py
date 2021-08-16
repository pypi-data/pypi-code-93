#!/usr/bin/env python

import importlib.util
import json

from os.path import basename, exists, join
from pathlib import Path
from typing import Any, cast, Dict, List, TypedDict, Union

import arrow
import click
import requests

from canvas_workflow_sdk.patient import Patient
from canvas_workflow_sdk.serializers.protocol import ProtocolSerializer
from canvas_workflow_sdk.timeframe import Timeframe

from stringcase import camelcase
from decouple import Config, RepositoryIni

mocks_path = 'TODO'


def get_settings_path() -> Path:
    return Path.home() / '.canvas' / 'config.ini'


def read_settings(ctx) -> Dict[str, Any]:

    try:
        ini = RepositoryIni(get_settings_path())
    except FileNotFoundError:
        raise click.ClickException(
            f'Please add your configuration at "{get_settings_path()}"; you can set '
            'defaults using `canvas-cli create-default-settings`.')

    if not ini.parser.has_section(ctx.obj['config_section']):
        raise click.ClickException(
            f'Settings file "{get_settings_path()}" does not contain section "{ctx.obj["config_section"]}"; '
            'you can set defaults using `canvas-cli create-default-settings`.')

    ini.SECTION = ctx.obj['config_section']
    config = Config(ini)

    ## LEFT OFF HERE

    settings: Dict[str, Any] = {
        'url': config('url', cast=str),
        'api_key': config('api-key', cast=str)
    }

    return settings


class PatientData(TypedDict):
    billingLineItems: List
    conditions: List
    imagingReports: List
    immunizations: List
    instructions: List
    interviews: List
    labReports: List
    medications: List
    referralReports: List
    vitalSigns: List
    patient: Dict[str, Any]
    protocolOverrides: List
    changeTypes: List
    protocols: List


def load_patient(fixture_folder: Path) -> Patient:
    data: PatientData = {
        'billingLineItems': [],
        'conditions': [],
        'imagingReports': [],
        'immunizations': [],
        'instructions': [],
        'interviews': [],
        'labReports': [],
        'medications': [],
        'referralReports': [],
        'vitalSigns': [],
        'patient': {},
        'protocolOverrides': [],
        'changeTypes': [],
        'protocols': [],
    }

    file_loaded = False

    for filepath in fixture_folder.glob('*.json'):
        file_loaded = True

        filename = str(basename(filepath))
        field = camelcase(filename.split('.')[0])

        with open(filepath, 'r') as file:
            if field not in data:
                raise click.ClickException(
                    f'Found file that does not match a known field: "{field}"')

            data[field] = json.load(file)  # type: ignore

    if not file_loaded:
        raise click.ClickException(f'No JSON files were found in "{fixture_folder}"')

    data['patient']['key'] = fixture_folder.name

    # click.echo(json.dumps(data, indent=2))

    return Patient(data)


# def load_patient_data(patient_key: str, field: str) -> List:
#     """
#     Load data from mock data JSON files dumped by the dump_patient command.
#     """
#     filename = f'{mocks_path}/{patient_key}/{field}.json'

#     if not exists(filename):
#         if field == 'patient':
#             raise Exception(f'Missing mock patient data for "{patient_key}"!')

#         return []

#     with open(filename, 'r') as file:
#         return json.load(file)  # type: ignore


@click.group()
@click.pass_context
@click.option('--use-config', required=False)
def cli(ctx, use_config='canvas_cli'):

    ctx.ensure_object(dict)
    ctx.obj['config_section'] = use_config and use_config or 'canvas_cli'

    if ctx.invoked_subcommand != 'create-default-settings':
        ctx.obj['settings'] = read_settings(ctx)


@cli.command()
def create_default_settings():
    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    click.echo(f'Writing default settings to "{settings_path}"...')

    settings_path.write_text('''[canvas_cli]
url =
api-key =
''')


@cli.command()
@click.argument('patient-key')
@click.argument('output_directory', nargs=1, required=False, type=click.Path())
@click.pass_context
def fixture_from_patient(ctx, patient_key: str, output_directory: Path):
    """
    Export a fixture for a given patient.  Providing an
    output directory will create a json file for each key.
    Eg: billingLineItems.json, conditions.json, referralReports.json ...
    """
    click.echo(f'Getting fixture from patient "{patient_key}"...')

    response = requests.get(join(
        ctx.obj["settings"]["url"], f'api/PatientProtocolInput/{patient_key}'
    ), headers={'Authorization': ctx.obj['settings']['api_key']})
    response.raise_for_status()
    response_json = response.json()

    if not output_directory:
        click.echo(response_json)
    else:
        output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        for key, values in response_json.items():
            (output_directory/f'{key}.json').write_text(json.dumps(values))
        click.echo(green(f'Successfully wrote patient fixture to {output_directory.absolute()}'))


def green(string: str) -> str:
    return click.style(string, fg='green')


@cli.command()
@click.argument('module-name')
@click.argument('class-name')
@click.argument('fixture-folder')
@click.option('--date')
def test_fixture(module_name: str, class_name: str, fixture_folder: str, date: str = None):
    module_path = Path(module_name)
    module_and_class = f'{module_path.stem}.{class_name}'

    click.echo(f'Executing "{green(module_and_class)}" with fixture "{green(fixture_folder)}"...')

    # 1. load module to test
    spec = importlib.util.spec_from_file_location(basename(module_name), module_name)

    if not spec:
        raise click.ClickException(f'Unable to load "{module_name}".')

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)  # type: ignore

    Class = getattr(module, class_name)

    # 2. load JSON folder of fixture data
    patient = load_patient(Path(fixture_folder))

    # if date:
    #     date = arrow.get(date)
    # else:
    #     date = arrow.now()  # utc?

    start = arrow.get('2017-10-23 13:24:56')
    end = arrow.get('2018-08-23 13:24:56')
    date = arrow.get('2018-08-23 13:24:56')

    timeframe = Timeframe(start=start, end=end)

    # 3. instantiate module
    protocol = Class(patient=patient, date=date, timeframe=timeframe)
    results = protocol.compute_results()

    serialized = ProtocolSerializer(protocol).data

    # 4. return results
    click.echo('\nOutput:\n')
    click.echo(json.dumps(serialized, indent=2))


@cli.command()
def upload():
    click.echo('Uploading...')


@cli.command()
@click.argument('module-name')
@click.argument('version')
def set_active(module_name: str, version: str):
    click.echo(f'Setting version "{version}" of "{module_name}" as active...')


if __name__ == '__main__':
    cli()
