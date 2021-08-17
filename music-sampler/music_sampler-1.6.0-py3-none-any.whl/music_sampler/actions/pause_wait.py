def run(action, wait_id=None, **kwargs):
    action.mapping.pause_wait(wait_id)

def description(action, wait_id=None, **kwargs):
    if wait_id is None:
        return _("pause all waits")
    else:
        return _("pause wait with id {}").format(wait_id)
