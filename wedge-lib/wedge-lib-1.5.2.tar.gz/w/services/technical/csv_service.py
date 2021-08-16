import csv
from pathlib import Path

from w.services.abstract_service import AbstractService
from w.services.technical.filesystem_service import FilesystemService


class CsvService(AbstractService):
    @classmethod
    def is_csv(cls, filename):
        """ Check if filename is csv (from extension) """
        return FilesystemService.has_suffix(filename, ".csv")

    @classmethod
    def check_is_csv(cls, filename) -> Path:
        """
        Check if filename is csv (from extension) or raise RuntimeError
        """
        filename = FilesystemService.get_path(filename)
        if cls.is_csv(filename):
            return filename
        raise RuntimeError(f"{filename.name} is not a csv file")

    @classmethod
    def load(cls, csv_filename, mapping_columns) -> list:
        """
        Load csv file to list

        Args:
            csv_filename(str|Path): csv file
            mapping_columns(dict): csv header columns mapping to wanted attributes

        Returns:
            list: [{"<mapping name>": < row col value>, ...}, ...]

        Raises:
            RuntimeError :
                - filename is not csv
                - filename does not exists
                - incorrect or missing header
        """
        csv_filename = cls.check_is_csv(csv_filename)
        FilesystemService.check_file_exists(csv_filename)
        reader = csv.reader(csv_filename.open())
        required_headers = list(mapping_columns.keys())
        headers = [c for c in next(reader)]
        if required_headers != headers:
            raise RuntimeError(
                f"incorrect or missing header, expected '{';'.join(required_headers)}' "
                f"got '{';'.join(headers)}'"
            )
        return [
            {mapping_columns[headers[i]]: value for i, value in enumerate(row)}
            for row in reader
        ]

    @classmethod
    def dump(cls, csv_filename, mapping_columns, rows):
        """
        Dump rows into csv

        Args:
            csv_filename(str|Path): csv filename
            mapping_columns(dict): attributes to csv header columns mapping
            rows([dict]): list of rows [{"<mapping name>": <row col value>, ...}, ...]
        """
        with open(csv_filename, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=mapping_columns.values())
            writer.writeheader()
            for row in rows:
                csv_row = {
                    mapping_columns[k]: v
                    for k, v in row.items()
                    if k in mapping_columns
                }
                writer.writerow(csv_row)
