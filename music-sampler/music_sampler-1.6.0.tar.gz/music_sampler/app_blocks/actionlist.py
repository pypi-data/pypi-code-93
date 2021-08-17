from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ListProperty, StringProperty
from ..lock import Lock

from kivy.clock import mainthread

__all__ = ["ActionList",
        "ActionListIcons", "ActionListIcon",
        "ActionListDescriptions", "ActionListDescription"]

actionlist_lock = Lock("playlist")

class ActionList(RelativeLayout):
    action_title = StringProperty("")
    action_list = ListProperty([])

    @mainthread
    def update_list(self, key, action_descriptions):
        if key.repeat_delay > 0:
            self.action_title = _(
                    "actions linked to key {} (repeat protection {}s):"
                    ).format(key.key_sym, key.repeat_delay)
        else:
            self.action_title = _(
                    "actions linked to key {}:"
                    ).format(key.key_sym)

        action_list = []

        for [action, status] in action_descriptions:
            if status == "done":
                icon = "✓"
            elif status == "current":
                icon = "✅"
            else:
                icon = " "
            action_list.append([icon, action])
        with actionlist_lock:
            self.action_list = action_list

class ActionListIcons(StackLayout):
    def __init__(self, **kwargs):
        super(ActionListIcons, self).__init__(**kwargs)
        self.icons = []

    def on_parent(self, instance, parent):
        parent.bind(action_list=self.update_actionlist_icons)

    def update_actionlist_icons(self, instance, actionlist):
        icons_length = len(self.icons)
        index = -1
        for index, [icon, description] in enumerate(actionlist):
            if index >= icons_length:
                icon_label = ActionListIcon(text=icon)
                self.add_widget(icon_label)
                self.icons.append(icon_label)
            else:
                self.icons[index].text = icon

        if index+1 < icons_length:
            self.clear_widgets(children=self.icons[index+1:icons_length])
            del(self.icons[index+1:icons_length])

class ActionListIcon(Label):
    def __init__(self, text='', **kwargs):
        super(ActionListIcon, self).__init__(**kwargs)
        self.text = text

    def on_parent(self, instance, parent):
        if parent is not None:
            parent.bind(font_size=self.update_font_size)
            parent.bind(labels_height=self.update_height)

    def update_height(self, instance, height):
        self.height = height

    def update_font_size(self, instance, font_size):
        self.font_size = font_size

class ActionListDescriptions(StackLayout):
    def __init__(self, **kwargs):
        super(ActionListDescriptions, self).__init__(**kwargs)
        self.descriptions = []

    def on_parent(self, instance, parent):
        parent.bind(action_list=self.update_actionlist_descriptions)

    def update_actionlist_descriptions(self, instance, actionlist):
        descriptions_length = len(self.descriptions)
        index = -1
        for index, [icon, description] in enumerate(actionlist):
            if index >= descriptions_length:
                description_label = ActionListDescription(text=description)
                self.add_widget(description_label)
                self.descriptions.append(description_label)
            else:
                self.descriptions[index].text = description

        if index+1 < descriptions_length:
            self.clear_widgets(
                    children=self.descriptions[index+1:descriptions_length])
            del(self.descriptions[index+1:descriptions_length])

class ActionListDescription(Label):
    def __init__(self, text='', **kwargs):
        super(ActionListDescription, self).__init__(**kwargs)
        self.text = text

    def on_parent(self, instance, parent):
        if parent is not None:
            parent.bind(font_size=self.update_font_size)
            parent.bind(labels_height=self.update_height)

    def update_height(self, instance, height):
        self.height = height

    def update_font_size(self, instance, font_size):
        self.font_size = font_size

