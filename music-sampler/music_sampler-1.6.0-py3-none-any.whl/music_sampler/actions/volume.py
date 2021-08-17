def run(action, music=None, value=100, fade=0, delta=False, **kwargs):
    if music is not None:
        music.set_volume(value, delta=delta, fade=fade)
    else:
        action.mapping.set_master_volume(value, delta=delta, fade=fade)

def description(action, music=None,
        value=100, delta=False, fade=0, **kwargs):
    formats = []
    message = ""
    if delta:
        if music is not None:
            message += "{:+d}% to volume of « {} »"
            formats.append(value)
            formats.append(music.name)
        else:
            message += "{:+d}% to volume"
            formats.append(value)
    else:
        if music is not None:
            message += "setting volume of « {} » to {}%"
            formats.append(music.name)
            formats.append(value)
        else:
            message += "setting volume to {}%"
            formats.append(value)

    if fade > 0:
        message += " with {}s fade"
        formats.append(fade)

    return _(message).format(*formats)
