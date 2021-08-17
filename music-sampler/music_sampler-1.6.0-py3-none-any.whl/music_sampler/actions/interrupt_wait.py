def run(action, wait_id=None, **kwargs):
    action.mapping.interrupt_wait(wait_id)

def description(action, wait_id=None, **kwargs):
    if wait_id is None:
        return _("interrupt all waits")
    else:
        return _("interrupt wait with id {}").format(wait_id)
