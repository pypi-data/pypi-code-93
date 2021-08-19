from datetime import datetime, timedelta
from os import environ
import sys

from warden_sdk.hub import Hub
from warden_sdk.debug import (
   capture_internal_exceptions,
   event_from_exception,
   AnnotatedValue
)
from warden_sdk.utils import (
   logger,
   reraise,
   iteritems
)
from warden_sdk.integrations import Integration

from typing import (
   Optional,
   Any,
   Dict
) 

# Constants
TIMEOUT_WARNING_BUFFER = 1500  # Buffer time required to send timeout warning to Warden
MILLIS_TO_SECONDS = 1000.0

def _wrap_init_error(init_error):
   # type: (F) -> F
   def warden_init_error(*args, **kwargs):
      # type: (*Any, **Any) -> Any

      hub = Hub.current
      integration = hub.get_integration(AwsLambdaIntegration)
      if integration is None:
         return init_error(*args, **kwargs)

      # If an integration is there, a client has to be there.
      client = hub.client  # type: Any

      with capture_internal_exceptions():
         # with hub.configure_scope() as scope:
         #     scope.clear_breadcrumbs()

         exc_info = sys.exc_info()
         if exc_info and all(exc_info):
            warden_event, hint = event_from_exception(
               exc_info,
               client_options=client.options,
               mechanism={"type": "aws_lambda", "handled": False},
            )
            hub.capture_event(warden_event, hint=hint)

      return init_error(*args, **kwargs)

   return warden_init_error  # type: ignore

def _wrap_handler(handler):
   def warden_handler(aws_event, aws_context, *args, **kwargs) -> Any:
        # Per https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html,
        # `event` here is *likely* a dictionary, but also might be a number of
        # other types (str, int, float, None).
        #
        # In some cases, it is a list (if the user is batch-invoking their
        # function, for example), in which case we'll use the first entry as a
        # representative from which to try pulling request data. (Presumably it
        # will be the same for all events in the list, since they're all hitting
        # the lambda in the same request.)

      if isinstance(aws_event, list):
         request_data = aws_event[0]
         batch_size = len(aws_event)
      else:
         request_data = aws_event
         batch_size = 1

      if not isinstance(request_data, dict):
         # If we're not dealing with a dictionary, we won't be able to get
         # headers, path, http method, etc in any case, so it's fine that
         # this is empty
         request_data = {}

      hub = Hub.current
      integration = hub.get_integration(AwsLambdaIntegration)
      if integration is None:
         return handler(aws_event, aws_context, *args, **kwargs)

      # If an integration is there, a client has to be there.
      client = hub.client  # type: Any
      configured_time = aws_context.get_remaining_time_in_millis()

      #   with hub.push_scope() as scope:
            # timeout_thread = None
      with capture_internal_exceptions():
         print(request_data, aws_context, configured_time)
         #  scope.clear_breadcrumbs()
         #  scope.add_event_processor(
         print(_make_request_event_processor(
            request_data, aws_context, configured_time
         ))
         #  )
         #  scope.set_tag(
         #      "aws_region", aws_context.invoked_function_arn.split(":")[3]
         #  )
      #  if batch_size > 1:
      #      scope.set_tag("batch_request", True)
      #      scope.set_tag("batch_size", batch_size)

         # Starting the Timeout thread only if the configured time is greater than Timeout warning
         # buffer and timeout_warning parameter is set True.
         # if (
         #    integration.timeout_warning
         #    and configured_time > TIMEOUT_WARNING_BUFFER
         # ):
         #    waiting_time = (
         #       configured_time - TIMEOUT_WARNING_BUFFER
         #    ) / MILLIS_TO_SECONDS

         #    timeout_thread = TimeoutThread(
         #       waiting_time,
         #       configured_time / MILLIS_TO_SECONDS,
         #    )

         #    # Starting the thread to raise timeout warning exception
         #    timeout_thread.start()

      headers = request_data.get("headers")
      # AWS Service may set an explicit `{headers: None}`, we can't rely on `.get()`'s default.
      if headers is None:
            headers = {}
      # transaction = Transaction.continue_from_headers(
      #     headers, op="serverless.function", name=aws_context.function_name
      # )
      # with hub.start_transaction(
      #     transaction,
      #     custom_sampling_context={
      #         "aws_event": aws_event,
      #         "aws_context": aws_context,
      #     },
      # ):
      try:
         return handler(aws_event, aws_context, *args, **kwargs)
      except Exception:
         exc_info = sys.exc_info()
         warden_event, hint = event_from_exception(
            exc_info,
            client_options=client.options,
            mechanism={"type": "aws_lambda", "handled": False},
         )
         hub.capture_event(warden_event, hint=hint)
         reraise(*exc_info)
         #  finally:
         #      if timeout_thread:
         #          timeout_thread.stop()

   return warden_handler  # type: ignore


