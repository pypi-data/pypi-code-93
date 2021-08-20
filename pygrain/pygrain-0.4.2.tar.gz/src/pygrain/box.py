from .component import Component


class Box(Component):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)