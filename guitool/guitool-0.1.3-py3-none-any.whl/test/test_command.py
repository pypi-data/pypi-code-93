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


class Event:
    """
    Event object
    """

    x = 20
    y = 25


@pytest.fixture
def param_event():
    # Init event
    return Event()


class TestCommandMouse:
    def test_adjust_mouse(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        self.template_manager.active_template.adjust_mousse(10, 15)
        assert self.template_manager.active_template.x == 10
        assert self.template_manager.active_template.y == 15

    def test_motion(self, param_tkinter, param_event):
        self.template_manager = template_manager.Template(param_tkinter, True)
        self.template_manager.active_template.mouse_motion(param_event)
        assert self.template_manager.active_template.x == 20
        assert self.template_manager.active_template.y == 25

    def test_double_double_click_button_1(self, param_tkinter, param_event):
        self.template_manager = template_manager.Template(param_tkinter, True)
        self.template_manager.active_template.double_click_button_1(param_event)
        assert (
            self.template_manager.active_template.manage.action == "<Double-Button-1>"
        )

    def test_double_click_button_1(self, param_tkinter, param_event):
        self.template_manager = template_manager.Template(param_tkinter, True)
        self.template_manager.active_template.click_button_1(param_event)
        assert self.template_manager.active_template.manage.action == "<Button-1>"


class TestCommandGui:
    def test_command_fullscreen(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        self.template_manager.active_template.fullscreen()
        assert self.template_manager.window.wm_attributes("-fullscreen") == 1
        self.template_manager.active_template.fullscreen()
        assert self.template_manager.window.wm_attributes("-fullscreen") == 0
