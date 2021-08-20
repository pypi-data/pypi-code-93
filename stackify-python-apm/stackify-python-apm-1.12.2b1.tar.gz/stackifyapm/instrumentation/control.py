import threading

from stackifyapm.instrumentation import register

_lock = threading.Lock()


def instrument(client=None):
    """
    Instruments all registered methods/functions
    """
    with _lock:
        for obj in register.get_instrumentation_objects(client=client):
            obj.instrument(client=client)


def uninstrument(client=None):
    """
    If instrumentation is present, remove it and replaces it with the original method/function
    """
    with _lock:
        for obj in register.get_instrumentation_objects(client=client):
            obj.uninstrument(client=client)
