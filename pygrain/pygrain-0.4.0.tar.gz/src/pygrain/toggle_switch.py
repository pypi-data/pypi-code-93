from .button import Button


class ToggleSwitch(Button):
    """
    Button to switch between given values.
    """
    def __init__(self, parent, values=[], **kwargs):
        super().__init__(parent, text=values[0], **kwargs)
        self.values = values
        self.curr = 0
        self.on_left_click(func=lambda target: self.next_value())

    def next_value(self):
        """
        Increments curr (wraps to start) and updates text in button.
        :return:
        """
        self.curr = (self.curr + 1) % len(self.values)
        self.set_property('text', self.get_values()[self.get_curr()])
        self.parent.update()

    def get_values(self):
        """
        Return list of values.
        :return:
        """
        return self.values

    def get_curr(self):
        """
        Return index of current value.
        :return:
        """
        return self.curr

    def get_value(self):
        """
        Current value of button.
        :return:
        """
        return self.values[self.curr]