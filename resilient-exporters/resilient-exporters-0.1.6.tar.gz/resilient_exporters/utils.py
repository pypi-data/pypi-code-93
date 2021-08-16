import shelve
import time
import queue
import random
import string
import math
import logging
import requests
from typing import Optional, Text, Union
from datetime import datetime
from .exceptions import DataTypeError
from collections import namedtuple

ColumnDescription = namedtuple("ColumnDescription",
                               ["col_name", "data_type", "ordinal_position",
                                "is_nullable", "precision"])
logger = logging.getLogger(__name__)

sql_datatypes_map = {
    "postgres": {
            "boolean": bool,
            "character varying": str,
            "varchar": str,
            "character": str,
            "char": str,
            "text": str,
            "real": float,
            "double precision": float,
            "decimal": float,
            "numeric": float,
            "money": float,
            "integer": int,
            "smallint": int,
            "bigint": int,
            "smallserial": int,
            "serial": int,
            "bigserial": int,
            "timestamp": datetime,
            "timestamp without time zone": datetime,
            "interval": str,
            "cidr": str,
            "inet": str,
            "macaddr": str,
            "macaddr8": str,
            "USER-DEFINED": str,
            "ARRAY": list
        }
}


def generate_rand_name() -> str:
    """Generate a random name of the form "export_XXXXXX" where XXXXXX are
    6 random characters.

    Returns:
        str: the generated name
    """
    suf = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"exporters_{suf}"


def is_able_to_connect(url: Optional[Text] = None) -> bool:
    """Runs a HTTP GET request to the url.

    Args:
        url (str): an URL (with its schema)

    Returns:
        bool: if a ConnectionError or Timeout are raised, returns `False`.
            `True`, otherwise.
    """
    if url is None:
        url = "https://www.google.com"
    try:
        _ = requests.get(url, timeout=.5)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False


def _stringify_sql(value):
    if isinstance(value, str):
        return f"'{value}'"
    elif value is None:
        return "NULL"
    else:
        return str(value)


def _transform_data_for_sql_query(data: Union[dict, tuple]):
    generator = enumerate(data) if isinstance(data, tuple) else data.items()
    for k, v in generator:
        if isinstance(v, bool):
            data[k] = "true" if v else "false"
        if isinstance(v, datetime):
            data[k] = str(v)
        if isinstance(v, float):
            if v == math.inf:
                data[k] = 'Infinity'
            elif v == -math.inf:
                data[k] = '-Infinity'
            elif math.isnan(v):
                data[k] = 'NaN'
        if isinstance(v, list):
            data[k] = str(v).replace("[", "{").replace("]", "}")

    columns = None
    if isinstance(data, dict):
        columns = ",".join(data.keys())

    values = ",".join([f"'{val}'" if isinstance(val, str) else _stringify_sql(val)
                        for val in data.values()])
    values = values.replace("None", "NULL")
    return columns, values


def _describe_postgres_column(col: tuple):
    """Input column is a tuple of the form:
        (table_name, column_name, data_type, ordinal_position, is_nullable,
        character_maximum_length, numeric_precision, datetime_precision)
    """
    if col[5]:
        precision = col[5]
    elif col[6]:
        precision = col[6]
    else:
        precision = col[7]

    try:
        data_type = sql_datatypes_map["postgres"][col[2]]
    except KeyError:
        logger.error(f"Data type not found in mapping: {col[2]}")
        data_type = None
    
    ordinal_position = col[3]
    is_nullable = True if col[4] == 'YES' else False

    return ColumnDescription(col[1], data_type, ordinal_position, is_nullable, precision)


def _validate_data_for_sql_table(data: dict, table: dict):
    """Validates data based on a table's schema.
    `table` is a dictionary where keys are column names and values are of the type 
    `resilient_exporters.utils.ColumnDescription`.
    """
    for key, val in data.items():
        if val is None:
            if not table[key].is_nullable:
                raise DataTypeError(message=f"Column '{key}' is not nullable, but \
                                              value provided is None.")
        elif not isinstance(val, table[key].data_type):
            raise DataTypeError(message=f"Invalid data type for '{key}'.")
        elif isinstance(val, str):
            if isinstance(table[key].precision, int):
                if len(val) > table[key].precision:
                    raise DataTypeError(message=f"String of chars too long for '{key}'. \
                                                  It must be {table[key][3]} chars maximum.")
    return


class _DataStore:
    __instantiated = 0
    __used_filenames = []

    def __new__(cls, *args, **kwargs):
        if "shelf_filename" in kwargs.keys():
            if kwargs["shelf_filename"] in cls.__used_filenames:
                raise ValueError(f"File {kwargs['shelf_filename']} is already \
                                 being used.")
        return super(_DataStore, cls).__new__(cls)

    def __init__(self,
                 use_memory: bool = True,
                 shelf_filename: Optional[Text] = None,
                 max_size: int = 100 * 100 * 100,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__use_memory = use_memory

        self.__filename = generate_rand_name() \
            if shelf_filename is None \
            else shelf_filename
        self.__used_filenames.append(self.__filename)

        self.__size = 0
        self.max_size = max_size

        self.__queue = queue.Queue() if use_memory else None
        self.__shelf = None if use_memory else shelve.open(self.__filename)

    @property
    def size(self):
        return self.__size

    @property
    def use_memory(self) -> bool:
        return self.__use_memory

    @use_memory.setter
    def use_memory(self, new_val: bool) -> bool:
        if self.__use_memory and new_val is False:
            self.export_queue_to_shelf()
            self.__use_memory = new_val
            self.__queue = None
        elif self.__use_memory is False and new_val:
            self.__queue = self.import_queue_from_shelf()
            self.__use_memory = new_val
            self.__shelf.close()
            self.__shelf = None
        else:
            print(f"WARNING - use_memory is already set to {new_val}")
        return new_val

    def put(self, data) -> bool:
        if self.size >= self.max_size:
            # Cannot save more data
            return False
        if self.use_memory:
            self.__put_in_memory(data)
        else:
            self.__put_in_shelf(data)
        self.__size += 1
        return True

    def __put_in_memory(self, data):
        self.__queue.put(data)

    def __put_in_shelf(self, data):
        self.__shelf[str(time.time())] = data

    def get(self):
        if self.size <= 0:
            raise Exception("No saved data left.")
        if self.use_memory:
            data = self.__get_from_memory()
        else:
            data = self.__get_from_shelf()
        self.__size -= 1
        return data

    def __get_from_memory(self):
        return self.__queue.get()

    def __get_from_shelf(self):
        generator = iter(self.__shelf.keys())
        try:
            key = next(generator)
        except StopIteration:
            return None
        else:
            res = self.__shelf[key].copy()
            del self.__shelf[key]
            return res

    def export_queue_to_shelf(self):
        self.__shelf = shelve.open(self.__filename, "n")
        while not self.__queue.empty():
            data = self.__queue.get()
            self.__shelf[str(time.time())] = data

    def import_queue_from_shelf(self):
        q = queue.Queue()
        generator = iter(self.__shelf.keys())
        for key in generator:
            q.put(self.__shelf[key])
        return q

    def __len__(self):
        return self.size

    def __iter__(self):
        return self

    def __next__(self):
        if self.size:
            return self.get()
        raise StopIteration

    def __del__(self):
        if self.__shelf:
            self.__shelf.close()
