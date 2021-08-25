from __future__ import annotations
from os import getcwd, path
from traceback import extract_tb, print_exception
from flask import Response, jsonify, current_app
from werkzeug.exceptions import HTTPException
from jsonclasses.exceptions import (ObjectNotFoundException,
                                    ValidationException,
                                    UniqueConstraintException,
                                    UnauthorizedActionException)
from .remove_none import remove_none


def exception_handler(exception: Exception) -> tuple[Response, int]:
    code = exception.code if isinstance(exception, HTTPException) else 500
    code = 404 if isinstance(exception, ObjectNotFoundException) else code
    code = 400 if isinstance(exception, ValidationException) else code
    code = 400 if isinstance(exception, UniqueConstraintException) else code
    code = 401 if isinstance(exception, UnauthorizedActionException) else code
    if current_app.debug:
        if code == 500:
            print_exception(etype=type[exception], value=exception, tb=exception.__traceback__)
            return jsonify({
                'error': remove_none({
                    'type': 'Internal Server Error',
                    'message': 'There is an internal server error.',
                    'error_type': exception.__class__.__name__,
                    'error_message': str(exception),
                    'fields': (exception.keypath_messages
                               if (isinstance(exception, ValidationException) or isinstance(exception, UniqueConstraintException))
                               else None),
                    'traceback': [f'file {path.relpath(f.filename, getcwd())}:{f.lineno} in {f.name}' for f in extract_tb(exception.__traceback__)],  # noqa: E501
                })
            }), code
        else:
            return jsonify({
                'error': remove_none({
                    'type': exception.__class__.__name__,
                    'message': str(exception),
                    'fields': (exception.keypath_messages
                               if (isinstance(exception, ValidationException) or isinstance(exception, UniqueConstraintException))
                               else None),
                    'traceback': [f'file {path.relpath(f.filename, getcwd())}:{f.lineno} in {f.name}' for f in extract_tb(exception.__traceback__)],  # noqa: E501
                })
            }), code
    else:
        if code == 500:
            print_exception(etype=type[exception], value=exception, tb=exception.__traceback__)
            return jsonify({
                'error': remove_none({
                    'type': 'Internal Server Error',
                    'message': 'There is an internal server error.'
                })
            }), code
        else:
            return jsonify({
                'error': remove_none({
                    'type': exception.__class__.__name__,
                    'message': str(exception),
                    'fields': (exception.keypath_messages
                               if (isinstance(exception, ValidationException) or isinstance(exception, UniqueConstraintException))
                               else None)
                })
            }), code
