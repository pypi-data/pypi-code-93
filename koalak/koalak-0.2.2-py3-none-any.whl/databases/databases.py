import os
from typing import Any

"""
databases
- list
    - txt
    - json
    - csv
- key_value_db
    - json (dict)
- txt (list)
- json
- csv

existing light db (without port connection) ie using file
- sqlite
- text/csv/json
- tinydb
- dataset
- pickledb
- shelve (stdlib)
- dbm (key/value)
https://docs.python.org/3/library/persistence.html
"""


class Database:
    pass


class KeyValueDatabase(Database):
    def get(self, key):
        pass

    def set(self, key, value):
        pass


class ListDatabase(Database):
    def __len__(self) -> int:
        pass

    def insert(self, element: Any):
        pass

    def remove(self, element: Any):
        pass


class ListTxtDatabase(ListDatabase):
    def __init__(self, dbpath: str, unique=None):
        self.dbpath = dbpath
        self.unique = unique
        # create db if don't exist
        if not os.path.isfile(dbpath):
            with open(dbpath, "w"):
                pass

    def __len__(self):
        return self.count()

    def insert(self, line: str):
        if self.unique:
            if self.unique is True:
                if line in self:
                    raise TypeError(f"line {line!r} already exist")
            else:
                # unique if a function that return a string
                # check if the result of this function is unique in the db
                unique_line = self.unique(line)
                for db_line in self:
                    if self.unique(db_line) == unique_line:
                        raise TypeError(f"Identifier {unique_line!r} already exist")
        if "\n" in line:
            raise ValueError(f"line must not contain newline '\n' in txt database")
        with open(self.dbpath, "a") as f:
            f.write(line)
            f.write("\n")

    def remove(self, line_to_remove: str):
        # FIXME: can speed this by creating a tmp file
        # https://thispointer.com/python-how-to-delete-specific-lines-in-a-file-in-a-memory-efficient-way/

        # If self.unique is a function we remove by the id (result of unique)
        # and not by all the value
        if callable(self.unique):
            unique_callable = True
            line_to_remove = self.unique(line_to_remove)
        else:
            unique_callable = False
        new_lines = []
        removed = False
        with open(self.dbpath) as f:
            for line in f:
                compare_line = line[:-1]
                if unique_callable:
                    compare_line = self.unique(compare_line)
                if line_to_remove != compare_line:
                    new_lines.append(line)
                else:
                    # when we find the line to remove
                    # we add all other lines to the file
                    removed = True
                    for line in f:
                        new_lines.append(line)
                    break

        # if we removed nothing raise an exception
        if not removed:
            raise TypeError(f"line {line_to_remove!r} not found")

        # write new lines to the file
        with open(self.dbpath, "w") as f:
            f.writelines(new_lines)

    def count(self):
        return len(self.list())

    def list(self):
        with open(self.dbpath) as f:
            return [e[:-1] for e in f.readlines()]

    def pop(self):
        pass

    def __iter__(self):
        with open(self.dbpath) as f:
            for line in f:
                yield line[:-1]

    def __contains__(self, item):
        return self.contain(item)

    def contain(self, line: str):
        for db_line in self:
            if line == db_line:
                return True
        return False
