from .component import Component
from .util import show_text, get_text_size


class TextBox(Component):
    """
    Component to display text.
    """
    def __init__(self, parent, text='', padding=None, pad_left=0, pad_right=0,
                 pad_top=0, pad_bottom=0, font_size=20, **kwargs):
        self.text = text
        self.pad_left = pad_left
        self.pad_right = pad_right
        self.pad_top = pad_top
        self.pad_bottom = pad_bottom
        width, height = get_text_size(self.get_text(), font_size=font_size)
        super().__init__(parent, width=width, height=height, **kwargs)
        if padding is not None:
            self.pad_left = self.pad_right = padding
            self.pad_top = self.pad_bottom = padding

    def draw(self, screen):
        """
        Draw textbox with text.
        :param screen:
        :return:
        """

        x, y = self.get_abs_x(), self.get_abs_y()
        font_size = self.get_property('font_size')
        min_width, min_height = get_text_size(self.get_text(), font_size=font_size)
        width, height = self.get_properties(['width', 'height'])
        pad_left, pad_right = self.get_properties(['pad_left', 'pad_right'])
        pad_top, pad_bottom = self.get_properties(['pad_top', 'pad_bottom'])
        text = self.get_text()

        super().draw(screen)
        font_size = self.get_property('font_size')
        show_text(screen, text, x + width / 2, y + height / 2,
                  font_size=font_size)

        return self

    def get_text(self):
        """
        Return text if it is a string or call function that returns text.
        :return:
        """
        return self.get_property('text')



