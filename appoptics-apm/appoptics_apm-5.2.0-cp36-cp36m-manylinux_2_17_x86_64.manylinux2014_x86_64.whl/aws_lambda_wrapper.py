#    Copyright 2021 SolarWinds, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" AppOptics APM instrumentation for serverless AWS Lambda applications.
"""
import importlib
import logging
import os

import appoptics_apm

logger = logging.getLogger(__name__)


def wrap_lambda_handler():
    """Wraps the original AWS lambda function.
    The name of the lambda function is expected to be provided in an environment variable called
    'APPOPTICS_WRAP_LAMBDA_HANDLER'. The variable is expected to specify a lambda function handler in the form
    'module.function_handler'. If this variable is not set, or if the value of the variable does not specify a Python
    callable, the agent will raise an Exception.
    """
    if not appoptics_apm.is_lambda():
        return None
    error_msg_help = 'Please specify your original Lambda function in the form `module.function_handler`.'
    envv_name = 'APPOPTICS_WRAP_LAMBDA_HANDLER'
    envv_val = os.environ.get(envv_name, '')
    if envv_val == '':
        raise Exception('{} environment variable is not set. '.format(envv_name) + error_msg_help)

    target = envv_val.rsplit('.', 1)
    if len(target) < 2:
        raise Exception('Invalid {}: {}. '.format(envv_name, envv_val) + error_msg_help)

    try:
        target_module = importlib.import_module(target[0])
        target_handler = getattr(target_module, target[1])
    except (ModuleNotFoundError, AttributeError) as e:
        raise Exception('Invalid {}: {}, {}. '.format(envv_name, envv_val, e) + error_msg_help)

    if not callable(target_handler):
        raise Exception(
            'Invalid function handler provided {}: {}. The handler {} is not callable. '.format(
                envv_name, envv_val, target_handler) + error_msg_help)

    # We cannot directly use `import appoptics_apm.loader` here, as this would force the name `appoptics_apm` bound
    # to be a local variable. As a result, an `UnboundLocalError` would occur when `appoptics_apm.is_lambda()` is called
    # above.
    importlib.import_module('appoptics_apm.loader').load_inst_modules()
    return target_handler


target_handler = wrap_lambda_handler()


class LambdaEvent:
    """Provides classes to classify an incoming Lambda event."""
    @classmethod
    def create(cls, event):
        """Returns an object of one of the inheriting types of _ApiGatewayEvent or None if no suitable class could be
        associated with the provided event.

        The class can map incoming Lambda events resulting from an invocation through AWS Lambda integrations via HTTP
        API and REST API, but not Websocket API.
        """
        if cls._ApiGatewayEvent.qualifies(event):
            if cls._RestApiGatewayEvent.qualifies(event):
                logger.debug(
                    "Incoming Lambda event %s will be mapped to %s." % (event, cls._RestApiGatewayEvent.__name__))
                return cls._RestApiGatewayEvent(event)
            if cls._HttpApiV2GatewayEvent.qualifies(event):
                logger.debug(
                    "Incoming Lambda event %s will be mapped to %s." % (event, cls._HttpApiV2GatewayEvent.__name__))
                return cls._HttpApiV2GatewayEvent(event)
        return None

    class _ApiGatewayEvent:
        """Base class for Lambda events received from an API Gateway invocation.

        This class and all its inheriting classes should only be instantiated through LambdaEvent.create()."""
        def __init__(self, event):
            self.raw_evt = event
            self.headers = {}
            # The HTTP header dictionary must be checked in a case-insensitive manner. To avoid iterating over the dict
            # multiple times, we convert all keys to lower-case first. Note that we generally do not expect the same
            # keys with different casing in the HTTP header, and the conversion might thus loose information as multiple
            # keys would be mapped to the same lower-case key.
            for k, v in event['headers'].items():
                self.headers[k.lower()] = v

            self.x_trace = self.headers.get('x-trace', None)
            self.host = self.headers.get('host', None)

        @staticmethod
        def qualifies(event):
            """The provided event must satisfy the following criteria:
            (1) event must be a dictionary
            (2) event must have the key 'headers' and the value of events['headers'] must be a dictionary
            (3) headers must have a key 'Host' or 'host'
            """
            try:
                if isinstance(event, dict) and isinstance(event['headers'], dict) and ('Host' in event['headers']
                                                                                       or 'host' in event['headers']):
                    return True
            except KeyError:
                pass
            return False

        @property
        def stage(self):
            """Returns the API Gateway deployment stage."""
            try:
                return self.raw_evt['requestContext']['stage']
            except (TypeError, KeyError):
                return None

        @property
        def x_forwarded_for(self):
            """Returns X-Forwarded-For from HTTP header."""
            return self.headers.get('x-forwarded-for', None)

        @property
        def x_forwarded_proto(self):
            """Returns X-Forwarded-Proto from HTTP header."""
            return self.headers.get('x-forwarded-proto', None)

        @property
        def x_forwarded_port(self):
            """Returns X-Forwarded-Port from HTTP header."""
            return self.headers.get('x-forwarded-port', None)

    class _RestApiGatewayEvent(_ApiGatewayEvent):
        """Class for Lambda events received through an invocation through either RestApi or HttpApi V1."""
        @staticmethod
        def qualifies(event):
            """The provided event must satisfy the following criteria, otherwise None will be returned:
                (1) event has a key `httpMethod`
                (2) event has a key `resource`
            """
            # Technically, this should also call qualify of the base class. However, this check is omitted for
            # performance reasons (i.e. to avoid multiple invocations of _ApiGatewayEvent.qualifies on the same event)
            if 'httpMethod' in event and 'resource' in event:
                return True
            return False

        @property
        def path(self):
            """Returns the HTTP path."""
            return self.raw_evt['resource']

        @property
        def method(self):
            """Returns the HTTP method."""
            return self.raw_evt['httpMethod']

        @property
        def resource_id(self):
            """Returns the API Gateway resource ID."""
            try:
                return self.raw_evt['requestContext']['resourceId']
            except (TypeError, KeyError):
                return None

    class _HttpApiV2GatewayEvent(_ApiGatewayEvent):
        """Class for Lambda events received through an invocation through HttpApi V2."""
        @staticmethod
        def qualifies(event):
            """The provided event must satisfy the following criteria, otherwise None will be returned:
                (1) event has a key `requestContext` and the value of event['requestContext'] itself is a dictionary
                    which has a key `http`
                (2) event['requestContext']['http'] is a dictionary
                (3) event['requestContext']['http'] has a key 'path' and 'method'
            """
            # Technically, this should also call qualify of the base class. However, this check is omitted for
            # performance reasons (i.e. to avoid multiple invocations of _ApiGatewayEvent.qualifies on the same event)
            try:
                if not isinstance(event['requestContext'], dict):
                    raise TypeError
                if 'method' in event['requestContext']['http'] and 'path' in event['requestContext']['http']:
                    return True
            except (TypeError, KeyError):
                pass
            return False

        @property
        def path(self):
            """Returns the HTTP path."""
            # HTTP API V2 events include the stage in path, we need to remove it. However, stage is not guaranteed to
            # exist, thus we only strip if it has been populated.
            stage = self.stage
            if stage:
                return self.raw_evt['requestContext']['http']['path'].replace('/{}'.format(stage), '', 1)
            else:
                return self.raw_evt['requestContext']['http']['path']

        @property
        def method(self):
            """Returns the HTTP method."""
            return self.raw_evt['requestContext']['http']['method']

        @property
        def resource_id(self):
            """Returns the API Gateway resource ID."""
            try:
                return self.raw_evt['route_key']
            except KeyError:
                return None


# track invocation count
invocation_count = 0


def handler(event, context):
    """This function is the wrapping function which instruments the original Lambda function specified in the
    target_handler"""
    if not appoptics_apm.util.ready():
        # if the agent is not yet ready (e.g. when it is disabled) we just directly call the original function
        return target_handler(event, context)

    global invocation_count
    invocation_count += 1

    parsed_event = LambdaEvent.create(event)

    layer = 'aws_lambda_python'
    try:
        memory_limit_in_mb = int(context.memory_limit_in_mb)
    except Exception:
        memory_limit_in_mb = 0
    appoptics_apm.start_trace(
        layer,
        xtr=parsed_event.x_trace if parsed_event else None,
        keys={
            'Spec': 'aws-lambda:ws' if parsed_event else 'aws-lambda',
            'FunctionVersion': context.function_version,
            'InvokedFunctionARN': context.invoked_function_arn,
            'AWSRequestID': context.aws_request_id,
            'AWSRegion': os.environ.get('AWS_REGION'),
            'InvocationCount': invocation_count,
            'MemoryLimitInMB': memory_limit_in_mb,
            'LogStreamName': context.log_stream_name,
        })
    appoptics_apm.set_transaction_name(
        '.'.join([parsed_event.method, context.function_name]) if parsed_event else context.function_name)

    result = None
    has_error = False
    try:
        result = target_handler(event, context)
        if isinstance(result, Exception):
            # The instrumented Lambda function can return an Exception object which we need to log.
            has_error = True
            try:
                appoptics_apm.log_error(result.__class__.__name__, str(result), backtrace=result.__traceback__)
            except Exception as e:
                logger.debug("Could not log Exception object returned from instrumented Lambda function: %s" % e)
        else:
            # If no Exception object is returned, the instrumented Lambda function can still indicate an error by
            # setting the statusCode in the response object appropriately
            try:
                status_code = result['statusCode']
                if bool(status_code > 499) and bool(status_code < 600):
                    has_error = True
            except (KeyError, TypeError):
                pass
    except Exception:
        appoptics_apm.log_exception()
        has_error = True
        raise
    finally:
        if parsed_event:
            kvs = {
                'HTTP-Host': parsed_event.host,
                'URL': parsed_event.path,
                'HTTPMethod': parsed_event.method,
            }
            resourceId = parsed_event.resource_id
            if resourceId:
                kvs['APIGatewayResourceID'] = resourceId
            stage = parsed_event.stage
            if stage:
                kvs['APIGatewayStage'] = stage
            x_forwarded_for = parsed_event.x_forwarded_for
            if x_forwarded_for:
                kvs['Forwarded-For'] = x_forwarded_for
            x_forwarded_proto = parsed_event.x_forwarded_proto
            if x_forwarded_proto:
                kvs['Forwarded-Proto'] = x_forwarded_proto
            x_forwarded_port = parsed_event.x_forwarded_port
            if x_forwarded_port:
                kvs['Forwarded-Port'] = x_forwarded_port
            try:
                kvs['Status'] = result['statusCode']
            except (KeyError, TypeError):
                pass
        else:
            kvs = None
        outgoing_xtr_val = appoptics_apm.end_trace(layer, keys=kvs, has_error=has_error)

    if parsed_event and parsed_event.x_trace and outgoing_xtr_val:
        try:
            if 'headers' not in result:
                result['headers'] = {}
            result['headers']['X-Trace'] = outgoing_xtr_val
        except TypeError:
            logger.debug(
                "Failed to inject x-trace into response object of type %s despite existing incoming x-trace." %
                type(result))

    return result
