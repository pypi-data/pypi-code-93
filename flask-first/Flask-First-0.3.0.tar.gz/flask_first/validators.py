from typing import Iterable

from marshmallow import fields
from marshmallow import Schema
from marshmallow import validate
from marshmallow.exceptions import ValidationError as MarshmallowValidationError
from marshmallow.fields import Field

from .exc import FlaskFirstPathParameterValidation
from .exc import FlaskFirstValidation

FIELDS_VIA_TYPES = {
    'boolean': fields.Boolean(),
    'object': fields.Dict(),
    'number': fields.Float(),
    'string': fields.String(),
    'integer': fields.Integer(),
}

FIELDS_VIA_FORMATS = {
    'uuid': fields.UUID(),
    'date-time': fields.DateTime(),
    'date': fields.Date(),
    'time': fields.Time(),
    'email': fields.Email(),
    'ipv4': fields.IPv4(),
    'ipv6': fields.IPv6(),
    'url': fields.Url(),
}


def _make_field_for_schema(schema: dict) -> Field:
    if schema.get('format'):
        field = FIELDS_VIA_FORMATS[schema['format']]
    else:
        if schema['_type'] == 'array':
            nested_field = FIELDS_VIA_TYPES[schema['items']['_type']]
            field = fields.List(nested_field)
        else:
            field = FIELDS_VIA_TYPES[schema['_type']]

        validators = []

        if schema['_type'] in ['string']:
            validators.append(
                validate.Length(min=schema.get('minLength'), max=schema.get('maxLength'))
            )

        if schema['_type'] in ['string']:
            validators.append(validate.Regexp(schema.get('pattern', r'^.*$')))

        if schema['_type'] in ['integer', 'number']:
            validators.append(validate.Range(min=schema.get('minimum'), max=schema.get('maximum')))

        field.validators = validators

    field.required = schema.get('required', False)

    return field


def _make_parameter_schema(keys: Iterable, parameters: dict) -> type:
    schema_fields = {}
    for key in keys:
        try:
            schema = parameters[key]['schema']
        except KeyError:
            raise FlaskFirstValidation(f'Parameter <{key}> not found in specification!')

        field = _make_field_for_schema(schema)
        schema_fields[key] = field

    marshmallow_schema = Schema.from_dict(schema_fields)

    return marshmallow_schema


def _make_json_schema(json: dict, parameters: dict) -> type:
    json_keys = set(json)
    required_keys = set(parameters['required'])
    all_keys_obj = set(parameters['properties'])

    # Check required keys.
    if required_keys.difference(json_keys):
        raise FlaskFirstValidation(f'Required keys <{required_keys}> not in request <{json}>')

    # Check 'additionalProperties'.
    if not parameters['additionalProperties']:
        non_exist_keys = json_keys.difference(all_keys_obj)
        if non_exist_keys:
            raise FlaskFirstValidation(f'Keys <{non_exist_keys}> not in scheme <{all_keys_obj}>.')

    schema_fields = {}
    for key in json:
        schema = parameters['properties'][key]
        field = _make_field_for_schema(schema)
        schema_fields[key] = field

    marshmallow_schema = Schema.from_dict(schema_fields)

    return marshmallow_schema


def validate_parameters(values: dict, parameters: dict) -> dict:
    schema = _make_parameter_schema(values.keys(), parameters)
    try:
        return schema().load(values)
    except MarshmallowValidationError as e:
        raise FlaskFirstPathParameterValidation(e)


def validate_json(json: [dict, list], schema: dict) -> None:
    if isinstance(json, dict):
        new_schema = _make_json_schema(json, schema)
        try:
            new_schema().load(json)
        except MarshmallowValidationError as e:
            raise FlaskFirstValidation(e)

    if isinstance(json, list):
        for item in json:
            new_schema = _make_json_schema(item, schema['items']['items'])
            try:
                new_schema().load(item)
            except MarshmallowValidationError as e:
                raise FlaskFirstValidation(e)
