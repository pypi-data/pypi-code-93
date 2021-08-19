#!/usr/bin/python3
# -*- coding: utf8 -*-

import tkinter as tk

import tk_gui_tools.settings as setting
import tk_gui_tools.template_manager as template_manager


class Main(tk.Tk):
    def __init__(self, *args, **kwargs):

        # Launch command
        self.command(*args)

        # Init setting
        self.setting = kwargs.get("settings", None)

        if self.setting is not None:
            self.refresh = self.setting.refresh
            self.default_template = self.setting.default_template
            self.screen = self.setting.screen

        else:
            self.refresh = 200
            self.default_template = True
            self.screen = setting.screen

        # Init Tkinter
        tk.Tk.__init__(self)
        self.title(self.setting.screen["title"])
        self.geometry(self.setting.screen["screensize"])
        self.attributes("-fullscreen", self.setting.screen["fullscreen"])
        self.resizable(
            height=self.setting.screen["resizable"]["height"],
            width=self.setting.screen["resizable"]["width"],
        )

        self.window = self

        # Init template manager
        self.template = template_manager.Template(self.window, self.default_template)

    def run(self):
        self.after(self.refresh, self.update_gui)
        self.mainloop()

    def update_gui(self):
        self.template.active_template.update()
        self.after(self.refresh, self.update_gui)

    def command(self, *args):
        """
        Manage command, not implemented
        :param args:
        :return:
        """
        print(args)
