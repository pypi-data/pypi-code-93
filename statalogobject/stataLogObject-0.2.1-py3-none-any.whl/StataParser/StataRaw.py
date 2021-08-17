from stataLogObject.Configs import ExtractTable
from stataLogObject.Supports import clean_line

from pathlib import Path


class StataRaw:
    def __init__(self, log_path, isolator):
        """

        :param log_path: The path to the log file
        :type log_path: Path

        :param isolator: The Extraction elements for this table, contains dividers, space count and skip indexes
        :type isolator: ExtractTable
        """

        # Initializers
        self._log_path = log_path
        self._iso = isolator

        # Raw table that has been extracted
        self.raw_tables = [self._extract_raw_table(i) for i in self._find_start_indexes()]

    def __repr__(self):
        """Human readable output"""
        return f"StataRaw with {len(self.raw_tables)} tables"

    def _find_start_indexes(self):
        """
        Find the starting indexes from the log file where the line matches the divider
        """
        with open(self._log_path, "r") as log_file:
            return [index for index, line in enumerate(log_file) if self._evaluate_start_line(line)]

    def _evaluate_start_line(self, line):
        """Evaluate if the cleaned start line, minus elements in skip_indexes, equals the divider"""
        return [v for i, v in enumerate(clean_line(line)) if i not in self._iso.skip_indexes] == self._iso.divider

    def _extract_raw_table(self, index):
        """
        For each given start index, isolate the elements of this table given the space_count

        :param index: The current start index of the file lines
        :type index: int

        :return: The list of all the rows that are relevant to this table
        :rtype: list
        """
        # Set the per table iterable elements
        current_element = []
        spacer = 0

        with open(self._log_path, "r") as log_file:

            # Skip the lines we don't need for this table index
            [log_file.readline() for _ in range(index)]

            for index, line in enumerate(log_file):
                # Convert the string line with regular expressions into a list of space separated items.
                cleaned = clean_line(line)

                # If we find an empty line, and we have reached the limited of empty lines we are allowed to find
                if (len(cleaned) == 0) and (spacer == self._iso.separator) and (len(current_element) > 0):
                    return current_element

                # Otherwise if the line is empty but less than the allowed maximum, iterate the found empty upwards
                elif len(cleaned) == 0 and spacer < self._iso.separator:
                    spacer += 1

                # If we are currently within a table then append to current_element
                else:
                    current_element.append(cleaned)
        return current_element
