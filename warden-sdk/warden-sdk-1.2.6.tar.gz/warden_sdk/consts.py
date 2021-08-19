"""File containing all of the constants for the sdk.

  Typical usage example:

  from warden_sdk.consts import 
  bar = foo.FunctionBar()
  
Code reference:
- [sentry_sdk](https://github.com/getsentry/sentry-python/blob/master/sentry_sdk/consts.py)
"""

from typing import (Union, Tuple, Optional, List)

DEFAULT_QUEUE_SIZE = 100
DEFAULT_MAX_BREADCRUMBS = 100


class ClientConstructor(object):
   """Client Constructor is a base class for the default options allowed.
   """

   def __init__(
       self,
       integrations: list = [],  # type: Sequence[Integration]  # noqa: B006
       creds: Tuple[dict, str] = {
           'client_id': '',
           'client_secret': '',
       },  # type: str
       service: str = '',
       api: str = '',
       scopes: Union[list, str] = [],
       # flask: bool = True
       dsn=None,  # type: Optional[str]
       with_locals=True,  # type: bool
       max_breadcrumbs=DEFAULT_MAX_BREADCRUMBS,  # type: int
       release=None,  # type: Optional[str]
       environment=None,  # type: Optional[str]
       server_name=None,  # type: Optional[str]
       shutdown_timeout=2,  # type: int
       in_app_include=[],  # type: List[str]  # noqa: B006
       in_app_exclude=[],  # type: List[str]  # noqa: B006
       default_integrations=True,  # type: bool
       dist=None,  # type: Optional[str]
       transport=None,  # type: Optional[Union[sentry_sdk.transport.Transport, Type[sentry_sdk.transport.Transport], Callable[[Event], None]]]
       transport_queue_size=DEFAULT_QUEUE_SIZE,  # type: int
       sample_rate=1.0,  # type: float
       send_default_pii=False,  # type: bool
       http_proxy=None,  # type: Optional[str]
       https_proxy=None,  # type: Optional[str]
       ignore_errors=[],  # type: List[Union[type, str]]  # noqa: B006
       request_bodies="medium",  # type: str
       before_send=None,  # type: Optional[EventProcessor]
       before_breadcrumb=None,  # type: Optional[BreadcrumbProcessor]
       debug=False,  # type: bool
       attach_stacktrace=False,  # type: bool
       ca_certs=None,  # type: Optional[str]
       propagate_traces=True,  # type: bool
       traces_sample_rate=None,  # type: Optional[float]
       traces_sampler=None,  # type: Optional[TracesSampler]
       auto_enabling_integrations=True,  # type: bool
       auto_session_tracking=True,  # type: bool
       _experiments={},  # type: Experiments  # noqa: B006
       user_fid=None,  # type: str
       user_scope=None,  # type: str
   ):
      # type: (...) -> None
      pass


def __get_default_options():
   import inspect

   if hasattr(inspect, "getfullargspec"):
      getargspec = inspect.getfullargspec
   else:
      getargspec = inspect.getargspec  # type: ignore

   a = getargspec(ClientConstructor.__init__)
   defaults = a.defaults or ()
   return dict(zip(a.args[-len(defaults):], defaults))


DEFAULT_OPTIONS = __get_default_options()

WARDEN_LOGGING_API_LINK: str = "https://api.warden.ferant.io/log"
VERSION = "1.2.6"
SDK_INFO = {
    "name": "warden.python",
    "version": VERSION,
    "packages": [{
        "name": "pypi:warden-sdk",
        "version": VERSION
    }],
}
