from enum import Enum
from typing import Type

import inquirer
import typer

from openapi_client import ResponseOrganization
from savvihub.api.savvihub import SavviHubClient
from savvihub.api.exceptions import InvalidParametersAPIException, DuplicateAPIException
from savvihub.cli.exceptions import ExitException
from savvihub.cli.constants import DATASET_VERSION_HASH_LATEST


def get_default_organization(client: SavviHubClient) -> ResponseOrganization:
    organizations = client.organization_list().organizations
    if len(organizations) == 0:
        region_list_resp = client.region_list()
        typer.echo('Create organization')
        while True:
            organization_name = inquire_text("Organization name")
            region = inquire_list(
                "Select region",
                [(region.name, region.value) for region in region_list_resp.regions],
                default=region_list_resp.default_region,
            )
            
            try:
                default_organization = client.organization_create(organization_name=organization_name, region=region)
                break
            except InvalidParametersAPIException:
                typer.echo('Invalid organization name. Please try again.')
            except DuplicateAPIException:
                typer.echo('Duplicate organization name exist. Please try again.')

    elif len(organizations) == 1:
        default_organization = organizations[0]
        typer.echo(f'Default organization is automatically set to `{default_organization.name}`.')
        
    else:
        default_organization = inquire_list(
            'Select default organization',
            [(ws.name, ws) for ws in organizations],
        )
        typer.echo(f'Default organization is set to `{default_organization.name}`.')

    return default_organization


def inquire_text(message, default=None):
    key = 'question'
    inquiry = inquirer.Text(key, message=message, default=default)
    return inquirer.prompt([inquiry], raise_keyboard_interrupt=True).get(key)


def inquire_int(message, default=None):
    text = inquire_text(message, default)
    try:
        value = int(text)
    except ValueError:
        raise ExitException(f"Invalid '{text}'. Please enter a valid number.")
    return value


def inquire_float(message, default=None):
    text = inquire_text(message, default)
    try:
        value = float(text)
    except ValueError:
        raise ExitException(f"Invalid '{text}'. Please enter a valid number.")
    return value


def inquire_list(message, choices, default=None):
    key = "question"
    inquiry = inquirer.List(key, message=message, default=default, choices=choices)
    return inquirer.prompt([inquiry], raise_keyboard_interrupt=True).get(key)


def validate_text(value, error_message, nonempty=True, max_length=None):
    if (
        not isinstance(value, str)
        or (nonempty and not value.strip())
        or (max_length is not None and len(value.strip()) > max_length)
    ):
        raise ExitException(error_message)


def validate_int(value, error_message, gt=None, gte=None, lte=None, lt=None):
    # Must satisfy: gt < value < lt, gte <= value <= lte
    if (
        not isinstance(value, int)
        or (gt is not None and gt >= value)
        or (gte is not None and gte > value)
        or (lte is not None and lte < value)
        or (lt is not None and lt <= value)
    ):
        raise ExitException(error_message)


def validate_float(value, error_message, gt=None, gte=None, lte=None, lt=None):
    # Must satisfy: gt < value < lt, gte <= value <= lte
    if (
        not (isinstance(value, float) or isinstance(value, int))
        or (gt is not None and gt >= value)
        or (gte is not None and gte > value)
        or (lte is not None and lte < value)
        or (lt is not None and lt <= value)
    ):
        raise ExitException(error_message)


def validate_enum(value, enum_class: Type[Enum], error_message=None):
    try:
        enum_class(value)
    except ValueError as e:
        raise ExitException(error_message or str(e))


def parse_dataset(dataset_full_name):
    if '@' in dataset_full_name:
        dataset_name, dataset_version_hash = dataset_full_name.split('@', 1)
    else:
        dataset_name = dataset_full_name
        dataset_version_hash = DATASET_VERSION_HASH_LATEST

    if '/' in dataset_name:
        organization_name, dataset_name = dataset_name.split('/', 1)
    else:
        organization_name = None

    return organization_name, dataset_name, dataset_version_hash
