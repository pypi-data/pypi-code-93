from .frame import Frame
from .point import Point
import pygame
from .util import show_text


class ValueSlider(Frame):
    """
    Slider component to select values in a range.
    """
    def __init__(self, parent, start=0, end=10, step=None, default=None,
                 **kwargs):
        """

        :param parent:
        :param start: minimum value
        :param end: maximum value
        :param step: to only allow discrete values at given interval
        :param default: initial value of slider
        :param kwargs:
        """
        assert start < end
        super().__init__(parent, **kwargs)
        self.start = start
        self.end = end
        self.step = step
        self.default = default
        height = self.get_property('height')

        self.point = Point(self, center_y=(height / 2),
                           draggable=True, fixed_y=True, min_x=0, max_x=self.width,
                           radius=10)
        self.point.bind('left up', lambda target: self.set_position())

        if self.default is None:
            # Default value is halfway
            self.default = (self.start + self.end) / 2
        # Set default position of point
        self.set_position(value=self.default)

    def draw(self, screen):
        super().draw(screen)
        # Draw line of slider
        width, height = self.get_properties(['width', 'height'])
        pygame.draw.line(screen, (0, 0, 0),
                         (self.get_abs_x(), self.get_abs_y() + height / 2),
                         (self.get_abs_x() + width, self.get_abs_y() + height / 2),
                         2)
        # Draw point
        self.point.set_center_y(height / 2)
        self.point.draw(screen)
        # Display current value of slider
        show_text(screen, str(round(self.get_value(), 2)),
                  x=(self.get_abs_x() + width / 2), y=self.get_abs_y(), font_size=30)
        # Update screen
        self.update()

    def set_position(self, value=None):
        """
        Set position of slider point based on given value or
        current value of slider after rounding.
        :param value:
        :return:
        """
        if value is None:
            value = self.get_value()

        diff = value - self.start
        value_range = self.end - self.start
        # Set x-coordinate of slider point
        width = self.get_property('width')
        self.point.set_property('x', width * (diff / value_range))

    def get_value(self):
        """
        Calculates current value of slider using the step to round.
        :return:
        """
        # Amount to increment from start
        width = self.get_property('width')
        x = self.point.get_property('x')
        start, end, step = self.get_properties(['start', 'end', 'step'])
        offset = (end - start) * (x / width)

        if step is not None:
            # Adjust offset to nearest step multiple
            quot = round(offset / step)
            offset = quot * step

        # Current value
        start = self.get_property('start')
        value = start + offset

        return value
