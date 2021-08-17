def run(action, music=None, value=0, delta=False, **kwargs):
    for music in action.music_list(music):
        music.seek(value=value, delta=delta)

def description(action, music=None, value=0, delta=False, **kwargs):
    if delta:
        if music is not None:
            return _("moving music « {} » by {:+d}s") \
                    .format(music.name, value)
        else:
            return _("moving all musics by {:+d}s") \
                    .format(value)
    else:
        if music is not None:
            return _("moving music « {} » to position {}s") \
                    .format(music.name, value)
        else:
            return _("moving all musics to position {}s") \
                    .format(value)
