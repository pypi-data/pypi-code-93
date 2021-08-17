from fractions import Fraction
from typing import List

import pysmt.typing as types
from pysmt.shortcuts import Equals, Symbol, Real, Plus, GE, LE, And
import pysmt.shortcuts as smt
from pysmt.solvers.solver import Model
from pysmt.smtlib.parser import SmtLibParser


from assignments import Assignment
import assignments
import DPGM as AF
from distribution import Distribution


class SolverInstance:
    def __init__(self, af: AF, solver_name=None):
        self.af = af
        self.dimension = 2**len(af.get_nodes())
        self.solver_name = solver_name

        self.full_assignments: List[Assignment] = []
        self.full_assignment_symbols = dict()
        self.assignment_symbols = dict()
        self.constraints = []  # internal constraints that are always enforced by being added to the solver by default
        self.solver = None

        self._generate_full_assignment_symbols()

    def _generate_full_assignment_symbols(self):
        if not self.full_assignments:
            self.full_assignments = assignments.generate(sorted(self.af.get_nodes()))
        for assignment in self.full_assignments:
            name = symbol_name(assignment)
            symbol = Symbol(name, types.REAL)
            self.full_assignment_symbols[assignment] = symbol
            self.constraints.append(GE(symbol, Real(0)))
            # self.constraints.append(LE(symbol, Real(1)))
        # sum of all full assignments equals one
        self.constraints.append(Equals(Plus(self.full_assignment_symbols.values()), Real(1)))

    def get_symbol(self, assignment: Assignment):
        assert assignment, "empty assignment"

        if assignment in self.full_assignment_symbols:
            return self.full_assignment_symbols[assignment]
        elif assignment in self.assignment_symbols:
            return self.assignment_symbols[assignment]
        else:
            return self.generate_symbol(assignment)

    def get_node_symbol(self, node: AF.Node):
        return self.get_symbol(tuple([(node, True)]))

    def generate_symbol(self, assignment: Assignment):
        """Generate a symbol and constraints for the probability of a partial assignment."""
        assert len(assignment) < self.dimension
        name = symbol_name(assignment)
        symbol = Symbol(name, types.REAL)
        self.assignment_symbols[assignment] = symbol
        self._add_internal_constraint(GE(symbol, Real(0)))
        self._add_internal_constraint(LE(symbol, Real(1)))
        # express partial assignment as sum of full assignments
        full_assignments = assignments.sum_out(assignment, sorted(self.af.get_nodes()))
        constraint = Equals(symbol, Plus([self.full_assignment_symbols[asg] for asg in full_assignments]))
        self._add_internal_constraint(constraint)
        return symbol

    def distribution_from_model(self, model: Model) -> Distribution:
        """
        Get a distribution object from a model.
        """
        distribution_dict = dict()
        for assignment in self.full_assignments:
            distribution_dict[assignment] = self.value_from_model(assignment, model)
            # distribution_dict[assignment] = self.value_from_model_fraction(assignment, model)
        distribution = Distribution(distribution_dict, self.af.get_nodes())
        distribution.model = model
        return distribution

    def value_from_model(self, assignment: Assignment, model: Model):
        symbol = self.get_symbol(assignment)
        constant = model.get_value(symbol)
        if constant.is_real_constant() or constant.is_int_constant():
            return float(constant.constant_value())
        else:
            raise ValueError("Constant is neither INT or REAL: " + str(constant))

    def value_from_model_fraction(self, assignment: Assignment, model: Model) -> Fraction:
        symbol = self.get_symbol(assignment)
        constant = model.get_value(symbol)
        if constant.is_real_constant() or constant.is_int_constant():
            value = constant.constant_value()
            if isinstance(value, Fraction):
                return value
            else:
                return constant.algebraic_approx_value()
        else:
            raise ValueError("Constant is neither INT or REAL: " + str(constant))

    def is_sat(self, constraints):
        solver = self.get_solver()
        return solver.is_sat(And(constraints))

    def get_model(self, constraints):
        if self.is_sat(constraints):
            return self.solver.get_model()

    def get_solver(self) -> smt.Solver():
        if not self.solver:
            # create a new solver and add internal constraints
            if self.solver_name:
                self.solver = smt.Solver(name=self.solver_name)
            else:
                self.solver = smt.Solver()
            # print("basic constraints: ", self.constraints)
            self.solver.add_assertion(And(self.constraints))
        return self.solver

    def _add_internal_constraint(self, constraint):
        self.constraints.append(constraint)
        if self.solver:
            self.solver.add_assertion(constraint)

    def add_constraints_from_smt(self, smt_file):
        parser = SmtLibParser()
        try:
            script = parser.get_script(smt_file)
        except AttributeError:
            raise ValueError("Invalid SMT file. (Are all symbols declared?)")
        if not script.contains_command("check-sat"):
            script.add("check-sat", "")
        # print(script)
        for smt_symbol in script.get_declared_symbols():
            asg = symbol_name_to_assignment(str(smt_symbol), self.af)
            symbol = self.get_symbol(asg)
            if smt_symbol != symbol:
                raise ValueError("Invalid symbol name in SMT file: '" + str(smt_symbol)
                                 + "'. Did you mean + '" + str(symbol) + "'?")
        constraint = script.get_strict_formula()
        print("SMT constraint: ", constraint)
        self.constraints.append(constraint)


def symbol_name(assignment: Assignment) -> str:
    """
    Generates a fixed name for any assignment.
    Expects a list of tuples of nodes matched to True or False, i.e. [(node_B, False), (node_C, True)].
    Generates a name for the probability of the conjunction of the nodes, i.e. 'p_nB_C'.
    The order is determined by node IDs.
    """
    # assert list(assignment) == sorted(list(assignment))  # TODO: enforce sortedness as invariant?
    assignment = sorted(list(assignment))
    name = "p"
    for (arg, b) in assignment:
        name += "_"
        if not b:
            name += "n"
        name += arg.name
    return name


def symbol_name_to_assignment(name: str, af: AF) -> Assignment:
    """
    Inverse of `symbol_name` function.
    """
    split = name.split("_")
    assert split[0] == "p"

    assignment = []
    for i in range(1, len(split)):
        token = split[i]
        b = True
        if token.startswith("n"):
            b = False
            token = token[1:]
        node: AF.Node = af.get_node_by_name(token)
        assignment.append((node, b))
    return tuple(assignment)
