# -*- coding: utf-8 -*-

"""
DateTime   : 2021/04/04 22:37
Author     : ZhangYafei
Description: 
"""


class Foreground:
    Black = 30
    Red = 31
    Green = 32
    Yellow = 33
    Blue = 34
    Purplish_red = 35
    Cyan = 36
    White = 37


class Background:
    Black = 40
    Red = 41
    Green = 42
    Yellow = 43
    Blue = 44
    Purplish_red = 45
    Cyan = 46
    White = 47


class Display:
    Default = 0
    Highlight = 1
    Underline = 4
    Twinkle = 5
    Reverse = 7
    Invisible = 8


def print_color(string: str, display_mode: int = Display.Default, foreground: int = Foreground.Green,
                background: int = Background.Black):
    print(f"\033[{display_mode};{foreground};{background}m{string}\033[0m")


def add_color(string: str, display_mode: int = Display.Default, foreground: int = Foreground.Green,
                background: int = Background.Black):
    return f"\033[{display_mode};{foreground};{background}m{string}\033[0m"
