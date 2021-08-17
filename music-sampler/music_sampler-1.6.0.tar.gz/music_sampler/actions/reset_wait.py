def run(action, wait_id=None, **kwargs):
    action.mapping.reset_wait(wait_id)

def description(action, wait_id=None, **kwargs):
    if wait_id is None:
        return _("reset all waits")
    else:
        return _("reset wait with id {}").format(wait_id)
