def run(action, wait_id=None, **kwargs):
    action.mapping.unpause_wait(wait_id)

def description(action, wait_id=None, **kwargs):
    if wait_id is None:
        return _("unpause all waits")
    else:
        return _("unpause wait with id {}").format(wait_id)
