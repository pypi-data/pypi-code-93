from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class VariableHolder(ABC):
    parameters: list

    @property
    @abstractmethod
    def as_dict(self):
        """Return as a dict"""


class RandomParameters(VariableHolder):
    rounder: int = 3

    @property
    def as_dict(self):
        """
        Return as a dict

        Note
        ----
        stata uses _cons for multiple levels so they will replace each other without enumerate
        """
        return {f"{name}_{i}": {"Est": est, "std": std, "lb_95": lb_95, "ub_95": ub_95}
                for i, (name, est, std, lb_95, ub_95) in enumerate(self.parameters)}

    def vpc_table(self, with_header=False):
        """Calculates the vpc of each parameter and return it alongside its 95%CI """
        parameter_rows = [self._table_row(i, level) for i, level in enumerate(self.parameters)]
        if with_header:
            return [['Level', "VPC", '95%CI']] + parameter_rows
        else:
            return parameter_rows

    def _table_row(self, i, level):
        """Set a row in the vpc table"""
        name, est, std_err, lb_95, ub_95 = level
        name = f"{name}_{i}"
        return [name, self.calculate_vpc(est), f"{round(lb_95, self.rounder)}; {round(ub_95, self.rounder)}"]

    def calculate_vpc(self, estimate):
        """Variance partition coefficient"""
        return round((estimate / self.total_variance) * 100, self.rounder)

    @property
    def total_variance(self):
        """Total variance of the random parameters"""
        return sum([est for _, est, _, _, _ in self.parameters])


# TODO: add as dict
class GroupParameter(VariableHolder):

    def as_dict(self):
        return