# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

"""Session profile class and necessary tools."""

import six

from .identity import UriIdentity
from .internal.protocol import Type, create_action_message
from .internal.response_storage import ResponseStorage
from .resources import ParameterFile, ResponseMapFile
from .session_response import SessionActionResponse, response_step_compare
from .exception import SLCError
from functools import cmp_to_key

_KNOWN_INVOKE_ARGS = ['response_map', 'parameters', 'command', 'properties']


def _to_invoke_args(kwargs):
    """Prepares the given arguments dict for invoking as action arguments.

    Arguments:
    kwargs -- dict or arguments

    Returns a new dict, ready to be passed as arguments to invoke_command().
    """

    ret = {}
    params = {}

    for key, value in kwargs.items():
        if key in _KNOWN_INVOKE_ARGS:
            ret[key] = value
        else:
            params[key] = value

    if params:
        ret['parameters'] = params
    return ret


def _to_list(arg):
    """If arg is a list, returns it. If it's None, returns None. Otherwise, returns a one-element list with arg."""

    if arg is None:
        return None

    if isinstance(arg, list):
        return arg

    return [arg, ]


def _to_requirements(agent_requirements):
    """Converts the given argument into a list of Type.Requirement.

    Arguments:
    agent_requirements -- dict of the format {'requirement_name': 'requirement_value'}. Can be None.

    Returns a list of Type.Requirement, or None.
    """

    if not agent_requirements:
        return None

    ret = []
    for key, value in agent_requirements.items():
        req = Type.Requirement()
        req.name = key
        req.value = value
        ret.append(req)

    return ret


def _to_property_group(properties):
    """Converts the given properties dict into Type.PropertiesGroup.

    Arguments:
        properties -- a dictionary with keys being property names (strings)
                      and value being property values (strings or nested properties group).
                      Can be None.

    Returns Type.PropertiesGroup, or None.
    """

    if not properties:
        return None

    ret = Type.PropertiesGroup()
    ret.name = ''

    for key, value in properties.items():
        if isinstance(value, six.string_types):
            # prop = Type.Property()
            prop = ret.properties.add()
            prop.name = key
            prop.value = value
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, six.string_types):
                    child = ret.properties.add()
                    child.name = key
                    child.value = item
                else:
                    child = _to_property_group(item)
                    child.name = key
                    ret.children.extend([child])
        else:
            child = _to_property_group(value)
            if child:
                child.name = key
                ret.children.extend([child])

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
        if isinstance(value, ParameterFile):
            param.value = value.uri
        elif isinstance(value, ResponseMapFile):
            param.value = value.uri
        elif isinstance(value, dict):
            param.value = str(value['value'])
            if 'children' in value:
                param.parameters.extend(_to_params_list(value['children']))
        else:
            param.value = str(value)

        ret.append(param)

    return ret


class SessionProfileInformation(object):
    """ A details object to specify agent parameters"""

    def __init__(self, agent_name, agent_id, protocol_version, agent_type, capabilities):
        """Initialise a agent parameters object
        agent_name -- a name of agent.
        agent_id -- a identifier of agent.
        protocol_version -- a version of protocol used
        """
        self.name = agent_id
        self.agent_name = agent_name
        self.protocol_version = protocol_version
        self.agent_type = agent_type
        self.capabilities = {}

        for cap in capabilities:
            cur_cap = self.capabilities.get(cap.name)
            if cur_cap is None:
                cur_cap = cap.value
            elif type(cur_cap) == list:
                cur_cap.append(cap.value)
            else:
                cur_cap = [cur_cap, cap.value]
            self.capabilities[cap.name] = cur_cap

    def __str__(self):
        return str(vars(self))


