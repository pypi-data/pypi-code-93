from pynput.keyboard import Listener, Key, KeyCode
from colorama import init, Fore, Back, Style
from .components import Component, Field
import os


class Reader:
    def __init__(self, components: list[Component], stop_when_press=type(None), selected_color=Back.WHITE, selected_fore_color=Fore.BLACK):
        init()
        self.selected_color = selected_color
        self.selected_fore_color = selected_fore_color

        self.components = {}
        for i in components:
            i.reader = self
            self.components[i.name] = i

        self.current_selected=components[0]
        self.index = 0

        if not self.current_selected.enable:
            while True:
                self.index += 1
                if self.index >= len(self.components):
                    self.index = 0
                self.update()

                if self.current_selected.enable:
                    break
        elif isinstance(self.current_selected, Field) and self.current_selected.readonly:
            while True:
                self.index += 1
                if self.index >= len(self.components):
                    self.index = 0
                self.update()

                if isinstance(self.current_selected, Field) and not self.current_selected.readonly:
                    break
                elif not isinstance(self.current_selected, Field):
                    break

        self.stop_when_press = stop_when_press

        self._key_up = KeyCode(char='w')
        self._key_up2 = Key.up
        self._key_down = KeyCode(char='s')
        self._key_down2 = Key.down
        self._enter = Key.enter


    @staticmethod
    def _print_with_color(s, color=Fore.WHITE, brightness=Style.NORMAL, **kwargs):
        print(f"{brightness}{color}{s}{Style.RESET_ALL}", **kwargs)

    def up(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.components) - 1
        self.update()

        if not self.current_selected.enable:
            while True:
                self.index -= 1
                if self.index < 0:
                    self.index = len(self.components) - 1
                self.update()

                if self.current_selected.enable:
                    break
        elif isinstance(self.current_selected, Field) and self.current_selected.readonly:
            while True:
                self.index -= 1
                if self.index < 0:
                    self.index = len(self.components) - 1
                self.update()

                if isinstance(self.current_selected, Field) and not self.current_selected.readonly:
                    break
                elif not isinstance(self.current_selected, Field):
                    break


    def down(self):
        self.index += 1
        if self.index >= len(self.components):
            self.index = 0
        self.update()

        if not self.current_selected.enable:
            while True:
                self.index += 1
                if self.index >= len(self.components):
                    self.index = 0
                self.update()

                if self.current_selected.enable:
                    break
        elif isinstance(self.current_selected, Field) and self.current_selected.readonly:
            while True:
                self.index += 1
                if self.index >= len(self.components):
                    self.index = 0
                self.update()

                if isinstance(self.current_selected, Field) and not self.current_selected.readonly:
                    break
                elif not isinstance(self.current_selected, Field):
                    break


    def click(self):
        return False


    def on_press(self, key):
        if key == self._key_up or key == self._key_up2:
            self.up()
        elif key == self._key_down or key == self._key_down2:
            self.down()
        elif key == self._enter:
            return self.click()
        elif key == Key.esc:
            exit(-1)

    def update(self):
        os.system('cls')
        for index, i in enumerate(self.components.values()):
            if index == self.index:
                self._print_with_color(i, color=self.selected_color + self.selected_fore_color)
                self.current_selected = i
            else:
                if not i.enable:
                    self._print_with_color(i, color=Back.WHITE + Fore.LIGHTWHITE_EX)
                else:
                    print(i)

    def read(self):
        self.update()
        with Listener(on_press=self.on_press) as ls:
            ls.join()
            self.update()

            if not ls.running:
                self.current_selected.on_click()
                if type(self.current_selected) == self.stop_when_press:
                    return self.current_selected
                self.update()
                self.read()