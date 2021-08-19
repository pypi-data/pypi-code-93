import pytest
import tkinter as tk
import time

import tk_gui_tools.template_manager as template_manager


@pytest.fixture
def param_tkinter():
    # Init Tkinter
    time.sleep(0.05)
    root = tk.Tk()
    time.sleep(0.05)
    root.title("Python Project")
    root.geometry("1920x1080")
    root.attributes("-fullscreen", False)
    root.resizable(height=False, width=False)
    return root


class TestButton:
    def test_button_init(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        menu_test = self.template_manager.active_template.manage.create_button(50, 50)
        assert menu_test.x1 == 20
        assert menu_test.x2 == 80
        assert menu_test.y1 == 40
        assert menu_test.y2 == 60
        assert menu_test.rectangle["x1"] == 30

    def test_button_command(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        menu_test = self.template_manager.active_template.manage.create_button(50, 50)
        assert menu_test.active is False
        menu_test.commande(50, 50, "<Button-1>")
        assert menu_test.active is True
        assert menu_test.rectangle["x1"] == 70
        menu_test.commande(50, 50, "<Button-1>")
        assert menu_test.active is False
        assert menu_test.rectangle["x1"] == 30
