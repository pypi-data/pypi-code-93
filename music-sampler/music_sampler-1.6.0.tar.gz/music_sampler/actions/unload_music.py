def run(action, music=None, **kwargs):
    for music in action.music_list(music):
        if music.is_unloadable():
            music.unload()

def description(action, music=None, **kwargs):
    if music is not None:
        return "unload music « {} » from memory".format(music.name)
    else:
        return "unload all music from memory"
