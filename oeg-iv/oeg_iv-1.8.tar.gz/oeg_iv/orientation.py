"""Orientation object."""
import math


class Error(Exception):
    """Orientation exception."""

    pass


class Orientation:
    """Orientation units conversions."""

    def __init__(self, hours, minutes):
        """Construct object from integer hours and minutes."""
        if not(0 <= hours <= 12):
            raise Error("Wrong hours: {}. Must be 0-12".format(hours))

        if not(0 <= minutes <= 59):
            raise Error("Wrong minutes: {}. Must be 0-59".format(minutes))

        self.hours = hours
        self.minutes = minutes

    def __unicode__(self):
        """Return orientation string in IV csv format."""
        hours = int(self.hours)
        if hours == 0:
            hours = '12'

        minutes = self.minutes
        if minutes < 10:
            minutes = '0{}'.format(minutes)

        return "{},{}".format(hours, minutes)

    def __str__(self):
        """Same as __unicode__."""
        return self.__unicode__()

    @classmethod
    def from_hour_float(cls, hour_float):
        """Construct object from hours as float."""
        parttial_hour, hours = math.modf(hour_float)
        minutes = parttial_hour * 60
        return cls(int(hours), int(minutes))

    @classmethod
    def from_minutes(cls, minutes):
        """Construct object from integer minutes."""
        return cls(minutes / 60, minutes % 60)


def from_infotech_html(text):
    """Return orientation from infotech string."""
    return Orientation.from_hour_float(float(text.replace(',', '.')))
