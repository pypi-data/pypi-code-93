def reducer(fn):
    """Reducers take in an Event and return a single value.py

    Reducer names are always prefixed with ``get_``."""
    return fn


def hook(fn):
    """Hooks allow you to alter control flow by overriding default implementations of Template steps.py

    Hook names are always prefixed with ``on_``."""
    return fn


def action(fn):
    """Actions allow you to subscribe to Events so as to enact various side-effects.

    Action names are always prefixed with ``after_``."""
    return fn
