from .scroll_bar import ScrollBar
from .box import Box


class HorizontalScrollBar(ScrollBar):
    def __init__(self, parent, scroll_width, **kwargs):
        super().__init__(parent,
                         x=0,
                         y=lambda: parent.get_property('height') * 0.98,
                         height=lambda: parent.get_property('height') * 0.02,
                         width=lambda: parent.get_property('width'),
                         border_thickness=2,
                         fixed_y=True,
                         scrollable=False,
                         **kwargs)
        self.scroll_width = scroll_width
        self.box = Box(self, x=0, y=0,
                       height=lambda: self.get_property('height'),
                       width=lambda: self.get_property('width') * parent.get_property('width') / self.get_property(
                           'scroll_width'),
                       bg_colour=(100, 100, 100),
                       draggable=True,
                       fixed_y=True)
        self.previous_x = 0
        super().bind_scroll_events()

    def scroll(self):
        x = self.box.get_property('x')
        previous_x = self.get_property('previous_x')
        if x == previous_x:
            return False

        width = self.get_property('width')
        scroll_width = self.get_property('scroll_width')
        dx = (x - previous_x) * (scroll_width / width)
        self.set_previous_x(x)

        for component in self.parent.get_components():
            if not component.is_scrollable():
                continue
            x = component.get_property('x')
            component.set_x(x - dx)

        return True

    def set_previous_x(self, x):
        self.previous_x = x
        return self
