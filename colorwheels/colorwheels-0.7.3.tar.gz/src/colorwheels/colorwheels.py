""" ``Colorwheels`` is a module to generate color sequences. A Colorwheels instance
contains multiple color wheel definitions and functions as a generator of color values
in multiple formats. You can activate any available colorwheel anytime, to obtain
different effects.
"""

import logging

from .colorwheels_config import ColorwheelsConfig
from .wheel_item import WheelItem

logger = logging.getLogger(__name__)

generator_types = ["rgb_tuple", "rgba_tuple", "hexadecimal"]

class Colorwheels():
    """Base class for returning color sequences.

    We represent colors similar to Color Wheels in photography, i.e. a sequence
    of colors is located on an imaginary wheel and endlessly served to applications
    in a given sequence.

    Colorwheels can be generated or loaded from a YAML file. See documentation and
    examples.
    """

    def __init__(self, add_base_colors=True):
        """Create ``Colorwheels`` instance.

        wheel configurations is a :doc:`colorwheels_config` object (singleton), which
        contains color definitions loaded from the environment, or generated
        by code.

        A default configuration object is created (or inherited from other
        parts of the code).
        """

        self.counter = 0
        self._generator_type = ""
        self.set_generator_type("rgb_tuple")

        self._wheel_configurations = ColorwheelsConfig()
        if add_base_colors:
            self.wheel_configurations.add_base_colors()

        self.active_wheel = None
        self.activate_colorwheel(self._wheel_configurations.first_wheel.name)

    def __str__(self):
        return (f"Colorwheels - available: {len(self._wheel_configurations._wheel_items)}, "
                f"active: '{self.active_wheel.name}'")

    @property
    def wheel_configurations(self):
        """Returns the configuration object :doc:`colorwheels_config`,
        used by Colorwheels

        You can manage the configurations from any Colorwheels instance used
        in your program. Handle with care! The configurator is a singleton, i.e.
        if you for example load a different set of colors, all running
        generators will be affected.
        """

        return self._wheel_configurations

    @property
    def active_colors(self):
        """Color list of active colorwheel.

        Exposes the active colorwheels color list for easy iteration"""

        return self.active_wheel.colors

    @property
    def active_name(self):
        """Currently active colorwheel name"""

        return self.active_wheel.name

# -- Generator Functions -----------------------------------------------------

    def __iter__(self):
        """Return the iterator"""

        return self

    def __next__(self):
        """Return next color element. The return value depends on
        generator_type"""

        if self._generator_type == "rgb_tuple":
            return self.next()
        if self._generator_type == "rgba_tuple":
            return self.next_rgba()
        if self._generator_type == "hexadecimal":
            return self.next_hex()

        raise ValueError(f"Unknown generator type '{self._generator_type}'")

    def _next_color_item(self):
        """Returns a next ColorItem available in active ColorWheel"""

        # this is the core method of all iterator flavors below
        color = self.active_wheel.colors[self.counter]
        self.counter += 1
        if self.counter >= len(self.active_wheel.colors):
            self.counter = 0
        return color

    def next(self):
        """Get the next color from the ColorWheel as an RGB tuple

        Returns
        -------
        tuple
            RGB tuple of next selected color. The returned value is an integer
            tuple representing a color, i.e. (r,g,b). Red would return (255,0,0)

        See Also
        --------
        next_rgba: Get the next color from ColorWheel using RGBA
        next_hex: Get the next color from ColorWheel as a hex string
        """

        color = self._next_color_item()
        return (color.red, color.green, color.blue)

    def next_rgba(self, alpha=255):
        """Get the next color from ColorWheel using RGBA

        Returns
        -------
        tuple
            RGB tuple of next selected color. The returned value is an integer
            tuple representing a color, i.e. (r,g,b,a). Red would return
            (255,0,0,255) if alpha is default at 255

        See Also
        --------
        next: Get the next color from the ColorWheel as an RGB tuple
        next_hex: Get the next color from ColorWheel as a hex string
        """

        color = self.next()
        color = color + (alpha,)
        return color

    def next_hex(self):
        """Get the next color from ColorWheel as a hex string

        Returns
        -------
        string
            hex string representation of RGB color

        See Also
        --------
        next: Get the next color from the ColorWheel as an RGB tuple
        next_rgba: Get the next color from ColorWheel using RGBA
        """

        color = self.next()
        return "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])

    def set_generator_type(self, new_type):
        """
        Set the generator type to a value out of generator_types.

        Raises
        ------
        ValueError
            Raises ValueError exception if new_type is not avaialble
        """

        if new_type not in generator_types:
            raise ValueError(f"Unknown generator type '{new_type}'")

        if new_type != self._generator_type:
            self._generator_type = new_type
            logger.info("Setting generator type to '%s'", self._generator_type)

    def activate_colorwheel(self, name):
        """Activates colorwheel by name, from configuration file. Sets
        active_wheel with new setting.

        Raises
        ------
        ValueError
            Raises ValueError exception if name is not found
        """

        self.counter = 0 # always reset counter
        self.active_wheel = self._wheel_configurations.find_wheel(name)

        if self.active_wheel is not None:
            logger.info("Activating wheel '%s'", name)
        else:
            message = f"Wheel '{name}' cannot be activated. Not found"
            logger.fatal(message)
            raise ValueError(message)

    def complement(self):
        """Use own colors to create a compementing color palette.

        Current colors are overwritten.

        Tip: to synchronize two colorwheels, create complements before
        using the generator(s)

        See Also
        --------
        rainbow: You can also change the generator colors by creating a
            rainbow effect
        """

        new_wheel_item = WheelItem.complement_wheel_item(self.active_wheel)
        self.active_wheel = new_wheel_item

    def rainbow(self, size):
        """Generate rainbow color palette, using defaults.

        Current colors are overwritten. A new, suitable name is generated.

        Tip: to generate rainbow effects with more options, use the related
        rainbow class method from wheel_item

        Parameters
        ----------
        size:
            number of rainbow colors to be generated

        See Also
        --------
        complement: You can also change the generator colors by replacing
            current colors with complementing colors
        """

        new_name = f"rainbow_{size}"
        new_wheel_item = WheelItem.rainbow_wheel_item(new_name, size)
        self.active_wheel = new_wheel_item
