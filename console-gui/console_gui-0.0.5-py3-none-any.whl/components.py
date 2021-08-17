import os
from colorama import Back, Fore
from gui.reader import Reader

class Component:
    def __init__(self, name, click, enable=True, **kwargs):
        self.name = name
        self.click = click
        self.kwargs = kwargs
        self.enable = enable
        self.reader = None
        self.back_color = kwargs.get('back_color', Reader.default_back_color)
        self.fore_color = kwargs.get('fore_color', Reader.default_fore_color)

    def on_click(self):
        if self.click is not None:
            self.click(self)

    def config(self, click=None, enable=None, **kwargs):
        if click is None:
            click = self.click
        if enable is None:
            enable = self.enable
        back = kwargs.get('back_color', self.back_color)
        fore = kwargs.get('fore_color', self.fore_color)

        self.__init__(self.name, click, enable, back_color=back, fore_color=fore, **kwargs)

    def __call__(self, *args, **kwargs):
        self.on_click()


    def __str__(self): return self.name

class Button(Component):
    def __init__(self, name, click, enable=True, **kwargs):
        super().__init__(name, click, enable, **kwargs)
        self.content = kwargs.get('content', name)

    def __str__(self):
        return self.content

class Field(Component):
    def __init__(self, name, click, enable=True, readonly=False, **kwargs):
        super().__init__(name, click, enable, **kwargs)
        self.text = kwargs.get('text', name)
        self.readonly = readonly

    def config(self, click=None, enable=None, **kwargs):
        if click is None:
            click = self.click
        if enable is None:
            enable = self.enable

        back = kwargs.get('back_color', self.back_color)
        fore = kwargs.get('fore_color', self.fore_color)

        self.__init__(self.name,
                      click,
                      enable,
                      back_color=back,
                      fore_color=fore,
                      readonly=kwargs.get('readonly', self.readonly),
                      **kwargs)

    def __str__(self):
        return self.text

    def on_click(self):
        if self.readonly:
            return None

        input('')
        os.system('cls')
        response = input(f'{self.kwargs.get("title", f"{self.name}:{self.text}")}> ')

        if self.kwargs.get('change_text', True):
            self.text = response
        self.click(self)
        os.system('cls')
