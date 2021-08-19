from .component import Component


class Frame(Component):
    """
    Class for a collection of components.
    """
    def __init__(self, parent, **kwargs):
        self.components = []
        super().__init__(parent, **kwargs)
        parent.switch_frame(self)

