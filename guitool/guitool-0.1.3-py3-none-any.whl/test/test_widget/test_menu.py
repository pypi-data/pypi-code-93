import pytest
import tkinter as tk
import time

import tk_gui_tools.template_manager as template_manager


@pytest.fixture
def param_tkinter():
    # Init Tkinter
    time.sleep(0.1)
    root = tk.Tk()
    time.sleep(0.05)
    root.title("Python Project")
    root.geometry("1920x1080")
    root.attributes("-fullscreen", False)
    root.resizable(height=False, width=False)
    return root


class TestMenu:
    def test_menu_init(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        menu_test = self.template_manager.active_template.manage.create_menu(
            10, 10, 20, 20
        )
        assert menu_test.x1 == 10

    def test_menu_label(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        menu_test = self.template_manager.active_template.manage.create_menu(
            10, 10, 20, 20
        )
        menu_test.add_label("test_label")
        assert menu_test.label[0].text == "test_label"
        assert menu_test.label[0].x1 == 10
        assert menu_test.label[0].x2 == 110
        assert menu_test.label[0].y1 == 21
        assert menu_test.label[0].y2 == 41

    def test_menu_label_2(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        menu_test = self.template_manager.active_template.manage.create_menu(
            10, 10, 20, 20
        )
        menu_test.add_label("test_label_1")
        menu_test.add_label("test_label_2")
        assert menu_test.label[1].text == "test_label_2"
        assert menu_test.label[1].x1 == 10
        assert menu_test.label[1].x2 == 110
        assert menu_test.label[1].y1 == 41
        assert menu_test.label[1].y2 == 61

    def test_menu_cascade(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        menu_test = self.template_manager.active_template.manage.create_menu(
            10, 10, 20, 20
        )
        test_label_int = menu_test.add_label("test_label_1")
        menu_test.add_cascade("test_cascade", test_label_int)
        assert menu_test.cascade[menu_test.label[0]][0].text == "test_cascade"
        assert menu_test.cascade[menu_test.label[0]][0].x1 == 110
        assert menu_test.cascade[menu_test.label[0]][0].x2 == 210
        assert menu_test.cascade[menu_test.label[0]][0].y1 == 21
        assert menu_test.cascade[menu_test.label[0]][0].y2 == 41

    def test_menu_cascade_2(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        menu_test = self.template_manager.active_template.manage.create_menu(
            10, 10, 20, 20
        )
        test_label_int = menu_test.add_label("test_label_1")
        menu_test.add_cascade("test_cascade_1", test_label_int)
        menu_test.add_cascade("test_cascade_2", test_label_int)
        assert menu_test.cascade[menu_test.label[0]][1].text == "test_cascade_2"
        assert menu_test.cascade[menu_test.label[0]][1].x1 == 110
        assert menu_test.cascade[menu_test.label[0]][1].x2 == 210
        assert menu_test.cascade[menu_test.label[0]][1].y1 == 41
        assert menu_test.cascade[menu_test.label[0]][1].y2 == 61

    def test_menu_motion(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        menu_test = self.template_manager.active_template.manage.create_menu(
            10, 10, 20, 20
        )
        menu_test.motion(15, 15)
        assert menu_test.active_focus is True
        menu_test.motion(20, 20)
        assert menu_test.active_focus is False

    def test_menu_motion_2(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        menu_test = self.template_manager.active_template.manage.create_menu(
            10, 10, 20, 20
        )
        menu_test.add_label("test_label_1")
        menu_test.label_active = True
        menu_test.motion(15, 15)
        assert menu_test.label[0].active_focus is False
        menu_test.motion(15, 30)
        assert menu_test.label[0].active_focus is True

    def test_menu_motion_3(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        menu_test = self.template_manager.active_template.manage.create_menu(
            10, 10, 20, 20
        )
        test_label_int = menu_test.add_label("test_label_1")
        menu_test.add_cascade("test_cascade_1", test_label_int)
        menu_test.label_active = True
        menu_test.motion(15, 15)
        assert menu_test.label[0].active_focus is False
        menu_test.motion(15, 30)
        assert menu_test.label[0].active_focus is True
        menu_test.motion(120, 30)
        assert menu_test.cascade[menu_test.label[0]][0].active_focus is False
        menu_test.label[0].cascade_active = True
        menu_test.motion(120, 30)
        assert menu_test.cascade[menu_test.label[0]][0].active_focus is True

    def test_menu_command(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        menu_test = self.template_manager.active_template.manage.create_menu(
            10, 10, 20, 20
        )
        menu_test.add_label("test_label_1")
        menu_test.commande(15, 15, "<Button-1>")
        assert menu_test.label_active is True
        menu_test.commande(15, 15, "<Button-1>")
        assert menu_test.label_active is False

    def test_menu_command_2(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        menu_test = self.template_manager.active_template.manage.create_menu(
            10, 10, 20, 20
        )
        test_label_int = menu_test.add_label("test_label_1")
        menu_test.add_cascade("test_cascade_1", test_label_int)
        menu_test.motion(15, 15)
        menu_test.commande(15, 15, "<Button-1>")
        assert menu_test.label_active is True
        menu_test.motion(15, 30)
        menu_test.commande(15, 30, "<Button-1>")
        assert menu_test.label[0].cascade_active is True
        menu_test.commande(15, 30, "<Button-1>")
        assert menu_test.label[0].cascade_active is False
        menu_test.commande(15, 30, "<Button-1>")
        assert menu_test.label[0].cascade_active is True
        menu_test.motion(500, 500)
        menu_test.commande(500, 500, "<Button-1>")
        assert menu_test.label[0].cascade_active is False
        assert menu_test.label_active is False