class SessionProfile(UriIdentity):
    """Session profile representation.

    Allows to open session.

    Recommended way to use this class is as follows:

        with proj.session_name_ffsp.open() as s1:
            # invoke a 'init_routes' quickcall
            response = s1.init_routes(interface='Eth2/2', timeout=150)

            # other syntax of same command
            response = s1.init_routes('-interface Eth2/2 -timeout 150')

            # invoke a command:
            response = s1.command('command', response_map=proj.response_map_ffrm)

    Constructing instances of this class directly may be handy for testing, but generally is discouraged.

    Properties:
    agent -- agent information
    """

    def __init__(self, protocol_socket, agent_type, uri, dependencies=None):
        """Initiates a new session profile.

        Arguments:
        protocol_socket -- an instance of ProtocolSocket. It must be connected by the time open() is called.
        uri -- session profile URI, e.g. project://my_project/session_profiles/slc_test.ffsp
        dependencies -- session profile dependencies,
                        e.g. ['file:///home/dsavenko/itest/itest/dev/src/non-plugins/SpirentSLC/my_project.itar']

        """
        UriIdentity.__init__(self, uri)
        self._protosock = protocol_socket
        self._deps = dependencies

        self.agent = SessionProfileInformation(self._protosock.agent_name, self._protosock.agent_id,
                                               self._protosock.protocol_version, agent_type,
                                               self._protosock.capabilities)

    def open(self, parameter_file=None, agent_requirements=None, properties=None, response_map_lib=None,
             response_cache_size=10 * 1024 * 1024, **kwargs):
        """Opens the session.

        Arguments:
        parameter_file -- a single parameter file (URI), or a list of parameter files.
        agent_requirements -- dict of the format {'requirement_name': 'requirement_value'}
        properties -- a dictionary with keys being property names (strings)
                      and value being property values (strings or nested properties group).

        Raises SLCError, if socket is close. May raise socket.error.
        """
        if not self._protosock.is_open():
            raise SLCError('SLC connection is closed')

        return SlcSession(self._protosock, self.agent, self.uri, self._deps, response_cache_size, parameter_file,
                          agent_requirements, properties, response_map_lib, **kwargs)

    def list(self, qc_name=None):
        """Returns all QuickCalls available on a given session profile"""

        if qc_name:
            resp = self._protosock.query_session(self._uri, qc_name)
            qc = resp.quickCall[0]
            return dict((arg.name, arg.description) for arg in qc.args)

        quickcalls = dict()
        resp = self._protosock.query_session(self._uri)
        for qc in resp.quickCall:
            quickcalls[qc.name] = dict((arg.name, arg.description) for arg in qc.args)

        return quickcalls

    def __dir__(self):
        """ return a list of methods available to session profile"""
        return dir(super) + list(self.list().keys())

    def __getattr__(self, key):
        ret = self[key]
        if not ret:
            raise AttributeError(key)
        return ret


