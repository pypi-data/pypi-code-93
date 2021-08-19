"""
Command line tools
"""
import json

import click


def add_common_options(options):
    """
    Convenience decorator for shared options (i.e. options that are common across commands)
    """

    def _add_common_options(function):
        for option in options[::-1]:
            function = option(function)
        return function

    return _add_common_options


def validate_json_callback(ctx_, param_, value):
    """
    Convenience callback to help validate (and load) JSON in option strings
    """
    try:
        return json.loads(value)
    except json.decoder.JSONDecodeError as err:
        raise click.BadParameter(f'Malformed JSON - {err}')
    except TypeError:
        return value
