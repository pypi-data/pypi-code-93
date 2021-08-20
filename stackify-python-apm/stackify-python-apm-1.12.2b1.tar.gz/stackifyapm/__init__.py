__all__ = ("VERSION")

__version__ = '1.12.2b1'
name = "stackify-python-apm"


VERSION = __version__


from stackifyapm.base import Client  # noqa
from stackifyapm.conf import setup_logging  # noqa
from stackifyapm.instrumentation.control import instrument  # noqa
from stackifyapm.instrumentation.control import uninstrument  # noqa
from stackifyapm.traces import CaptureSpan  # noqa
from stackifyapm.traces import set_transaction_context  # noqa
from stackifyapm.traces import set_transaction_name  # noqa
from stackifyapm.traces import execution_context # noqa
from stackifyapm.utils.helper import get_rum_script_or_none # noqa


# FIXME: Not sure if the right location
def insert_rum_script():
    transaction = execution_context.get_transaction()
    rum_script = get_rum_script_or_none(transaction)
    if rum_script:
        return rum_script
    return ''
