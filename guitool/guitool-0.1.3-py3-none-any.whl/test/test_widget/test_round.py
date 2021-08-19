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


class TestRound:
    def test_round_init(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        round_test = self.template_manager.active_template.manage.create_round(
            10, 10, 20, 20
        )
        assert round_test.x1 == 10

    def test_round_text(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        round_test = self.template_manager.active_template.manage.create_round(
            10, 10, 20, 20, command=("<Double-Button-1>", "test")
        )
        assert round_test.command["<Double-Button-1>"] == "test"
        round_test = self.template_manager.active_template.manage.create_round(
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
        assert round_test.command["<Double-Button-1>"] == "test Double Button-1"
        assert round_test.command["<Button-1>"] == "test Button-1"

    def test_round_draw(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        round_test = self.template_manager.active_template.manage.create_round(
            10, 10, 20, 20, square_fill="black"
        )
        assert len(round_test.item_tk) == 2
        round_test.square_fill = None
        round_test.draw()
        assert len(round_test.item_tk) == 1

    def test_round_draw_focus(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        round_test = self.template_manager.active_template.manage.create_round(
            10, 10, 20, 20, square_fill="black"
        )
        assert round_test.active_focus is False
        round_test.motion(15, 15)
        assert round_test.active_focus is True
        round_test.motion(25, 25)
        assert round_test.active_focus is False

    def test_round_update(self, param_tkinter):
        self.template_manager = template_manager.Template(param_tkinter, True)
        round_test = self.template_manager.active_template.manage.create_round(
            10, 10, 20, 20, fill="red", square_fill="black"
        )
        assert round_test.fill == "red"
        round_test.update(fill="blue")
        assert round_test.fill == "blue"
        round_test.motion(15, 15)
        round_test.update(fill="red")
        assert round_test.fill == "red"
