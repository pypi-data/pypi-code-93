#!/usr/bin/python3
# -*- coding: utf8 -*-


class CommandGUI:
    """
    Manage command events
    """

    def quit_gui(self, *args):
        """
        Destroy window and close app
        """

        self.window.destroy()
        self.window.template = None

    def fullscreen(self, *args):
        """
        Change between full screen
        """
        fullscreen_var = self.window.wm_attributes("-fullscreen")
        if fullscreen_var == 1:
            self.window.attributes("-fullscreen", False)
        else:
            self.window.attributes("-fullscreen", True)

    def draw_dashboard(self):
        """
        destroy the old page and load the new one
        """

        self.window.template.active_template.canvas.destroy()
        self.window.template.draw_dashboard()
