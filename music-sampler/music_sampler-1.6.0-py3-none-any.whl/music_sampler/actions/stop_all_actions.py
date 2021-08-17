def run(action, key_start_time=0, other_only=False, **kwargs):
    if other_only:
        action.mapping.stop_all_running(
                except_key=action.key,
                key_start_time=key_start_time)
    else:
        action.mapping.stop_all_running()

def description(action, other_only=False, **kwargs):
    message = "stopping all actions"
    if other_only:
        message += " except this key"

    return _(message)
