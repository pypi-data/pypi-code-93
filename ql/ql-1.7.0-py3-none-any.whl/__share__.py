from . import __path__ as _dir_nspath
from pathlib import Path
from enum import IntEnum

__all__ = ["ql_path"]
ql_path = Path(list(_dir_nspath)[0])

# used for prefix dicts
class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

class MonthEnum(IntEnum):
    jan = 1
    feb = 2
    mar = 3
    apr = 4
    may = 5
    jun = 6
    jul = 7
    aug = 8
    sep = 9
    oct = 10
    nov = 11
    dec = 12

num2month_dict = dict([(x,y.name) for x,y in MonthEnum._value2member_map_.items()])

num2alphanum_monthdict = {k: f"{k:02}{v}" for k,v in num2month_dict.items()}
alphanum2num_monthdict = {v: k for k,v in num2alphanum_monthdict.items()}
