from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ListProperty
from kivy.clock import Clock, mainthread
from ..helpers import duration_to_min_sec
from ..lock import Lock

__all__ = ["PlayList",
        "PlayListIcons", "PlayListIcon",
        "PlayListNames", "PlayListName",
        "PlayListTimes", "PlayListTime"]

playlist_lock = Lock("playlist")

class PlayList(RelativeLayout):
    playlist = ListProperty([])

    def __init__(self, **kwargs):
        super(PlayList, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_playlist, 0.5)

    @mainthread
    def update_playlist(self, dt):
        if self.parent is None or 'Mapping' not in self.parent.ids:
            return True

        open_files = self.parent.ids['Mapping'].open_files
        playlist = []
        for music_file in open_files.values():
            if not music_file.is_in_use():
                continue

            time_info = "{}/{}".format(
                    duration_to_min_sec(music_file.sound_position),
                    duration_to_min_sec(music_file.sound_duration))

            if music_file.is_loaded_paused():
                playlist.append(["⏸", music_file.name, time_info, False])
            else:
                playlist.append(["⏵", music_file.name, time_info, True])
        with playlist_lock:
            self.playlist = playlist


class PlayListIcons(StackLayout):
    def __init__(self, **kwargs):
        super(PlayListIcons, self).__init__(**kwargs)
        self.icons = []

    def on_parent(self, instance, parent):
        parent.bind(playlist=self.update_playlist_icons)

    def update_playlist_icons(self, instance, playlist):
        icons_length = len(self.icons)
        index = -1
        for index, [icon, filename, time_info, playing] in enumerate(playlist):
            if index >= icons_length:
                icon_label = PlayListIcon(text=icon)
                self.add_widget(icon_label)
                self.icons.append(icon_label)
            else:
                self.icons[index].text = icon

        if index+1 < icons_length:
            self.clear_widgets(children=self.icons[index+1:icons_length])
            del(self.icons[index+1:icons_length])

class PlayListIcon(Label):
    def __init__(self, text='', **kwargs):
        super(PlayListIcon, self).__init__(**kwargs)
        self.text = text

    def on_parent(self, instance, parent):
        if parent is not None:
            parent.bind(font_size=self.update_font_size)
            parent.bind(labels_height=self.update_height)

    def update_height(self, instance, height):
        self.height = height

    def update_font_size(self, instance, font_size):
        self.font_size = font_size

class PlayListNames(StackLayout):
    def __init__(self, **kwargs):
        super(PlayListNames, self).__init__(**kwargs)
        self.names = []

    def on_parent(self, instance, parent):
        parent.bind(playlist=self.update_playlist_names)

    def update_playlist_names(self, instance, playlist):
        names_length = len(self.names)
        index = -1
        for index, [icon, filename, time_info, playing] in enumerate(playlist):
            if index >= names_length:
                name_label = PlayListName(text=filename, is_playing=playing)
                self.add_widget(name_label)
                self.names.append(name_label)
            else:
                self.names[index].text = filename

        if index+1 < names_length:
            self.clear_widgets(children=self.names[index+1:names_length])
            del(self.names[index+1:names_length])

class PlayListName(Label):
    def __init__(self, text='', is_playing=False, **kwargs):
        super(PlayListName, self).__init__(**kwargs)
        self.text = text
        self.bold = is_playing

    def on_parent(self, instance, parent):
        if parent is not None:
            parent.bind(font_size=self.update_font_size)
            parent.bind(labels_height=self.update_height)

    def update_height(self, instance, height):
        self.height = height

    def update_font_size(self, instance, font_size):
        self.font_size = font_size

class PlayListTimes(StackLayout):
    def __init__(self, **kwargs):
        super(PlayListTimes, self).__init__(**kwargs)
        self.times = []

    def on_parent(self, instance, parent):
        parent.bind(playlist=self.update_playlist_times)

    def update_playlist_times(self, instance, playlist):
        times_length = len(self.times)
        index = -1
        for index, [icon, filename, time_info, playing] in enumerate(playlist):
            if index >= times_length:
                time_label = PlayListTime(text=time_info)
                self.add_widget(time_label)
                self.times.append(time_label)
            else:
                self.times[index].text = time_info

        if index+1 < times_length:
            self.clear_widgets(children=self.times[index+1:times_length])
            del(self.times[index+1:times_length])

class PlayListTime(Label):
    def __init__(self, text='', **kwargs):
        super(PlayListTime, self).__init__(**kwargs)
        self.text = text

    def on_parent(self, instance, parent):
        if parent is not None:
            parent.bind(font_size=self.update_font_size)
            parent.bind(labels_height=self.update_height)

    def update_height(self, instance, height):
        self.height = height

    def update_font_size(self, instance, font_size):
        self.font_size = font_size

