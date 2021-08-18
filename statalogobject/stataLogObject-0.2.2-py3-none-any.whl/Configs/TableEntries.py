from stataLogObject.Supports import EntryLengthInvalid

from dataclasses import dataclass, fields
from abc import ABC, abstractmethod


@dataclass
class Entry(ABC):

    @abstractmethod
    def entry_type(self):
        """The Entry Type of this Sub Class"""

    @property
    def entry_names(self):
        """Names of each field"""
        return [f.name for f in fields(self)]

    @property
    def entry_values(self):
        """Get all the values associated with this entry"""
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def create_entry(self, value_list):
        """Create the given entry with the values initialised to the value_list"""
        entry = self.entry_type()()
        if len(value_list) != len(entry.entry_names):
            raise EntryLengthInvalid(entry.entry_names, value_list)

        [setattr(entry, n, v) for n, v in zip(entry.entry_names, value_list)]
        return entry


@dataclass
class ZScore(Entry):
    """Z score variant of TableEntry"""
    var_name: str = None
    coefficient: float = None
    std_err: float = None
    z_score: float = None
    prob: float = None
    lb_95: float = None
    ub_95: float = None

    def entry_type(self):
        return ZScore


@dataclass
class PValue(Entry):
    """P value variant of Table Entry"""
    var_name: str = None
    coefficient: float = None
    std_err: float = None
    p_value: float = None
    prob: float = None
    lb_95: float = None
    ub_95: float = None

    def entry_type(self):
        return PValue


@dataclass
class Summary(Entry):
    """Summary table variant of Table Entry"""
    var_name: str = None
    obs: int = None
    mean: float = None
    std_dev: float = None
    v_min: float = None
    v_max: float = None

    def entry_type(self):
        return Summary


@dataclass
class Tabulate(Entry):
    """Tabulate table variant of Table Entry"""
    var_name: str = None
    freq: int = None
    percent: float = None
    cumulative: float = None

    def entry_type(self):
        return Tabulate
