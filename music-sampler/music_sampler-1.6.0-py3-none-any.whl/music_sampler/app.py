from .helpers import parse_args, dump_config, register_fonts, path

parse_args()

import kivy
kivy.require("1.9.1")
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.properties import ListProperty, StringProperty
from kivy.core.window import Window
from kivy.lang import Builder

dump_config()
register_fonts()


from .helpers import Config
from .key import Key
from .mapping import Mapping

from .app_blocks.actionlist import *
from .app_blocks.playlist import *

class KeyList(RelativeLayout):
    keylist = ListProperty([])
    first_key = StringProperty("")
    second_key = StringProperty("")
    third_key = StringProperty("")

    def append(self, value):
        self.keylist.insert(0, value)

    def on_keylist(self, instance, new_key_list):
        if len(self.keylist) > 0:
            self.first_key  = self.keylist[0]
        if len(self.keylist) > 1:
            self.second_key = self.keylist[1]
        if len(self.keylist) > 2:
            self.third_key  = self.keylist[2]

class UnfocusedOverlay(Label):
    pass

class Screen(FloatLayout):
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.unfocused_widget = UnfocusedOverlay()
        Window.bind(focus=self.focus_changed)
        Window.on_request_close = self.on_request_close

    def focus_changed(self, instance, focus):
        if not Config.focus_warning:
            return
        if not focus:
            self.add_widget(self.unfocused_widget)
        else:
            self.remove_widget(self.unfocused_widget)

    def on_request_close(self, *args, **kwargs):
        self.ids["Mapping"].leave_application()

class MusicSamplerApp(App):
    def build(self):
        Window.size = (913, 563)

        return Screen()

def main():
    with open(path() + "/music_sampler.kv", encoding='utf8') as f:
        Builder.load_string(f.read())
    MusicSamplerApp().run()
