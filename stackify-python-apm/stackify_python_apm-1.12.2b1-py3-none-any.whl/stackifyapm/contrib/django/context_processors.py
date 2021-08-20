from stackifyapm.traces import execution_context
from stackifyapm.utils.helper import get_rum_script_or_none


def rum_tracing(request):

    transaction = execution_context.get_transaction()
    rum_script = get_rum_script_or_none(transaction)
    if rum_script:
        return {
            "stackifyapm_inject_rum": rum_script
        }
    return {}
