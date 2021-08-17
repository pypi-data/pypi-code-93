def run(action, music=None, fade_out=0, wait=False,
        set_wait_id=None, **kwargs):
    previous = None
    for music in action.music_list(music):
        if music.is_loaded_paused() or music.is_loaded_playing():
            if previous is not None:
                previous.stop(fade_out=fade_out)
            previous = music
        else:
            music.stop(fade_out=fade_out)

    if previous is not None:
        action.waiting_music = previous
        previous.stop(
                fade_out=fade_out,
                wait=wait,
                set_wait_id=set_wait_id)

def description(action, music=None, fade_out=0, wait=False,
        set_wait_id=None, **kwargs):

    formats = []
    message = "stopping "
    if music is not None:
        message += "music « {} »"
        formats.append(music.name)
    else:
        message += "all musics"

    if fade_out > 0:
        message += " with {}s fadeout"
        formats.append(fade_out)
        if wait:
            if set_wait_id is not None:
                message += " (waiting the end of fadeout, with id {})"
                formats.append(set_wait_id)
            else:
                message += " (waiting the end of fadeout)"

    return _(message).format(*formats)

def interrupt(action, music=None, fade_out=0, wait=False,
        set_wait_id=None, **kwargs):
    if action.waiting_music is not None:
        action.waiting_music.wait_event.set()
