'''
======================================================================
Generic wrapper for different validators
----------------------------------------------------------------------
'''
import json
import jsonschema
from importlib import import_module

from carte_blanche_utils.find_path.find_path import walk
walk()

errors = import_module('carte_blanche_utils.validators.__errors__')


class Validator(object):
    """Abstraction for JSON schema validation"""
    def __init__(self, schema):
        super(Validator, self).__init__()
        self.schema = self.set_schema(schema)

    def set_schema(self, schema_path):

        if isinstance(schema_path, str):
            try:
                with open(schema_path) as sp:
                    return json.load(sp)
            except Exception as exception:

                vaildator_exception = errors.SchemaException({'exception': exception})

                raise vaildator_exception
        elif isinstance(schema_path, dict):
            return schema_path

    def validate(self, input):
        try:
            jsonschema.validate(input, self.schema)
            return True

        except jsonschema.exceptions.ValidationError as validation_error:
            ve_string = str(validation_error.message)

            vaildator_exception = errors.ValidationException({'exception': ve_string})

            raise vaildator_exception


if __name__ == '__main__':
    schema_path = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            }
        },
        "additionalProperties": False
    }
    validator = Validator(schema=schema_path)

    input_ = {'name': 'foo'}

    try:
        print(validator.validate(input_))
    except errors.ValidationException as exception:
        print(exception.exception)
