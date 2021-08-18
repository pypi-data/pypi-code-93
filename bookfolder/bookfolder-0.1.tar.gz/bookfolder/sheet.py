"""
Representation of a sheet of paper in a book.
"""


class Sheet():
    """
    A sheet of book in a bookfolding sculpture.

    The locations of the folds are internally handled in "page coordinates",
    the separation of which is determined by `measurement_interval`.
    """

    def __init__(self, fold_locations, measurement_interval, page_number):
        """
        Create a new bookfolding sheet.

        :fold_locations: Locations of the folds on this page shown on page
                         coordinates.
        :measurement_interval: Length of a page coordinate unit in millimeters.
        """
        self.folds = fold_locations.copy()
        self.folds.sort()
        self.measurement_interval = measurement_interval
        self.page_number = page_number

    def fold_locations_in_mm(self):
        """
        Return a list of fold locations in millimeters.
        """
        decimals = self._decimal_places(self.measurement_interval)
        return [round(fold_index * self.measurement_interval, decimals)
                for fold_index in self.folds]

    def fold_locations_in_cm(self):
        """
        Return a list of fold locations in centimeters.
        """
        decimals = self._decimal_places(self.measurement_interval)
        return [round(fold_index * self.measurement_interval * 0.1, decimals+1)
                for fold_index in self.folds]

    def _decimal_places(self, float_number):
        """
        Return the number of digits after the decimal point.
        """
        # pylint: disable=no-self-use
        number_str = str(float_number)
        return number_str[::-1].find('.')
