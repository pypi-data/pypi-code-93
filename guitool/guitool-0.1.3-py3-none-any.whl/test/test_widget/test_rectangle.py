#!/usr/bin/python3
# -*- coding: utf8 -*-

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


class TestRectangle:
    def test_rectangle_init(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        rectangle_test = self.template_manager.active_template.manage.create_rectangle(
            10, 10, 20, 20
        )
        assert rectangle_test.x1 == 10

    def test_rectangle_init_text(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        rectangle_test = self.template_manager.active_template.manage.create_rectangle(
            10, 10, 20, 20, text="test"
        )
        assert rectangle_test.text == "test"
        assert rectangle_test.text_x == 15
        assert rectangle_test.text_y == 15
        assert rectangle_test.anchor == "center"

    def test_rectangle_init_command(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        rectangle_test = self.template_manager.active_template.manage.create_rectangle(
            10, 10, 20, 20, command=("<Double-Button-1>", "test")
        )
        assert rectangle_test.command["<Double-Button-1>"] == "test"
        rectangle_test = self.template_manager.active_template.manage.create_rectangle(
            10,
            10,
            20,
            20,
            command=(
                "<Double-Button-1>",
                "test Double Button-1",
                "<Button-1>",
                "test Button-1",
            ),
        )
        assert rectangle_test.command["<Double-Button-1>"] == "test Double Button-1"
        assert rectangle_test.command["<Button-1>"] == "test Button-1"

    def test_rectangle_init_relief(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        rectangle_test = self.template_manager.active_template.manage.create_rectangle(
            10, 10, 20, 20, relief=True
        )
        assert rectangle_test.relief is True
        assert rectangle_test.ligne_1 == [10, 20, 20, 20]
        assert rectangle_test.ligne_2 == [20, 10, 20, 20]

    def test_rectangle_draw(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        rectangle_test = self.template_manager.active_template.manage.create_rectangle(
            10, 10, 20, 20, relief=True
        )
        assert len(rectangle_test.item_tk) == 3
        rectangle_test.relief = False
        rectangle_test.draw()
        assert len(rectangle_test.item_tk) == 1

    def test_rectangle_focus(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        rectangle_test = self.template_manager.active_template.manage.create_rectangle(
            10, 10, 20, 20, relief=True, text="test"
        )
        assert rectangle_test.active_focus is False
        rectangle_test.motion(15, 15)
        assert rectangle_test.active_focus is True
        rectangle_test.motion(5, 5)
        assert rectangle_test.active_focus is False

    def test_rectangle_update(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        rectangle_test = self.template_manager.active_template.manage.create_rectangle(
            10, 10, 20, 20, relief=True, text="test", fill="#FF0000"
        )
        assert rectangle_test.fill == "#FF0000"
        rectangle_test.update(fill="blue")
        assert rectangle_test.fill == "blue"
        rectangle_test.motion(15, 15)
        rectangle_test.update(fill="red")
        assert rectangle_test.fill == "red"
