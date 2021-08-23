"""Adapted from
https://github.com/navarasu/opencv-log/blob/master/cvtest/csv_reporter.py
"""

import csv
from pathlib import Path


class CsvReporter:
    def __init__(self, file_path):
        self.__file_path = file_path
        self.__fields = ["Test Image", "Result", "Message"]
        self.__create_file()

    def __create_file(self):
        # Make directory
        path = Path(self.__file_path)
        dir_path = path.parents[0]
        dir_path.mkdir(parents=True, exist_ok=True)
        # Make file
        with open(self.__file_path, "w") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(self.__fields)

    def __append(self, values):
        with open(self.__file_path, "a") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(values)

    def log_report(self, result):
        self.__append(result)