def _drain_queue() -> None:
   with capture_internal_exceptions():
      hub = Hub.current
      integration = hub.get_integration(AwsLambdaIntegration)
      if integration is not None:
         # Flush out the event queue before AWS kills the
         # process.
         hub.flush()

class AwsLambdaIntegration(Integration):
    identifier = "aws_lambda"

    def __init__(self, timeout_warning=False):
        # type: (bool) -> None
        self.timeout_warning = timeout_warning

    @staticmethod
    def setup_once():
        # type: () -> None

        lambda_bootstrap = get_lambda_bootstrap()
        if not lambda_bootstrap:
            logger.warning(
                "Not running in AWS Lambda environment, "
                "AwsLambdaIntegration disabled (could not find bootstrap module)"
            )
            return

        if not hasattr(lambda_bootstrap, "handle_event_request"):
            logger.warning(
                "Not running in AWS Lambda environment, "
                "AwsLambdaIntegration disabled (could not find handle_event_request)"
            )
            return

        pre_37 = hasattr(lambda_bootstrap, "handle_http_request")  # Python 3.6 or 2.7

        if pre_37:
            old_handle_event_request = lambda_bootstrap.handle_event_request

            def warden_handle_event_request(request_handler, *args, **kwargs):
                # type: (Any, *Any, **Any) -> Any
                request_handler = _wrap_handler(request_handler)
                return old_handle_event_request(request_handler, *args, **kwargs)

            lambda_bootstrap.handle_event_request = warden_handle_event_request

            old_handle_http_request = lambda_bootstrap.handle_http_request

            def warden_handle_http_request(request_handler, *args, **kwargs):
                # type: (Any, *Any, **Any) -> Any
                request_handler = _wrap_handler(request_handler)
                return old_handle_http_request(request_handler, *args, **kwargs)

            lambda_bootstrap.handle_http_request = warden_handle_http_request

            # Patch to_json to drain the queue. This should work even when the
            # SDK is initialized inside of the handler

            old_to_json = lambda_bootstrap.to_json

            def warden_to_json(*args, **kwargs):
                # type: (*Any, **Any) -> Any
                _drain_queue()
                return old_to_json(*args, **kwargs)

            lambda_bootstrap.to_json = warden_to_json
        else:
            lambda_bootstrap.LambdaRuntimeClient.post_init_error = _wrap_init_error(
                lambda_bootstrap.LambdaRuntimeClient.post_init_error
            )

            old_handle_event_request = lambda_bootstrap.handle_event_request

            def warden_handle_event_request(  # type: ignore
                lambda_runtime_client, request_handler, *args, **kwargs
            ):
                request_handler = _wrap_handler(request_handler)
                return old_handle_event_request(
                    lambda_runtime_client, request_handler, *args, **kwargs
                )

            lambda_bootstrap.handle_event_request = warden_handle_event_request

            # Patch the runtime client to drain the queue. This should work
            # even when the SDK is initialized inside of the handler

            def _wrap_post_function(f):
                def inner(*args, **kwargs):
                    # type: (*Any, **Any) -> Any
                    _drain_queue()
                    return f(*args, **kwargs)

                return inner  # type: ignore

            lambda_bootstrap.LambdaRuntimeClient.post_invocation_result = (
                _wrap_post_function(
                    lambda_bootstrap.LambdaRuntimeClient.post_invocation_result
                )
            )
            lambda_bootstrap.LambdaRuntimeClient.post_invocation_error = (
                _wrap_post_function(
                    lambda_bootstrap.LambdaRuntimeClient.post_invocation_error
                )
            )

def get_lambda_bootstrap() -> Optional[Any]:
    # Python 2.7: Everything is in `__main__`.
    #
    # Python 3.7: If the bootstrap module is *already imported*, it is the
    # one we actually want to use (no idea what's in __main__)
    #
    # On Python 3.8 bootstrap is also importable, but will be the same file
    # as __main__ imported under a different name:
    #
    #     sys.modules['__main__'].__file__ == sys.modules['bootstrap'].__file__
    #     sys.modules['__main__'] is not sys.modules['bootstrap']
    #
    # On container builds using the `aws-lambda-python-runtime-interface-client`
    # (awslamdaric) module, bootstrap is located in sys.modules['__main__'].bootstrap
    #
    # Such a setup would then make all monkeypatches useless.
    if "bootstrap" in sys.modules:
        return sys.modules["bootstrap"]
    elif "__main__" in sys.modules:
        if hasattr(sys.modules["__main__"], "bootstrap"):
            # awslambdaric python module in container builds
            return sys.modules["__main__"].bootstrap  # type: ignore
        return sys.modules["__main__"]
    else:
        return None

