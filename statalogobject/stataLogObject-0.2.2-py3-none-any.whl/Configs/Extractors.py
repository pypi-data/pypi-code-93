from stataLogObject.Supports import clean_value
from stataLogObject.Configs import Entry

from dataclasses import dataclass, field
from typing import List


@dataclass
class ExtractTable:
    """
    | Contains the information needed for extraction
    |
    | *Attributes*:
    |    **divider (list)**: The divider to isolate the elements
    |    **separator (int)**: The number of spaces allowed before the table is considered finished and is saved
    |    **skip_indexes** (Optional[list]):  Option list of elements found in the log needs to have certain elements
    |   skipped

    """
    divider: List
    separator: int
    skip_indexes: List = field(default_factory=lambda: [])


@dataclass
class ExtractBody:
    body_type: Entry
    skip_lines: int = 0
    skip_indexes: List = field(default_factory=lambda: [])

    def extract_body(self, raw):
        """
        This extracts the body of the table by looking for the stata dividers and then parsing out the unique elements.
        Use the first element of the first line as the phenotype, and then return the rest as column headers will be set
        based on table type.

        :return: A str of the phenotype and a list of TableEntry
        :rtype: (str, list[TableEntry])
        """
        self._format_indexes(len(raw))

        # Isolate results with tables based on table line delimiters, skip indexes in the skip_indexes if provided
        result_indexes = [i for i, line in enumerate(raw) if ("|" in line) and (i not in self.skip_indexes)]

        # Isolate these lines without the table line elements
        body_lines = self._extract_body_lines(raw, result_indexes)

        # # Extract the variable names, with the first one always being the phenotype/outcome
        phenotype = body_lines[0][0]

        # Return the phenotype, variable names, and the table bodies formatted values
        return phenotype, self._create_table_entries(body_lines)

    def _format_indexes(self, table_length):
        """
        We may need to subtract indexes from the bottom, in which case the index is relative to the table length

        Note
        ----
        Table length is not base zero, hence why we need to take one way from it
        negative skip indexes are formatted in the same way as indexing, so -1 retrieves the last element. However, if
            we take the index of -1 from the table length then we always skip the second to last element. We can't use
            zero, as zero is an actual index for the first element. As such, each negative value gets +1 added to it.
        """
        self.skip_indexes = [v if v >= 0 else (table_length - 1) + (v + 1) for v in self.skip_indexes]

    def _extract_body_lines(self, raw, result_indexes):
        """
        This will strip out the lines without the table line elements.

        :param result_indexes: The indexes of the results table
        :type result_indexes: list[int]

        :return: A list of each row that is in the table body
        :rtype: list[list[str]]
        """
        body_lines = []
        for index, line in enumerate(raw):
            # TODO: This feels like a very strange if statement...
            if min(result_indexes) + self.skip_lines <= index and index in result_indexes:

                # Not all regression types will be without blanks, so this only adds rows that where the value is more
                # than just he name of the variable
                values_stripped = [value for value in line if value != "|"]
                if len(values_stripped) > 1:
                    body_lines.append(values_stripped)

                    # Most tables end with _cons so we can stop after this point
                    if values_stripped[0] == "_cons":
                        break
        return body_lines

    def _create_table_entries(self, body_lines):
        """Clean the values which are not the table header, create Entry of type Body_Type for each line accordingly"""
        return [self.body_type.create_entry(line) for line in self._limit_var_names(body_lines)]

    def _limit_var_names(self, body_lines):
        """
        Extract the values then format them

        Note
        ----
        After extracting the values, it is possible that space seperated names may lead to more elements in a row than
        there are columns to accept them. Here after extracting the values, we format them relative to the length of
        table headers

        :param body_lines: Each line from the body that is a variable result
        :type body_lines: list[list[str]]

        :return: Formatted lines
        :rtype: list[list]
        """
        lines = [[clean_value(value) for value in line] for line in body_lines[1:]]
        return [line if len(line) == len(self.body_type.entry_names) else self._line_format(line) for line in lines]

    def _line_format(self, line):
        """Format line relative to the number of table headers"""
        values = line[-(len(self.body_type.entry_names) - 1):]
        var_name = "_".join(line[:-(len(self.body_type.entry_names) - 1)])
        return [var_name] + values
