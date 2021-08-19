from typing import Dict, Any, List, Union
import os
import csv
from pathlib import Path
from loguru import logger
from parqser.saver import BaseSaver


class CSVSaver(BaseSaver):
    def __init__(self, path: str, columns: List[str] = [], sep=','):
        self._check_dir_exists(path)
        self.path = path
        self.sep = sep
        self.columns = self._validate_file_columns(path, sep, columns)

    def _check_dir_exists(self, path: str):
        path = Path(path).parent
        if not os.path.exists(path):
            raise AttributeError(f'Cant get given file. Path {path} doesnt exist')

    def _validate_file_columns(self, path: str, sep: str, columns: List[str]) -> Union[None, List[str]]:
        """If file exists, checks if file columns matches with given columns"""
        if os.path.exists(path):
            readen_columns = open(path).readline().strip().split(sep)
            if not len(columns):
                # Use columns from file
                columns = readen_columns
            elif columns != readen_columns:
                raise AttributeError(f'given columns doesnt match with columns in file {path}')

        else:
            if not len(columns):
                logger.warning('No columns given. Csv header will be determined by first record keys')
                columns = None
        return columns

    def save(self, params: Dict[str, Any]):
        self.save_batch([params])

    def save_batch(self, params: List[Dict[str, Any]]):
        if len(params) == 0:
            raise AttributeError('Records batch shouldnt be empty')

        with open(self.path, 'a') as f:
            writer = csv.writer(f, delimiter=self.sep, quotechar='"')
            if self.columns is None:
                # use first record columns as header
                self.columns = sorted(params[0].keys())
                writer.writerow(self.columns)

            if not all(map(lambda params: set(params.keys()) == set(self.columns), params)):
                raise AttributeError(f'Unexpected columns in batch. Only columns {", ".join(self.columns)} should be used')

            for param in params:
                # order values
                values = [str(param[col]) for col in self.columns]
                writer.writerow(values)
