import atexit
import sys

from . import (
    _compatibility,  # pylint: disable=redefined-builtin; Import first to fail fast
)
from . import (
    _functions,
    agg,
    array,
    comparator,
    config,
    experimental,
    math,
    query,
    scope,
    string,
    type,
)
from ._functions import *  # pylint: disable=redefined-builtin
from ._java_utils import retrieve_info_from_jar
from ._licensing import EULA as __license__
from ._licensing import check_license, hide_new_license_agreement_message
from ._plugins import register_active_plugins
from ._sessions import Sessions
from ._telemetry import setup_telemetry
from ._tutorial import copy_tutorial
from ._type_utils import _typecheck_instrumentation
from ._version import VERSION as __version__

# pylint: disable=invalid-name
sessions = Sessions()
create_session = sessions.create_session
open_query_session = sessions.open_query_session
# pylint: enable=invalid-name


@atexit.register
def close() -> None:
    """Close all opened sessions."""
    sessions.close()


(_LICENSE_END_DATE, _IS_COMMUNITY_LICENSE) = retrieve_info_from_jar()

check_license(_LICENSE_END_DATE, _IS_COMMUNITY_LICENSE)

register_active_plugins()

setup_telemetry()

__all__ = [
    "copy_tutorial",
    "create_session",
    "open_query_session",
    "__version__",
]
__all__ += _functions.__all__
if __license__:
    __all__.append("__license__")

# Instrument the public API for runtime typechecking
_typecheck_instrumentation(sys.modules[__name__])
