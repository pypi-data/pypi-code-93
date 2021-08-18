"""
Formatting tools for outputting the Sheet data in various forms.
"""


class Formatter():
    """
    Base class for classes outputting Sheet data in a specific format.
    """

    def __init__(self, sheets):
        self.sheets = sheets

    def format(self):
        """
        Return the formatted data for all the sheets.
        """
        raise NotImplementedError("Must be implemented in subclasses")


class CSVFormatter(Formatter):
    """
    Formatter that returns the data as a string CSV format.
    """

    def format(self, separator=";"):
        """
        Return the fold locations as a CSV.

        The default separator is a semicolon (;), but this can be overridden.

        The returned data is in the following format:
            page; cut and fold point locations (cm)
            1; 11.025; 11.975
            3; 10; 12.75
        """
        # pylint: disable=arguments-differ

        if len(separator) == 1:
            separator = separator + " "
        header = separator.join(["page",
                                 "cut and fold point locations (cm)"])
        csv_lines = [header]
        for sheet in self.sheets:
            column_data = [sheet.page_number] + sheet.fold_locations_in_cm()
            column_data_strs = [str(field) for field in column_data]
            csv_lines.append(separator.join(column_data_strs))
        return "\n".join(csv_lines)
