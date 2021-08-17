import threading

def run(action, music=None, **kwargs):
    for music in action.music_list(music):
        if not music.is_loaded(allow_substates=True):
            threading.Thread(name="MSMusicLoad", target=music.load).start()

def description(action, music=None, **kwargs):
    if music is not None:
        return "load music « {} » to memory".format(music.name)
    else:
        return "load all music to memory"
