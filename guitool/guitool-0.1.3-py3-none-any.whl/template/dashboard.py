#!/usr/bin/python3
# -*- coding: utf8 -*-


# Héritage
from tk_gui_tools.template.base import Base


class Dashboard(Base):
    """
    Test template and example
    """

    def __init__(self, window):

        # Init Base Template Héritage
        Base.__init__(self, window)
        self.template_name = "Dashboard"

        # Create Canvas title
        self.title = self.canvas.create_text(50, 50, text="Dashboard", anchor="w")

        # Create button quit
        self.button_quit = self.manage.create_rectangle(
            50,
            100,
            100,
            150,
            text="quit",
            fill="white",
            fill_mouse="red",
            command=("<Button-1>", self.quit_gui),
        )

        # Create round
        self.round_test = self.manage.create_round(
            200, 200, 250, 250, fill="red", fill_mouse="green"
        )

        # Create text
        self.text_test = self.manage.create_text(500, 500, text="test", fill="black")

        # Create switch
        self.button_switch = self.manage.create_button(400, 70)
        self.text_state = self.manage.create_text(460, 70, text="inactif")

    def update(self):

        if self.button_switch.active:
            self.text_state.update(text="actif")
        else:
            self.text_state.update(text="inactif")
