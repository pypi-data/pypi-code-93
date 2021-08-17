"""ColorItem is a dataclass containing one Color definition and color converters.

The object contains the following values:

* red: red component of color (integer)
* green: green component of color (integer)
* blue: blue component of color (integer)

Further, color format conversions - in between RGB, RGBA (integer representation)
and float representations - are provided.
"""

from dataclasses import dataclass

@dataclass
class ColorItem:
    """Color object (dataclass) for easy color handling.

    Parameters
    ----------
    red
        red color component. The native format is an integer 0-255
    green
        green color component. The native format is an integer 0-255
    blue
        blue color component. The native format is an integer 0-255
    """

    red: int
    green: int
    blue: int

    @property
    def color(self):
        """The `color` property return color as tuple.

        Returns
        -------
        tuple
            A tuple of 3 elements, red, green, blue. A red is returned
            as `(255, 0, 0)`
        """

        return (self.red, self.green, self.blue)

    @property
    def color_hex(self):
        """Return hexadecimal representation of color.

        Returns
        -------
        str
            Hexadecimal coded string. A red is returned as `#ff0000`
        """

        return "#{:02x}{:02x}{:02x}".format(self.red, self.green, self.blue)

    @property
    def complement(self):
        """Return complement (opposite) color tuple.

        Returns
        -------
        tuple
            Finds a complementing color to current, and returns it as a tuple.
            Our example red color - `(255, 0, 0)` is complemented by
            `(0, 255, 255)` - cyan.
        """

        def min_max(a, b, c):
            """inner function to find best delta for complementing color"""

            if c < b:
                b, c = c, b
            if b < a:
                a, b = b, a
            if c < b:
                b, c = c, b
            return a + c

        k = min_max(self.red, self.green, self.blue)
        return ColorItem(k - self.red, k - self.green, k - self.blue)

    def from_float(self, colrgb):
        """Convert a float RGB tuple the native format (int tuple)

        This method comes in handy, if you use libraries like 'Colour' in your
        code.

        The Colour library uses RGB float values, encoded in tuples ranging
        from 0.0-1.0. We convert these values to an int tuple, i.e. int values
        ranging from 0-255
        """

        self.red = int(255*colrgb[0])
        self.green = int(255*colrgb[1])
        self.blue = int(255*colrgb[2])
