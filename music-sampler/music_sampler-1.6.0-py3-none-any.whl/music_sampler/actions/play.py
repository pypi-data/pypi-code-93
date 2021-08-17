def run(action, music=None, fade_in=0, start_at=0,
        restart_if_running=False, volume=100,
        loop=0, **kwargs):
    for music in action.music_list(music):
        if restart_if_running:
            if music.is_in_use():
                music.stop()
            music.play(
                    volume=volume,
                    fade_in=fade_in,
                    start_at=start_at,
                    loop=loop)
        elif not music.is_in_use():
            music.play(
                    volume=volume,
                    fade_in=fade_in,
                    start_at=start_at,
                    loop=loop)

def description(action, music=None, fade_in=0, start_at=0,
        restart_if_running=False, volume=100, loop=0, **kwargs):
    formats = []
    message = "starting "
    if music is not None:
        message += "« {} »"
        formats.append(music.name)
    else:
        message += "all musics"

    if start_at != 0:
        message += " at {}s"
        formats.append(start_at)

    if fade_in != 0:
        message += " with {}s fade_in"
        formats.append(fade_in)

    message += " at volume {}%"
    formats.append(volume)

    if loop > 0:
        message += " {} times"
        formats.append(loop + 1)
    elif loop < 0:
        message += " in loop"

    if restart_if_running:
        message += " (restarting if already running)"

    return _(message).format(*formats)
