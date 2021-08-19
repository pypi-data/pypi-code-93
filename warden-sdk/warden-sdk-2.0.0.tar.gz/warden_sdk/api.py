import inspect

from warden_sdk.hub import Hub

__all__ = [
    "debug"
    #  "capture_event",
    #  "capture_message",
    #  "capture_exception",
    #  "add_breadcrumb",
    #  "configure_scope",
    #  "push_scope",
    #  "flush",
    #  "last_event_id",
    #  "start_span",
    #  "start_transaction",
    #  "set_tag",
    #  "set_context",
    #  "set_extra",
    #  "set_user",
    #  "set_level",
]

from typing import (Optional, Union, List)


def hubmethod(f):
   f.__doc__ = "%s\n\n%s" % (
       "Alias for :py:meth:`warden_sdk.Hub.%s`" % f.__name__,
       inspect.getdoc(getattr(Hub, f.__name__)),
   )
   return f


@hubmethod
def debug(user_fid: Optional[str] = None,
          user_scope: Optional[Union[str, List[str]]] = None):
   return Hub.current.debug(user_fid, user_scope)
