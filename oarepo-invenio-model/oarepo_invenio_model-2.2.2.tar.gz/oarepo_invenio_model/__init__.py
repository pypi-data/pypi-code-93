from flask import current_app
from invenio_jsonschemas import current_jsonschemas
from jsonschema import Draft7Validator

from .version import __version__


class AllOfDraft7Validator(Draft7Validator):
    def __init__(self, schema, *args, **kwargs):
        if schema.get('$id') != 'http://json-schema.org/draft-07/schema#':
            # replace $ref recursively
            schema = current_app.extensions['invenio-records'].replace_refs(schema)
            # resolve allOfs
            schema = current_jsonschemas.resolver_cls(schema)
        super().__init__(schema, *args, **kwargs)


class InheritedSchemaRecordMixin:
    def validate(self, **kwargs):
        return super().validate(**{
            **kwargs,
            'validator': AllOfDraft7Validator
        })
