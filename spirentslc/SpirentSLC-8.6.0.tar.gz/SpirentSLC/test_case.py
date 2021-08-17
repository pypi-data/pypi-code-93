# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

"""Test case file class and necessary tools."""

from .internal.protocol import Type

from .session_response import SessionActionResponse
from .session_profile import _to_property_group
from .identity import UriIdentity
from .python_name import python_name

_KNOWN_CALL_ARGS = {'properties', 'testbed'}

def _to_call_args(kwargs):
    """Prepare the given argument dict to be used as procedure call arguments

    Arguments:
    kwargs -- dict or arguments

    Returns a new dict, ready to be passed as arguments to _call_procedure()
    """
    ret = {}
    parameters = {}
    for key, value in kwargs.items():
        if key in _KNOWN_CALL_ARGS:
            ret[key] = value
        else:
            parameters[key] = value
    ret['parameters'] = parameters
    return ret


def _to_params_list(parameters):
    """Converts the given parameters to a list of Type.Param.

    Arguments:
    parameters -- a dict with keys being parameter names and values being either parameter values, or
                  a dict with two keys: 'value', which is the parameter value, and 'children', which is a dict
                  of the same type as above. Example:
                  {'param1': 'value1', 'param2': {'value': 'value2', 'children': {'child_param1': 'value3'}}}
                  Can be None.

    Returns a list of Type.Param, or None.
    """

    if not parameters:
        return None

    ret = []

    for key, value in parameters.items():
        param = Type.Param()
        param.name = key
        param.value = str(value)

        ret.append(param)

    return ret

class TestCase(UriIdentity):
    """Test case file representation.
    """
    def __init__(self, protocol_socket, uri):
        """Initiates a new test case.

        Arguments:
        uri -- test case file URI, e.g. project://my_project/test_cases/test_case.fftc
        """

        UriIdentity.__init__(self, uri)
        self._protosock = protocol_socket

        self._procedures = None
        self._description = None

    def __str__(self):
        """ Return a URI """
        return self._uri

    def __dir__(self):
        """ return a list of methods available to project"""
        return super.__dir__(self) + list(self.list().keys())

    def __getitem__(self, key):
        self._update_test_case_list()
        return self._procedures[key]

    def __getattr__(self, key):
        ret = self[key]
        if not ret:
            raise AttributeError(key)
        return ret

    def _call_procedure(self, procedure_name, parameters=None, testbed=None, properties=None):
        procedure_uri = '{}#{}'.format(self.uri, procedure_name)
        result = self._protosock.test_case_procedure(procedure_uri,
                                                     parameters=_to_params_list(parameters),
                                                     testbed=testbed,
                                                     property_group=_to_property_group(properties))
        return SessionActionResponse(result)

    def _update_test_case_list(self):
        if not self._procedures:
            self._procedures = dict()
            self._description = dict()
            resp = self._protosock.query_test_case(self._uri)
            for procedure in resp.procedures:
                name = python_name(procedure.name)
                self._procedures[name] = lambda *args, **kwargs: self._call_procedure(procedure.name, **_to_call_args(kwargs))
                self._description[name] = dict((arg.name, arg.description) for arg in procedure.args)

    def list(self):
        """Returns all procedures available on a given test case"""
        self._update_test_case_list()
        return self._description
