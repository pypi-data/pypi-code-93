from fractions import Fraction
from typing import Dict, Any, List

from DPGM import Node
from assignments import Assignment
import assignments as asg

DEFAULT_PRECISION = 5


class Distribution:

    def __init__(self, distribution: Dict[Assignment, Any], all_nodes: List[Node]):
        self.all_nodes = sorted(all_nodes)
        self.distribution = distribution
        self.z3_model = None
        self.model = None

    def get_assignment_probability(self, a: Assignment):
        return self.distribution[a]

    def get_marginal_probability(self, node: Node):
        probability = 0
        for assignment in asg.get_node_assignments(node, self.all_nodes):
            probability += self.get_assignment_probability(assignment)
        return probability

    def print_assignment_prob(self, nodes=None, only_positive=False, printer=print, precision=DEFAULT_PRECISION):
        """
        Print distribution over the assignments of the given nodes or all nodes if no list is given.
        If the only_positive flag is set, only the assignments with probability greater than zero are outputted.
        """
        if not nodes:
            nodes = self.all_nodes
            node_assignments = asg.generate(nodes)
        else:
            node_assignments = self.distribution.keys()
        for assignment in node_assignments:
            value = self.get_assignment_probability(assignment)
            if not only_positive or round(value, precision + 1) > 0:
                print_assignment_probability(assignment, value, printer=printer, precision=precision)

    def print_formatted(self, format_string: str, printer=print, precision=DEFAULT_PRECISION):
        """
        Print distribution given by in the formats specified by the format string: (M) marginal node probabilities,
        (F) full distribution, (S) support of distribution, (Z) Z3 output, (T) SMT2 format.
        """
        for char in format_string:
            if char == "F":
                self.print_assignment_prob(printer=printer, precision=precision)
            elif char == "S":
                printer("Support:")
                self.print_assignment_prob(only_positive=True, printer=printer, precision=precision)
            elif char == "M":
                for node in self.all_nodes:
                    prob = self.get_marginal_probability(node)

                    printer("P(" + str(node.name) + ") = " + format_probability(prob, precision))
            elif char == "Z":
                if self.z3_model is not None:
                    printer(str(self.z3_model))
                elif self.model is not None:
                    printer(str(self.model))
                else:
                    printer("No Z3 model available.")
                    self.print_assignment_prob(printer=printer, precision=precision)
            elif char == "T":
                if self.z3_model is not None:
                    printer(str(self.z3_model.sexpr()))
                else:
                    printer("No Z3 model available, thus no SMT2 format as well.")
                    self.print_assignment_prob(printer=printer, precision=precision)
            else:
                printer("Unknown distribution format '" + char + "'.")
                self.print_assignment_prob(printer=printer, precision=precision)

    def __eq__(self, other):
        if isinstance(other, Distribution):
            for a in self.distribution.keys():
                if self.get_assignment_probability(a) != other.get_assignment_probability(a):
                    return False
            return True
        return False


def format_probability(prob: float, precision=DEFAULT_PRECISION):
    if isinstance(prob, Fraction):
        return str(prob)
    return "{:0.{p}g}".format(round(prob, precision+1), p=precision)


def repr_assignment_prob(a: Assignment, prob: float, given: Assignment = None, precision=DEFAULT_PRECISION):
    cond = "P(" + asg.repr_assignment(a) + ("|" + asg.repr_assignment(given) if given else "") + ")"
    return cond + " = " + format_probability(prob, precision)


def print_assignment_probability(a: Assignment, prob: float, precision=DEFAULT_PRECISION, printer=print):
    printer(repr_assignment_prob(a, prob, None, precision=precision))
