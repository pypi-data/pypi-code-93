def run(action, music=None, **kwargs):
    for music in action.music_list(music):
        if music.is_loaded_paused():
            music.unpause()

def description(action, music=None, **kwargs):
    if music is not None:
        return _("unpausing « {} »").format(music.name)
    else:
        return _("unpausing all musics")
