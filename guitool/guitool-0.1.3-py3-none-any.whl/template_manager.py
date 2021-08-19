#!/usr/bin/python3
# -*- coding: utf8 -*-

import tk_gui_tools.template.dashboard as dashboard


class Template:
    def __init__(self, window, default_template: bool):

        self.window = window

        if default_template:
            self.active_template = dashboard.Dashboard(self.window)

    def draw_dashboard(self):
        """
        Draw test template and example
        :return: None
        """

        self.active_template = dashboard.Dashboard(self.window)
