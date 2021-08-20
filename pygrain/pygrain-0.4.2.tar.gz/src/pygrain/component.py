import pygame
from collections import defaultdict


class Component:
    """
    Superclass for UI components.
    """

    def __init__(self, parent, x=0, y=0, font_color=(0, 0, 0),
                 bg_colour=(255, 255, 255), border_color=(0, 0, 0),
                 border_thickness=1, font_size=20, width=1, height=1,
                 colour=(0, 0, 0), draggable=False, fixed_x=False, fixed_y=False,
                 min_x=None, min_y=None, max_x=None, max_y=None, free_x=False,
                 free_y=False, free=False, invisible=False, scrollable=True,
                 resizeable=False):
        """

        :param parent: parent component or app
        :param x: relative from parent
        :param y: relative from parent
        :param font_color:
        :param bg_colour:
        :param border_color:
        :param border_thickness:
        :param font_size:
        :param width:
        :param height:
        :param colour:
        :param draggable:
        :param fixed_x: x-coordinate can't be modified
        :param fixed_y: y-coordinate can't be modified
        :param min_x:
        :param min_y:
        :param max_x:
        :param max_y:
        :param free: A free component can be moved outside the parent component
        :param invisible: An invisible component is not drawn
        """
        self.components = []
        self.parent = parent
        self.parent.add_component(self)
        self.x = x
        self.y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_colour = font_color
        self.bg_colour = bg_colour
        self.border_colour = border_color
        self.border_thickness = border_thickness
        self.font_size = font_size
        self.colour = colour
        self.actions = {}
        self.dragging = False
        self.drag_offset_x, self.drag_offset_y = 0, 0
        self.fixed_x = fixed_x
        self.fixed_y = fixed_y
        self.min_x = min_x
        self.free = free
        self.invisible = invisible
        self.free_x = free_x
        self.free_y = free_y
        self.scrollable = scrollable

        if self.min_x is None:
            self.min_x = 0
        self.min_y = min_y
        if self.min_y is None:
            self.min_y = 0
        self.max_x = max_x
        if self.max_x is None:
            self.max_x = lambda: self.parent.width
        self.max_y = max_y
        if self.max_y is None:
            self.max_y = lambda: self.parent.height

        if draggable:
            self.bind_drag_events()

        self.resizeable = resizeable

        from .point import Point
        from .box import Box
        if resizeable:
            self.resize_point = Point(self,
                                      center_x=self.get_property('width'),
                                      center_y=self.get_property('height'),
                                      draggable=True, free_x=True, free_y=True,
                                      radius=10, invisible=True, scrollable=False)

            self.bottom_bar = Box(self, x=0,
                                  y=self.get_property('height'),
                                  fixed_x=True,
                                  width=lambda: self.get_property('width'),
                                  height=10,
                                  invisible=True,
                                  free_y=True,
                                  draggable=True,
                                  scrollable=False)

            self.bind('always', lambda target: self.resize())

    def get_parent(self):
        """
        Return this component's parent component (or App)
        :return: parent component
        """
        return self.parent

    def draw(self, screen):
        """
        Draw component based on defined properties.
        :param screen:
        :return: None
        """
        if self.get_property('invisible'):
            return

        x, y = self.get_abs_x(), self.get_abs_y()
        bg_colour = self.get_property('bg_colour')
        width = self.get_property('width')
        height = self.get_property('height')
        # Background rectangle
        pygame.draw.rect(screen, bg_colour,
                         (x, y, width, height))
        # Border
        pygame.draw.rect(screen, self.border_colour,
                         (x, y, width, height),
                         width=self.border_thickness)

        for component in self.components:
            component.draw(screen)

    def valid_event(self, events, events_done):
        """
        Return true if events is intended for this component.
        :param events_done:
        :param events: set of events names
        :return: bool
        """
        for event in events:
            if event in events_done:
                return False
        if 'click' in events:
            if not self.mouseover():
                return False

        return True

    def event(self, events, events_done=None):
        """
        Call callback function for a given binding that is a subset of the
        current event.
        :param events_done:
        :param events: set of event names
        :return: None

        Pass events to all sub-components inside the frame.
        :param events_done:
        :param events:
        :return: if events was valid for any component
        """
        if events_done is None:
            events_done = set()

        for component in self.components[::-1]:
            component.event(events, events_done=events_done)

        events = frozenset(events)
        called = False
        for curr in self.actions:
            if curr.issubset(events) and self.valid_event(events, events_done):
                for action in self.actions[curr]:
                    called = action(self) or called
        if called:
            for event in events:
                events_done.add(event)

        return called

    def get_x(self):
        """
        Calculate absolute x coordinate of component.
        :return: int/float
        """
        x = self.get_property('x')
        free_x = self.get_property('free_x')
        if free_x:
            return x

        min_x = self.get_property('min_x')
        width = self.get_property('width')
        max_x = self.get_property('max_x')
        if min_x is not None and x < min_x:
            x = self.min_x
        if max_x is not None and x + width > max_x:
            x = max_x - width
        return x

    def set_x(self, x):
        free_x = self.get_property('free_x')
        if free_x:
            self.set_property('x', x)
            return

        fixed_x = self.get_property('fixed_x')
        min_x = self.get_property('min_x')
        width = self.get_property('width')
        max_x = self.get_property('max_x')
        if fixed_x:
            return
        if min_x is not None and x < min_x:
            x = self.min_x
        if max_x is not None and x + width > max_x:
            x = max_x - width
        self.set_property('x', x)

    def get_y(self):
        """
        Calculate absolute y coordinate of component.
        :return: int/float
        """
        y = self.get_property('y')
        free_y = self.get_property('free_y')
        if free_y:
            return y
        min_y = self.get_property('min_y')
        height = self.get_property('height')
        max_y = self.get_property('max_y')

        if min_y is not None and y < min_y:
            y = min_y
        if max_y is not None and y + height > max_y:
            y = max_y - height

        return y

    def set_y(self, y):
        free_y = self.get_property('free_y')
        if free_y:
            self.set_property('y', y)
            return

        fixed_y = self.get_property('fixed_y')
        min_y = self.get_property('min_y')
        height = self.get_property('height')
        max_y = self.get_property('max_y')
        if fixed_y:
            return
        if min_y is not None and y < min_y:
            y = min_y
        if max_y is not None and y + height > max_y:
            y = max_y - height

        self.set_property('y', y)

    def set_width(self, width):
        """
        Set width of component and signal parent component to update display.
        :param width:
        :return: None
        """
        self.width = width

        self.resize_point.set_center_x(width)
        self.parent.update()

    def get_property(self, name):
        """
        Return value of property given name.
        :param name:
        :return:
        """
        prop = self.__getattribute__(name)
        while callable(prop):
            prop = prop()

        return prop

    def get_properties(self, names):
        return tuple(map(lambda name: self.get_property(name), names))

    def set_properties(self, names, values):
        for i in range(len(names)):
            self.set_property(names[i], values[i])

    def set_property(self, name, value):
        """
        Set value of property given name and signal parent to update display.
        :param name:
        :param value:
        :return:
        """
        self.__setattr__(name, value)
        self.parent.update()

    def get_action(self, events):
        """
        Return callback function associated with events combination.
        :param events: set of events names
        :return:
        """
        return self.actions[events]

    def bind(self, events, func):
        """
        Add mapping for events combination in actions dict.
        :param self:
        :param events: set of events names
        :param func: callback function when events occurs
        :return:
        """
        if not isinstance(events, set):
            events = {events}

        if frozenset(events) not in self.actions:
            self.actions[frozenset(events)] = []

        self.actions[frozenset(events)].append(func)

    def mouseover(self):
        """
        Return true if mouse is inside component's region.
        :return:
        """
        for component in self.components:
            if component.mouseover():
                return True
        x, y = pygame.mouse.get_pos()
        width, height = self.get_property('width'), self.get_property('height')
        return (
                self.get_abs_x() <= x <= self.get_abs_x() + width and
                self.get_abs_y() <= y <= self.get_abs_y() + height
        )

    def set_dragging(self):
        """
        Calculate distances between current position of mouse and
        top left (or centre) of the component.
        :return:
        """
        self.dragging = True
        x, y = pygame.mouse.get_pos()
        self.drag_offset_x = x - self.get_abs_x()
        self.drag_offset_y = y - self.get_abs_y()

        return True

    def reset_dragging(self):
        """
        Sets self.dragging to false.
        Return true if self.dragging was true.
        :return:
        """
        original = self.dragging
        self.dragging = False
        return original

    def drag_position(self):
        """
        If component is being dragged then the relative x, y coordinates
        are set using the current position of the mouse and the offsets of
        the mouse from the component when the user clicked on the component.
        :return:
        """

        if not self.dragging:
            return False

        x, y = pygame.mouse.get_pos()
        self.set_x(x - self.get_parent().get_abs_x() - self.drag_offset_x)
        self.set_y(y - self.get_parent().get_abs_y() - self.drag_offset_y)

        self.parent.update()

        return True

    def bind_drag_events(self):
        """
        Binds actions for dragging component.
        :return:
        """
        self.bind('left click', lambda target: self.set_dragging())
        self.bind('left up', lambda target: self.reset_dragging())
        self.bind('mousemotion', lambda target: self.drag_position())

    def update(self):
        self.parent.update()

    def switch_frame(self, frame):
        self.parent.switch_frame(frame)

    def get_abs_x(self):
        return self.parent.get_abs_x() + self.get_x()

    def get_abs_y(self):
        return self.parent.get_abs_y() + self.get_y()

    def is_invisible(self):
        return self.get_property('invisible')

    def is_scrollable(self):
        return self.get_property('scrollable')

    def resize(self):
        if self.resize_point.dragging:
            width, height = self.resize_point.get_center_x(), \
                            self.resize_point.get_center_y()
            self.width, self.height = width, height
            self.bottom_bar.y = height
            self.update()
            return True

        elif self.bottom_bar.dragging:
            y = self.bottom_bar.y
            self.height = y
            self.resize_point.set_center_y(y)
            self.update()
            return True

        return False

    def add_component(self, component):
        self.components.append(component)

    def get_components(self):
        return self.components
