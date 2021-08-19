from .scroll_bar import ScrollBar
from .box import Box


class VerticalScrollBar(ScrollBar):
    def __init__(self, parent, scroll_height, **kwargs):
        """

        :param parent:
        :param scroll_height:
        :param kwargs:
        """
        super().__init__(parent,
                         x=lambda: parent.get_property('width') * 0.98,
                         width=lambda: parent.get_property('width') * 0.02,
                         height=lambda: parent.get_property('height'),
                         border_thickness=2,
                         fixed_x=True,
                         scrollable=False,
                         **kwargs)
        self.scroll_height = scroll_height
        self.box = Box(self, x=0, y=0,
                       width=lambda: self.get_property('width'),
                       height=lambda: self.get_property('height') * parent.get_property('height') / self.get_property('scroll_height'),
                       bg_colour=(100, 100, 100),
                       draggable=True,
                       fixed_x=True)
        self.previous_y = 0
        super().bind_scroll_events()

    def scroll(self):
        """

        :return:
        """
        y = self.box.get_property('y')
        previous_y = self.get_property('previous_y')
        if y == previous_y:
            return False
        height = self.get_property('height')
        scroll_height = self.get_property('scroll_height')

        dy = (y - previous_y) * (scroll_height / height)
        self.set_previous_y(y)

        for component in self.parent.get_components():
            if not component.is_scrollable():
                continue
            y = component.get_property('y')
            component.set_y(y - dy)

        return True

    def scroll_up(self):
        """

        :return:
        """
        y = self.box.get_property('y')
        height = self.get_property('height')

        self.box.set_y(y - 0.05 * height)
        self.scroll()

    def scroll_down(self):
        """

        :return:
        """
        y = self.box.get_property('y')
        height = self.get_property('height')

        self.box.set_y(y + 0.05 * height)
        self.scroll()

    def set_previous_y(self, y):
        self.previous_y = y
        return self
