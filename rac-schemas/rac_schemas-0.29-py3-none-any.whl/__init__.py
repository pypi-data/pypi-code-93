import json
import jsonschema
import re
from pathlib import Path

from .exceptions import ValidationError

schemas_dir = Path(__file__).parent / "schemas"


def handle_schema_filename(filename):
    extension = filename.split(".")[-1]
    if extension != "json":
        if len(filename.split(".")) > 1:
            filename = filename[:-len(extension)] + ".json"
        else:
            filename = filename + ".json"
    return filename


def is_date(value, instance):
    if not isinstance(instance, str):
        return False
    if instance.count("-") == 2:
        pattern = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
    elif instance.count("-") == 1:
        pattern = re.compile("^[0-9]{4}-[0-9]{2}$")
    else:
        pattern = re.compile("^[0-9]{4}$")
    return pattern.match(instance)


def is_valid(data, schema_name):
    """Main method to validate data against a JSON schema.

    Args:
        data (dict): data to be validated.
        schema_name (str): the schema against which the data should be validated.

    Raises:
        TypeError: if data is not a dict
        FileNotFoundError: if a schema file cannot be found
        rac_schemas.exceptions.ValidationError: if the validation fails
    """
    if not isinstance(data, dict):
        raise TypeError(
            "Data to be validated must be a dict, got {} instead".format(
                type(data)))
    filename = handle_schema_filename(schema_name)
    with open(Path(schemas_dir) / "base.json", "r") as bf:
        base_schema = json.load(bf)
        with open(Path(schemas_dir) / filename, "r") as sf:
            object_schema = json.load(sf)
            resolver = jsonschema.RefResolver.from_schema(base_schema)
            type_checker = jsonschema.Draft7Validator.TYPE_CHECKER.redefine(
                "date", is_date)
            validators = jsonschema.Draft7Validator.VALIDATORS
            validators["date"] = is_date
            CustomValidator = jsonschema.validators.extend(
                jsonschema.Draft7Validator,
                type_checker=type_checker,
                validators=validators)
            validator = CustomValidator(object_schema, resolver=resolver)
            try:
                validator.validate(data)
            except jsonschema.exceptions.ValidationError as e:
                raise ValidationError(e)
            return True
