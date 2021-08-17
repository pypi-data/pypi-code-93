import threading
import time

def run(action, duration=0, music=None, set_wait_id=None, **kwargs):
    action.mapping.add_wait(action, wait_id=set_wait_id)

    action.sleep_event = threading.Event()
    action.sleep_event_timer = threading.Timer(
            duration,
            action.sleep_event.set)

    action.sleep_event_initial_duration = duration
    action.sleep_event_paused = False
    action.sleep_event_left_time = duration

    if music is not None:
        music.wait_end()

    if duration <= 0 or not action.sleep_event_paused:
        action.sleep_event_timer.start()
        action.sleep_event_started_time = time.time()

    action.sleep_event.wait()

def description(action, duration=0, music=None, set_wait_id=None, **kwargs):
    formats = []
    message = ""
    if music is None:
        message += "waiting {}s"
        formats.append(duration)
    elif duration == 0:
        message += "waiting the end of « {} »"
        formats.append(music.name)
    else:
        message += "waiting the end of « {} » + {}s"
        formats.append(music.name)
        formats.append(duration)

    if set_wait_id is not None:
        message += " (setting id = {})"
        formats.append(set_wait_id)

    return _(message).format(*formats)

def pause(action, **kwargs):
    if action.sleep_event_paused:
        return

    action.sleep_event_paused = True

    if not action.sleep_event_timer.is_alive():
        return

    action.sleep_event_timer.cancel()

    action.sleep_event_left_time = action.sleep_event_left_time\
            - (time.time() - action.sleep_event_started_time)
    if action.sleep_event_left_time < 0:
        action.sleep_event.set()

def unpause(action, **kwargs):
    if not action.sleep_event_paused:
        return

    action.sleep_event_paused = False

    action.sleep_event_timer = threading.Timer(
            action.sleep_event_left_time,
            action.sleep_event.set)

    action.sleep_event_timer.start()
    action.sleep_event_started_time = time.time()

def reset(action, **kwargs):
    action.sleep_event_timer.cancel()

    action.sleep_event_left_time = action.sleep_event_initial_duration

    if action.sleep_event_paused:
        return

    action.sleep_event_timer = threading.Timer(
            action.sleep_event_left_time,
            action.sleep_event.set)

    action.sleep_event_timer.start()
    action.sleep_event_started_time = time.time()

def interrupt(action, duration=0, music=None, **kwargs):
    if action.sleep_event is not None:
        action.sleep_event.set()
        action.sleep_event_timer.cancel()
    if music is not None:
        music.wait_event.set()