def _make_request_event_processor(aws_event, aws_context, configured_timeout):
   # type: (Any, Any, Any) -> EventProcessor
   start_time = datetime.utcnow()

   def event_processor(warden_event, hint, start_time=start_time):
      # type: (Event, Hint, datetime) -> Optional[Event]
      remaining_time_in_milis = aws_context.get_remaining_time_in_millis()
      exec_duration = configured_timeout - remaining_time_in_milis

      extra = warden_event.setdefault("extra", {})
      extra["lambda"] = {
         "function_name": aws_context.function_name,
         "function_version": aws_context.function_version,
         "invoked_function_arn": aws_context.invoked_function_arn,
         "aws_request_id": aws_context.aws_request_id,
         "execution_duration_in_millis": exec_duration,
         "remaining_time_in_millis": remaining_time_in_milis,
      }

      extra["cloudwatch logs"] = {
         "url": _get_cloudwatch_logs_url(aws_context, start_time),
         "log_group": aws_context.log_group_name,
         "log_stream": aws_context.log_stream_name,
      }

      request = warden_event.get("request", {})

      if "httpMethod" in aws_event:
         request["method"] = aws_event["httpMethod"]

      request["url"] = _get_url(aws_event, aws_context)

      if "queryStringParameters" in aws_event:
         request["query_string"] = aws_event["queryStringParameters"]

      if "headers" in aws_event:
         request["headers"] = _filter_headers(aws_event["headers"])

      # if _should_send_default_pii():
      if False:
         user_info = warden_event.setdefault("user", {})

         identity = aws_event.get("identity")
         if identity is None:
               identity = {}

         id = identity.get("userArn")
         if id is not None:
               user_info.setdefault("id", id)

         ip = identity.get("sourceIp")
         if ip is not None:
               user_info.setdefault("ip_address", ip)

         if "body" in aws_event:
               request["data"] = aws_event.get("body", "")
      else:
         if aws_event.get("body", None):
               # Unfortunately couldn't find a way to get structured body from AWS
               # event. Meaning every body is unstructured to us.
               request["data"] = AnnotatedValue("", {"rem": [["!raw", "x", 0, 0]]})

      warden_event["request"] = request

      print('line 355',warden_event)

      return warden_event

   return event_processor


def _get_url(aws_event, aws_context) -> str:
   # type: (Any, Any) -> str
   path = aws_event.get("path", None)

   headers = aws_event.get("headers")
   if headers is None:
      headers = {}

   host = headers.get("Host", None)
   proto = headers.get("X-Forwarded-Proto", None)
   if proto and host and path:
      return "{}://{}{}".format(proto, host, path)
   return "awslambda:///{}".format(aws_context.function_name)


def _get_cloudwatch_logs_url(aws_context, start_time):
   # type: (Any, datetime) -> str
   """
   Generates a CloudWatchLogs console URL based on the context object
   Arguments:
      aws_context {Any} -- context from lambda handler
   Returns:
      str -- AWS Console URL to logs.
   """
   formatstring = "%Y-%m-%dT%H:%M:%SZ"
   region = environ.get("AWS_REGION", "")

   url = (
      "https://console.{domain}/cloudwatch/home?region={region}"
      "#logEventViewer:group={log_group};stream={log_stream}"
      ";start={start_time};end={end_time}"
   ).format(
      domain="amazonaws.cn" if region.startswith("cn-") else "aws.amazon.com",
      region=region,
      log_group=aws_context.log_group_name,
      log_stream=aws_context.log_stream_name,
      start_time=(start_time - timedelta(seconds=1)).strftime(formatstring),
      end_time=(datetime.utcnow() + timedelta(seconds=2)).strftime(formatstring),
   )

   return url

SENSITIVE_ENV_KEYS = (
    "REMOTE_ADDR",
    "HTTP_X_FORWARDED_FOR",
    "HTTP_SET_COOKIE",
    "HTTP_COOKIE",
    "HTTP_AUTHORIZATION",
    "HTTP_X_FORWARDED_FOR",
    "HTTP_X_REAL_IP",
)

SENSITIVE_HEADERS = tuple(
    x[len("HTTP_") :] for x in SENSITIVE_ENV_KEYS if x.startswith("HTTP_")
)

def _filter_headers(headers: Dict[str, str]) -> Dict[str, str]:
   #  if _should_send_default_pii():
   #      return headers

    return {
        k: (
            v
            if k.upper().replace("-", "_") not in SENSITIVE_HEADERS
            else AnnotatedValue("", {"rem": [["!config", "x", 0, len(v)]]})
        )
        for k, v in iteritems(headers)
    }