class SlcSession(UriIdentity):

    def __init__(self, protocol_socket, agent_type, uri, dependencies=None, response_cache_size=10 * 1024 * 1024,
                 parameter_file=None, agent_requirements=None, properties=None, response_map_lib=None, **kwargs):
        """Initiates a new session.

        Arguments:
        protocol_socket -- an instance of ProtocolSocket. It must be connected by the time open() is called.
        uri -- session profile URI, e.g. project://my_project/session_profiles/slc_test.ffsp
        dependencies -- session profile dependencies,
                        e.g. ['file:///home/dsavenko/itest/itest/dev/src/non-plugins/SpirentSLC/my_project.itar']

        """
        UriIdentity.__init__(self, uri)
        self._protosock = protocol_socket
        self._deps = dependencies

        self.agent = SessionProfileInformation(self._protosock.agent_name, self._protosock.agent_id,
                                               self._protosock.protocol_version, agent_type,
                                               self._protosock.capabilities)
        self.session_id = None
        self.open_response = None
        self._response_listener = SessionActionListener()
        self._response_storage = ResponseStorage(response_cache_size) if response_cache_size > 0 else None
        self._open(parameter_file, agent_requirements, properties, response_map_lib, **kwargs)

    def _open(self, parameter_file=None, agent_requirements=None, properties=None, response_map_lib=None, **kwargs):
        """Opens the session.

        Arguments:
        parameter_file -- a single parameter file (URI), or a list of parameter files.
        agent_requirements -- dict of the format {'requirement_name': 'requirement_value'}
        properties -- a dictionary with keys being property names (strings)
                      and value being property values (strings or nested properties group).

        Raises ValueError, if the session is already opened. May raise socket.error.
        """

        if self.session_id:
            raise ValueError('Session already opened with id=' + self.session_id)

        if properties is None:
            properties = {}
            for key, value in kwargs.items():
                properties[key] = str(value)

        # Convert parameter file to uri
        if isinstance(parameter_file, ParameterFile):
            parameter_file = parameter_file.uri

        # Convert project to uri
        if isinstance(response_map_lib, UriIdentity):
            response_map_lib = response_map_lib.uri

        if response_map_lib != None and not isinstance(response_map_lib, six.string_types):
            raise ValueError('Wrong response_map_lib value is passed. Should be URI' + str(response_map_lib))

        rsp = self._protosock.start_session(self._uri,
                                            dependencies=self._deps,
                                            param_files=_to_list(parameter_file),
                                            requirements=_to_requirements(agent_requirements),
                                            property_group=_to_property_group(properties),
                                            resp_map_lib=response_map_lib)
        self.session_id = rsp.sessionId
        self.open_response = SessionActionResponse(rsp)
        return self

    def close(self):
        """Closes the session.

        Does nothing, if the session has not been opened yet. May raise socket.error.
        """
        session_id = self.session_id
        self.session_id = None
        self.open_response = None
        if self._response_storage:
            self._response_storage.close()
        if session_id:
            self._protosock.close_session(session_id)

    def is_open(self):
        """ Return if session is stil opened or not"""
        return self.session_id != None and self._protosock != None and self._protosock.is_open()

    def session_properties(self):
        """Query a running session for all session properties"""
        return self.invoke_action('session_properties')

    def session_attribute(self, attr_name, default=None):
        """Query a running session for all session attributes"""
        return self.invoke_action('__session_attributes__' + attr_name, default)

    def step_properties(self, action, command=None, parameters=None, properties=None, response_map=None):
        """Query a running session for step actin properties"""
        return self.invoke_action('step_properties_' + action, command=command, parameters=parameters,
                                  properties=properties, response_map=response_map)

    def invoke_action(self, action, command=None, parameters=None, response_map=None, properties=None):
        """Invokes session action or quickcall.

        Generally, you do not need to use this method directly. E.g. instead of calling

            ssh_session.invoke_action('command', 'ls')

        you can just call

            ssh_session.command('ls')

        For Quickcalls, instead of calling

            session.invoke_action('my_quickcall', parameters={'param1': 'value1', 'param2': 123})

        you can just call

            session.my_quickcall(param1='value1', param2=123)

        Arguments:
        action -- session action or QuickCall name. Depends on a session.
                  Widely used actions: 'close' to close the session, 'command' to execute a specific session command.
        command -- command to execute
        parameters -- a dict with keys being parameter names and values being either parameter values, or
                      a dict with two keys: 'value', which is the parameter value, and 'children', which is a dict
                      of the same type as above. Example:
                      {'param1': 'value1', 'param2': {'value': 'value2', 'children': {'child_param1': 'value3'}}}
        properties -- a dictionary with keys being property names (strings)
                      and value being property values (strings or nested properties group).
                      A {'param_group.param': 'value1'} syntax could be used to update nested values.
        responseMap -- URI of the response map file to use.

        Returns action response. Console calling is equivalent to response._text.
        Raises ValueError, if the session is not opened. May raise socket.error
        """

        if not self.session_id:
            raise ValueError('Session is not opened')

        # Convert response map to it uri
        if isinstance(response_map, ResponseMapFile):
            response_map = response_map.uri

        def is_nested_response(msg):
            return msg.type == msg.SESSION_ACTION_RESPONSE and \
                   msg.sessionActionResponse.HasField("nestedActionDetails")

        def is_execution_issue(msg):
            return msg.type == msg.EXECUTION_ISSUE_MESSAGE

        def parent_id(step_id):
            id_parts = step_id.split('.')
            result = '.'.join(id_parts[:-1])
            return result if '.' in result else ''

        context = StepExecutionContext(self.session_id, self._protosock)
        root_builder = _ResponseBuilder(None)
        collected_steps = {root_builder.id: root_builder}

        orphaned_issues = {}

        def nested_step_collector(msg):
            if not is_nested_response(msg):
                # Check if it is execution_issue and collect it
                if is_execution_issue(msg):
                    msg = msg.executionIssueMessage
                    step_id = msg.stepId
                    if step_id == '':
                        root_builder.add_issue(msg)
                    elif step_id in collected_steps and isinstance(collected_steps[step_id], _ResponseBuilder):
                        # step is completed and step is under construction
                        builder = collected_steps[step_id]
                        builder.add_issue(msg)
                    else:
                        if step_id in orphaned_issues:
                            orphaned_issues[step_id].append(msg)
                        else:
                            orphaned_issues[step_id] = [msg]
                return
            response_message = msg.sessionActionResponse
            nested_details = response_message.nestedActionDetails
            step_id = nested_details.stepId
            if step_id == '':
                # 1st step is a Builder, skip it
                return
            if nested_details.status == Type.SessionActionUpdateStatus.Value('STARTED'):
                if step_id not in collected_steps:
                    # we see the step for the first time
                    collected_steps[step_id] = _ResponseBuilder(response_message)
                    self.response_listener.process_start(context, response_message)
                else:
                    # this is just an update of the step that we've already seen
                    builder = collected_steps[step_id]
                    builder.update_response(response_message)
                    self.response_listener.process_update(context, response_message)
            elif step_id in collected_steps and isinstance(collected_steps[step_id], _ResponseBuilder):
                # step is completed and step is under construction
                builder = collected_steps[step_id]
                builder.update_response(response_message)
                response = self._cache(step_id, builder.build())
                collected_steps[step_id] = response
                parent = collected_steps[parent_id(step_id)]
                parent.add_nested(response)
                self.response_listener.process_done(context, response)

                if step_id in orphaned_issues:
                    issues = orphaned_issues.pop(step_id)
                    for issue in issues:
                        builder.add_issue(issue)
            else:
                # step is completed but it wasn't seen before or
                # step is seen before but need to be overwritten
                issues = []
                if step_id in orphaned_issues:
                    issues = orphaned_issues.pop(step_id)
                response = self._cache(step_id, SessionActionResponse(response_message, execution_issues=issues))
                collected_steps[step_id] = response
                parent = collected_steps[parent_id(step_id)]
                parent.add_nested(response)
                self.response_listener.process_done(context, response)

        command = command if (command is None) else str(command)
        params_list = _to_params_list(parameters)
        property_group = _to_property_group

        resp = self._protosock.invoke_action(self.session_id,
                                             action=action,
                                             command=command,
                                             params=params_list,
                                             response_map=response_map,
                                             property_group=property_group(properties),
                                             nested_step_collector=nested_step_collector)

        root_builder.update_response(resp)
        root_builder.update_action(session_id=self.session_id,
                                   action=action,
                                   command=command,
                                   params=params_list,
                                   response_map=response_map,
                                   property_group=property_group(properties))

        return root_builder.build()

    def _cache(self, step_id, response):
        if self._is_caching_disabled():
            return response
        self._response_storage[step_id] = response
        return _CachedSessionResponse(step_id, self._response_storage, response.nested_steps, response._execution_issues)

    def _is_caching_disabled(self):
        return self._response_storage is None

    def list(self, qc_name=None):
        """Returns all QuickCalls available on a given session profile"""

        if qc_name:
            resp = self._protosock.query_session(self._uri, qc_name)
            qc = resp.quickCall[0]
            return dict((arg.name, arg.description) for arg in qc.args)

        quickcalls = dict()
        resp = self._protosock.query_session(self._uri)
        for qc in resp.quickCall:
            quickcalls[qc.name] = dict((arg.name, arg.description) for arg in qc.args)

        return quickcalls

    @property
    def response_listener(self):
        return self._response_listener

    @response_listener.setter
    def response_listener(self, listener):
        if listener is None:
            listener = SessionActionListener()
        self._response_listener = listener

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __dir__(self):
        """ return a list of methods available to project"""
        return dir(super) + list(self.list().keys())

    def __getitem__(self, key):
        return lambda *args, **kwargs: self.invoke_action(key, *args, **_to_invoke_args(kwargs))

    def __getattr__(self, key):
        ret = self[key]
        if not ret:
            raise AttributeError(key)
        return ret


