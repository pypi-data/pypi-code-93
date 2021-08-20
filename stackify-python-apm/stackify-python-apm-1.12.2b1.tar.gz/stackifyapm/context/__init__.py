def init_execution_context():
    if threading_local_monkey_patched():
        from stackifyapm.context.threadlocal import execution_context

        return execution_context

    try:
        from stackifyapm.context.contextvars import execution_context
    except ImportError:
        from stackifyapm.context.threadlocal import execution_context
    return execution_context


def threading_local_monkey_patched():
    try:
        from gevent.monkey import is_object_patched
    except ImportError:
        pass
    else:
        if is_object_patched("threading", "local"):
            return True

    try:
        from eventlet.patcher import is_monkey_patched
    except ImportError:
        pass
    else:
        if is_monkey_patched("thread"):
            return True

    return False
