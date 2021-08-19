from .frame import Frame


class ScrollBar(Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

    def draw(self, screen):
        """

        :param screen:
        :return:
        """
        super().draw(screen)
        self.box.draw(screen)

    def scroll(self):
        pass

    def scroll_up(self):
        pass

    def scroll_down(self):
        pass

    def bind_scroll_events(self):
        """

        :return:
        """
        self.box.bind('mousemotion', lambda target: self.scroll())
        parent = self.get_parent()
        parent.bind('scroll up', lambda target: self.scroll_up())
        parent.bind('scroll down', lambda target: self.scroll_down())