class _ResponseBuilder(object):
    def __init__(self, response_message):
        self._response_message = response_message
        self._execution_issues = []
        self._nested_steps = {}

    def add_nested(self, response):
        self._nested_steps[response.id] = response

    def add_issue(self, issue):
        self._execution_issues.append(issue)

    def update_response(self, response_message):
        self._response_message = response_message

    def update_action(self, session_id, action, command=None, params=None, response_map=None, property_group=None):

        message = create_action_message(session_id=session_id,
                                        action=action,
                                        command=command,
                                        params=params,
                                        response_map=response_map,
                                        property_group=property_group)

        self._response_message.nestedActionDetails.action.CopyFrom(message)

    @property
    def id(self):
        if self._response_message is None:
            return ''
        return self._response_message.nestedActionDetails.stepId

    def build(self):
        built_steps = self._nested_steps.values()
        nested_value = sorted(built_steps, key=cmp_to_key(response_step_compare))
        return SessionActionResponse(self._response_message,
                                     nested_steps=nested_value,
                                     execution_issues=self._execution_issues)

    def __repr__(self):
        if self._response_message is None:
            return 'None'
        return repr(self._response_message.nestedActionDetails.stepId)


class SessionActionListener:
    def __init__(self):
        pass

    def process_start(self, context, response_message):
        pass

    def process_update(self, context, response_message):
        pass

    def process_done(self, context, response):
        pass


class StepExecutionContext(object):
    def __init__(self, session_id, protocol_socket):
        self._session_id = session_id
        self._protocol_socket = protocol_socket

    def cancel(self):
        self._protocol_socket.cancel_step(self._session_id)


class _CachedSessionResponse(object):
    def __init__(self, step_id, cache, nested_steps=(), execution_issues=[]):
        self._step_id = step_id
        self._cache = cache
        self._nested_steps = tuple(nested_steps)
        self._execution_issues = execution_issues

    @property
    def nested_steps(self):
        return self._nested_steps

    @property
    def id(self):
        return self._step_id

    @property
    def issues(self):
        return self._execution_issues


    def add_nested(self, response):
        updated_steps = [step for step in self._nested_steps if step.id != response.id] + [response]
        self._nested_steps = tuple(sorted(updated_steps, key=cmp_to_key(response_step_compare)))

    def add_issue(self, issue):
        self._execution_issues.append(issue)

    def __getattr__(self, key):
        response = self._cache[self._step_id]
        return getattr(response, key)

    def __repr__(self):
        response = self._cache[self._step_id]
        return repr(response)
