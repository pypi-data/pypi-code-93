from .component import Component
from .util import show_text


class Button(Component):
    """
    Component for button.
    """
    def __init__(self, parent, x=0, y=0, text='', **kwargs):
        super().__init__(parent, x=x, y=y, **kwargs)
        self.text = text

    def on_left_click(self, func):
        """
        Bind component to left click.
        :param func:
        :return: self
        """
        self.bind({'left click'}, func)
        return self

    def on_right_click(self, func):
        """
        Bind component to right click.
        :param func:
        :return: self
        """
        self.bind({'right click'}, func)
        return self

    def on_middle_click(self, func):
        """
        Bind component to middle click.
        :param func:
        :return: self
        """
        self.bind({'middle click'}, func)
        return self

    def draw(self, screen):
        """
        Draw button.
        :param screen:
        :return: None
        """
        x, y = self.get_abs_x(), self.get_abs_y()

        super().draw(screen)
        # Button text
        show_text(screen, self.get_text(), x + self.width / 2,
                  y + self.height / 2, font_size=self.font_size)

    def set_text(self, text):
        """
        Set 'text' property.
        :param text:
        :return:
        """
        self.set_property('text', text)

    def get_text(self):
        """
        Return 'text' property.
        :return: string
        """
        return self.get_property('text')

