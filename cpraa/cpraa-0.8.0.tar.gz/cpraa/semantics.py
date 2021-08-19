import textwrap
from fractions import Fraction
from typing import List, Type, Set, Tuple

import z3
from pysmt.shortcuts import Not, And, Or, Implies, Iff, Equals, GE, GT, LE, Minus, Plus, Real, Bool

import assignments as asg
import classical_semantics as classical
from DPGM import DPGM, Node
from solver_instance import SolverInstance
from z3_instance import Z3Instance
from linear_solver import LinearSolver, Constraint


MAX_FRACTION_DENOMINATOR = 10000
CONSTRAINT_LOGGING = False
LOGGING_MAX_WIDTH = 120


class Semantics:
    def __init__(self, af: DPGM, complemented=False):
        self.af = af
        self.all_nodes = sorted(list(af.get_nodes()))
        self.constraints = None  # smt-lib constraints
        self.constraints_z3 = None
        self.constraints_linear = None
        self.complemented = complemented  # if this flag is set, the semantics' constraints are negated

    def generate_constraints(self, si: SolverInstance):
        # implemented by subclasses
        raise NotImplementedError

    def generate_z3_constraints(self, z3i: Z3Instance):
        # implemented by subclasses
        raise NotImplementedError

    def generate_linear_constraints(self, ls: LinearSolver):
        # implemented by subclasses
        raise NotImplementedError

    def get_constraints(self, si: SolverInstance) -> List:
        if self.constraints is None:
            self.constraints = []
            self.generate_constraints(si)
        if not self.complemented:
            return self.constraints
        else:
            return [Not(And(self.constraints))]

    def get_z3_constraints(self, z3i: Z3Instance) -> List:
        if self.constraints_z3 is None:
            self.constraints_z3 = []
            self.generate_z3_constraints(z3i)
        if not self.complemented:
            return self.constraints_z3
        else:
            return [z3.Not(z3.And(self.constraints_z3), ctx=z3i.context)]

    def get_linear_constraints(self, ls: LinearSolver) -> List[Constraint]:
        if self.complemented:
            raise NotImplementedError("Complement semantics not supported for linear constraints.")
        if self.constraints_linear is None:
            self.constraints_linear = []
            self.generate_linear_constraints(ls)
        return self.constraints_linear

    def add_constraint(self, constraint, node=None, edge=None):
        self.constraints.append(constraint)
        if CONSTRAINT_LOGGING:
            if node:
                print(str(self) + ": " + str(node) + ": " + textwrap.shorten(str(constraint), LOGGING_MAX_WIDTH))
            elif edge:
                print(str(self) + ": " + str(edge) + ": " + textwrap.shorten(str(constraint), LOGGING_MAX_WIDTH))
            else:
                print(str(self) + ": " + textwrap.shorten(str(constraint), LOGGING_MAX_WIDTH))

    def add_z3_constraint(self, constraint, node=None, edge=None):
        self.constraints_z3.append(constraint)
        if CONSTRAINT_LOGGING:
            if node:
                print(str(self) + ": " + str(node) + ": " + textwrap.shorten(str(constraint), LOGGING_MAX_WIDTH))
            elif edge:
                print(str(self) + ": " + str(edge) + ": " + textwrap.shorten(str(constraint), LOGGING_MAX_WIDTH))
            else:
                print(str(self) + ": " + textwrap.shorten(str(constraint), LOGGING_MAX_WIDTH))

    def __str__(self):
        name = self.__class__.__name__
        if self.complemented:
            name = "co-" + name
        return name


####################
# trivial semantics
####################

class Min(Semantics):
    """
    Minimality semantics: All nodes must hold with probability 0.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            self.add_constraint(Equals(node_symbol, Real(0)), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            self.add_z3_constraint(node_prob == 0, node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        for node in self.all_nodes:
            self.constraints_linear.extend(ls.constraints_node_equals_value(node, 0))


class Neu(Semantics):
    """
    Neutrality semantics: All nodes must hold with probability 0.5.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            self.add_constraint(Equals(node_symbol, Real(0.5)), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            self.add_z3_constraint(node_prob == 0.5, node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        for node in self.all_nodes:
            self.constraints_linear.extend(ls.constraints_node_equals_value(node, 0.5))


class Max(Semantics):
    """
    Maximality semantics: All nodes must hold with probability 1.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            self.add_constraint(Equals(node_symbol, Real(1)), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            self.add_z3_constraint(node_prob == 1, node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        for node in self.all_nodes:
            self.constraints_linear.extend(ls.constraints_node_equals_value(node, 1))


class Dirac(Semantics):
    """
    Dirac semantics: All nodes must hold with either probability 0 or 1.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            self.add_constraint(Or(Equals(node_symbol, Real(0)), Equals(node_symbol, Real(1))), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            self.add_z3_constraint(z3.Or(node_prob == 0, node_prob == 1), node=node)


class Ter(Semantics):
    """
    Ternary semantics: All nodes must hold with either probability 0, 0.5 or 1.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            self.add_constraint(Or(Equals(node_symbol, Real(0)),
                                   Equals(node_symbol, Real(0.5)),
                                   Equals(node_symbol, Real(1))), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            self.add_z3_constraint(z3.Or(node_prob == 0, node_prob == 0.5, node_prob == 1), node=node)


################################
# semantics by Hunter and Thimm
################################

class Fou(Semantics):
    """
    Foundedness semantics: Initial nodes must hold with probability 1.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.af.get_initial_nodes():
            node_symbol = si.get_node_symbol(node)
            self.add_constraint(Equals(node_symbol, Real(1)), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.af.get_initial_nodes():
            node_prob = z3i.get_node_prob_var(node)
            self.add_z3_constraint(node_prob == 1, node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        for node in self.af.get_initial_nodes():
            self.constraints_linear.extend(ls.constraints_node_equals_value(node, 1))


class SFou(Semantics):
    """
    Semi-Foundedness semantics: Initial nodes must hold with probability >= 0.5.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.af.get_initial_nodes():
            node_symbol = si.get_node_symbol(node)
            self.add_constraint(GE(node_symbol, Real(0.5)), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.af.get_initial_nodes():
            node_prob = z3i.get_node_prob_var(node)
            self.add_z3_constraint(node_prob >= 0.5, node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        for node in self.af.get_initial_nodes():
            self.constraints_linear.extend(ls.constraints_node_greater_or_equal_value(node, 0.5))


class Inv(Semantics):
    """
    Involution semantics: P(A) = 1 - P(B) for all attacks A -> B.
    """
    def generate_constraints(self, si: SolverInstance):
        for edge in self.af.get_edges():
            symbol_node_from = si.get_node_symbol(edge.node_from)
            symbol_node_to = si.get_node_symbol(edge.node_to)
            self.add_constraint(Equals(symbol_node_from, Minus(Real(1), symbol_node_to)), edge=edge)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for edge in self.af.get_edges():
            prob_node_from = z3i.get_node_prob_var(edge.node_from)
            prob_node_to = z3i.get_node_prob_var(edge.node_to)
            self.add_z3_constraint(prob_node_from == 1 - prob_node_to, edge=edge)

    def generate_linear_constraints(self, ls: LinearSolver):
        for edge in self.af.get_edges():
            node_from_assignments = asg.get_node_assignments(edge.node_from, self.all_nodes)
            node_to_false_assignments = asg.get_node_assignments(edge.node_to, self.all_nodes,
                                                                 node_assignment=False)
            c = ls.constraints_assignments_equal_assignments(node_from_assignments, node_to_false_assignments)
            self.constraints_linear.extend(c)


class Rat(Semantics):
    """
    Rationality semantics: P(A) > 0.5 implies P(B) <= 0.5 for all attacks A -> B.
    """
    def generate_constraints(self, si: SolverInstance):
        for edge in self.af.get_edges():
            symbol_node_from = si.get_node_symbol(edge.node_from)
            symbol_node_to = si.get_node_symbol(edge.node_to)
            constraint = Implies(GT(symbol_node_from, Real(0.5)), LE(symbol_node_to, Real(0.5)))
            self.add_constraint(constraint, edge=edge)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for edge in self.af.get_edges():
            prob_node_from = z3i.get_node_prob_var(edge.node_from)
            prob_node_to = z3i.get_node_prob_var(edge.node_to)
            constraint = z3.Implies(prob_node_from > 0.5, prob_node_to <= 0.5, ctx=z3i.context)
            self.add_z3_constraint(constraint, edge=edge)


class Coh(Semantics):
    """
    Coherency semantics: P(A) <= 1 - P(B) for all attacks A -> B.
    """
    def generate_constraints(self, si: SolverInstance):
        for edge in self.af.get_edges():
            symbol_node_from = si.get_node_symbol(edge.node_from)
            symbol_node_to = si.get_node_symbol(edge.node_to)
            constraint = LE(symbol_node_from, Minus(Real(1), symbol_node_to))
            self.add_constraint(constraint, edge=edge)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for edge in self.af.get_edges():
            prob_node_from = z3i.get_node_prob_var(edge.node_from)
            prob_node_to = z3i.get_node_prob_var(edge.node_to)
            self.add_z3_constraint(prob_node_from <= 1 - prob_node_to, edge=edge)

    def generate_linear_constraints(self, ls: LinearSolver):
        for edge in self.af.get_edges():
            node_from_assignments = asg.get_node_assignments(edge.node_from, self.all_nodes)
            node_to_false_assignments = asg.get_node_assignments(edge.node_to, self.all_nodes,
                                                                 node_assignment=False)
            c = ls.constraints_assignments_less_or_equal_assignments(node_from_assignments, node_to_false_assignments)
            self.constraints_linear.extend(c)


class Opt(Semantics):
    """
    Optimism semantics: P(A) >= 1 - Sum P(B) for all attackers B of A. For initial arguments A, this entails P(A) = 1.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            if node.is_initial():
                self.add_constraint(Equals(node_symbol, Real(1)), node=node)
                continue
            summation = Plus([si.get_node_symbol(attacker) for attacker in node.get_parents()])
            constraint = GE(node_symbol, Minus(Real(1), summation))
            self.add_constraint(constraint, node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            if node.is_initial():
                self.add_z3_constraint(node_prob == 1, node=node)
                continue
            summation = z3.Sum([z3i.get_node_prob_var(attacker) for attacker in node.get_parents()])
            self.add_z3_constraint(node_prob >= 1 - summation, node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        all_nodes = self.all_nodes
        for node in all_nodes:
            if node.is_initial():
                c = ls.constraints_node_equals_value(node, 1)
                self.constraints_linear.extend(c)
                continue
            # p_A >= 1 - Sum p_B is equivalent to p_A + Sum p_B >= 1 and -p_A + (-1) * Sum p_B <= -1
            sum_nodes = [node] + list(node.get_parents())
            rows = [ls.assignments_to_row(asg.get_node_assignments(n, all_nodes)) for n in sum_nodes]
            row = -1 * sum(rows)
            self.constraints_linear.append((row, -1))


class SOpt(Semantics):
    """
    Semi-optimism semantics: P(A) >= 1 - Sum P(B) for all non-initial arguments A with attackers B.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            if node.is_initial():
                continue
            summation = Plus([si.get_node_symbol(attacker) for attacker in node.get_parents()])
            constraint = GE(node_symbol, Minus(Real(1), summation))
            self.add_constraint(constraint, node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.all_nodes:
            if node.is_initial():
                continue
            node_prob = z3i.get_node_prob_var(node)
            summation = z3.Sum([z3i.get_node_prob_var(attacker) for attacker in node.get_parents()])
            self.add_z3_constraint(node_prob >= 1 - summation, node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        all_nodes = self.all_nodes
        for node in all_nodes:
            if node.is_initial():
                continue
            sum_nodes = [node] + list(node.get_parents())
            rows = [ls.assignments_to_row(asg.get_node_assignments(n, all_nodes)) for n in sum_nodes]
            row = -1 * sum(rows)
            self.constraints_linear.append((row, -1))


class Jus(Semantics):
    """
    Justifiability semantics: Coherency and optimism constraints hold.
    """
    def generate_constraints(self, si: SolverInstance):
        opt = Opt(self.af)
        coh = Coh(self.af)
        self.constraints.extend(opt.get_constraints(si) + coh.get_constraints(si))

    def generate_z3_constraints(self, z3i: Z3Instance):
        opt = Opt(self.af)
        coh = Coh(self.af)
        self.constraints_z3.extend(opt.get_z3_constraints(z3i) + coh.get_z3_constraints(z3i))

    def generate_linear_constraints(self, ls: LinearSolver):
        opt = Opt(self.af)
        coh = Coh(self.af)
        self.constraints_linear.extend(opt.get_linear_constraints(ls))
        self.constraints_linear.extend(coh.get_linear_constraints(ls))


######################
# semantics by Baier
######################

class CF(Semantics):
    """
    Conflict-freeness semantics: P(A,B) = 0 for all attacks A -> B.
    """
    def generate_constraints(self, si: SolverInstance):
        for edge in self.af.get_edges():
            assignment = tuple(sorted([(edge.node_from, True), (edge.node_to, True)]))
            # noinspection PyTypeChecker
            symbol = si.get_symbol(assignment)
            self.add_constraint(Equals(symbol, Real(0)), edge=edge)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for edge in self.af.get_edges():
            assignment = tuple(sorted([(edge.node_from, True), (edge.node_to, True)]))
            # noinspection PyTypeChecker
            prob_var = z3i.get_prob_var(assignment)
            self.add_z3_constraint(prob_var == 0, edge=edge)

    def generate_linear_constraints(self, ls: LinearSolver):
        for edge in self.af.get_edges():
            assignment = tuple(sorted([(edge.node_from, True), (edge.node_to, True)]))
            # noinspection PyTypeChecker
            full_assignments = asg.sum_out(assignment, self.all_nodes)
            self.constraints_linear.extend(ls.constraints_assignments_equal_value(full_assignments, 0))


# Admissibility

def almost_sure_defense_constraint(si: SolverInstance, node: Node):
    """
    Generate a constraint for an argument A to be almost-surely defended.
    This means for all attackers B->A, the probability that B is in turn attacked (and thus A is defended) is 1.
    That is, P(C1 or C2 or ... or Cn) = 1 for attackers C1...Cn of B, or, equivalently, P(nC1, nC2, ..., nCn) = 0.
    If an attacker B of A has no attackers, then A cannot be almost-surely defended, thus the impossible constraint
    'False' is added.
    """
    parents = list(node.get_parents())
    if len(parents) == 0:
        # unattacked nodes are necessarily defended
        return Bool(True)

    constraints = []
    for attacker in parents:
        attacker_parents: Set[Node] = attacker.get_parents()
        if attacker_parents:
            assignment_list = []
            for defender in attacker_parents:
                assignment_list.append((defender, False))
            assignment = tuple(sorted(assignment_list))
            symbol = si.get_symbol(assignment)
            constraints.append(Equals(symbol, Real(0)))
        else:
            return Bool(False)
    return And(constraints)


def almost_sure_defense_constraint_z3(z3i: Z3Instance, node: Node):
    """
    Generate a constraint for an argument A to be almost-surely defended.
    This means for all attackers B->A, the probability that B is in turn attacked (and thus A is defended) is 1.
    That is, P(C1 or C2 or ... or Cn) = 1 for attackers C1...Cn of B, or, equivalently, P(nC1, nC2, ..., nCn) = 0.
    If an attacker B of A has no attackers, then A cannot be almost-surely defended, thus the impossible constraint
    'False' is added.
    """
    parents = list(node.get_parents())
    if len(parents) == 0:
        # unattacked nodes are necessarily defended
        return z3.BoolVal(True, ctx=z3i.context)

    # special treatment for the first attacker as starting point for nested Ands
    first_attacker = parents[0]
    first_attacker_parents: Set[Node] = first_attacker.get_parents()
    if first_attacker_parents:
        assignment_list = []
        for defender in first_attacker_parents:
            assignment_list.append((defender, False))
        assignment = tuple(sorted(assignment_list))
        prob_var = z3i.get_prob_var(assignment)
        constraint = prob_var == 0
    else:
        return z3.BoolVal(False, ctx=z3i.context)

    for attacker in parents[1:]:
        attacker_parents: Set[Node] = attacker.get_parents()
        if attacker_parents:
            assignment_list = []
            for defender in attacker_parents:
                assignment_list.append((defender, False))
            assignment = tuple(sorted(assignment_list))
            prob_var = z3i.get_prob_var(assignment)
            constraint = z3.And(constraint, prob_var == 0)
        else:
            return z3.BoolVal(False, ctx=z3i.context)
    return constraint


class WAdm(Semantics):
    """
    Weak admissibility semantics: CF and P(A) = 1 implies A is almost-surely defended.
    """
    def generate_constraints(self, si: SolverInstance):
        sCF = CF(self.af)
        self.constraints.extend(sCF.get_constraints(si))
        for node in self.all_nodes:
            if node.is_initial():
                # initial nodes are always almost-surely defended, thus the constraint would become 'p_A == 1 -> True'
                continue
            node_symbol = si.get_node_symbol(node)
            as_defense_constraint = almost_sure_defense_constraint(si, node)
            self.add_constraint(Implies(Equals(node_symbol, Real(1)), as_defense_constraint), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        sCF = CF(self.af)
        self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
        for node in self.all_nodes:
            if node.is_initial():
                # initial nodes are always almost-surely defended, thus the constraint would become 'p_A == 1 -> True'
                continue
            node_prob = z3i.get_node_prob_var(node)
            as_defense_constraint = almost_sure_defense_constraint_z3(z3i, node)
            constraint = z3.Implies(node_prob == 1, as_defense_constraint, ctx=z3i.context)
            self.add_z3_constraint(constraint, node=node)


class PrAdm(Semantics):
    """
    Probabilistic admissibility semantics: CF and for all arguments B with attackers A1...An and attackees C1...Cm,
    P(C1 or ... or Cm) <= P(A1 or ... or An) holds. Equivalently, by negating each side and simplifying, we get
    P(nC1, ..., nCm) >= P(nA1, ..., nAn).
    """
    def generate_constraints(self, si: SolverInstance):
        sCF = CF(self.af)
        self.constraints.extend(sCF.get_constraints(si))
        for node in self.all_nodes:
            node_parents: Set[Node] = node.get_parents()
            if node_parents:
                attacker_assignment = tuple([(attacker, False) for attacker in node_parents])
                attacker_symbol = si.get_symbol(attacker_assignment)
            else:
                # there are no attackers, so the prob of any attacker holding is 0
                # thus, in the negated view, the prob is 1
                attacker_symbol = Real(1)
            node_children: Set[Node] = node.get_children()
            if node_children:
                attackee_assignment = tuple([(attackee, False) for attackee in node_children])
                attackee_symbol = si.get_symbol(attackee_assignment)
            else:
                # there are no attackees, so the prob of any attackee holding is 0
                # thus, in the negated view, the prob is 1
                attackee_symbol = Real(1)
            if node_parents or node_children:
                self.add_constraint(GE(attackee_symbol, attacker_symbol), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        sCF = CF(self.af)
        self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
        for node in self.all_nodes:
            node_parents: Set[Node] = node.get_parents()
            if node_parents:
                attacker_assignment = tuple([(attacker, False) for attacker in node_parents])
                attacker_prob_var = z3i.get_prob_var(attacker_assignment)
            else:
                # there are no attackers, so the prob of any attacker holding is 0
                # thus, in the negated view, the prob is 1
                attacker_prob_var = 1
            node_children: Set[Node] = node.get_children()
            if node_children:
                attackee_assignment = tuple([(attackee, False) for attackee in node_children])
                attackee_prob_var = z3i.get_prob_var(attackee_assignment)
            else:
                # there are no attackees, so the prob of any attackee holding is 0
                # thus, in the negated view, the prob is 1
                attackee_prob_var = 1
            if node_parents or node_children:
                self.add_z3_constraint(attackee_prob_var >= attacker_prob_var, node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        sCF = CF(self.af)
        self.constraints_linear.extend(sCF.get_linear_constraints(ls))
        attacker_full_assignments = None
        attacker_value = None
        for node in self.all_nodes:
            node_parents: Set[Node] = node.get_parents()
            if node_parents:
                attacker_assignment = tuple([(attacker, False) for attacker in node_parents])
                attacker_full_assignments = asg.sum_out(attacker_assignment, self.all_nodes)
            else:
                # there are no attackers, so the prob of any attacker holding is 0
                # thus, in the negated view, the prob is 1
                attacker_value = 1
            node_children: Set[Node] = node.get_children()
            if node_children:
                attackee_assignment = tuple([(attackee, False) for attackee in node_children])
                attackee_full_assignments = asg.sum_out(attackee_assignment, self.all_nodes)
                if node_parents:
                    c = ls.constraints_assignments_greater_or_equal_assignments(attackee_full_assignments,
                                                                                attacker_full_assignments)
                    self.constraints_linear.extend(c)
                else:
                    c = ls.constraints_assignments_greater_or_equal_value(attackee_full_assignments, attacker_value)
                    self.constraints_linear.extend(c)
            else:
                # there are no attackees, so the prob of any attackee holding is 0
                # thus, in the negated view, the prob is 1
                attackee_value = 1
                if node_parents:
                    c = ls.constraints_assignments_less_or_equal_value(attacker_full_assignments, attackee_value)
                    self.constraints_linear.extend(c)
                else:
                    # constraint would be 1 >= 1
                    pass


class MinAdm(Semantics):
    """
    Min-admissibility semantics: CF and for every argument C, P(C) <= min_{B in Pre(C)} P(OR Pre(B)) holds.
    Equivalently, for all B in Pre(C) with Pre(B) = {A1, ..., An}, it holds P(C) <= 1 - P(nA1, ..., nAn).
    """
    def generate_constraints(self, si: SolverInstance):
        sCF = CF(self.af)
        self.constraints.extend(sCF.get_constraints(si))
        for node in self.all_nodes:
            node_parents = node.get_parents()
            if node_parents:
                node_symbol = si.get_node_symbol(node)
                for attacker in node_parents:
                    attacker_parents: Set[Node] = attacker.get_parents()
                    if attacker_parents:
                        assignment = tuple([(defender, False) for defender in attacker_parents])
                        symbol = si.get_symbol(assignment)
                        self.add_constraint(LE(node_symbol, Minus(Real(1), symbol)), node=node)
                    else:
                        self.add_constraint(Equals(node_symbol, Real(0)), node=node)
            else:
                pass  # minAdm enforces no constraint for initial arguments

    def generate_z3_constraints(self, z3i: Z3Instance):
        sCF = CF(self.af)
        self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
        for node in self.all_nodes:
            node_parents = node.get_parents()
            if node_parents:
                node_prob = z3i.get_node_prob_var(node)
                for attacker in node_parents:
                    attacker_parents: Set[Node] = attacker.get_parents()
                    if attacker_parents:
                        assignment = tuple([(defender, False) for defender in attacker_parents])
                        prob_var = z3i.get_prob_var(assignment)
                        self.add_z3_constraint(node_prob <= 1 - prob_var, node=node)
                    else:
                        self.add_z3_constraint(node_prob == 0, node=node)
            else:
                pass  # minAdm enforces no constraint for initial arguments

    def generate_linear_constraints(self, ls: LinearSolver):
        sCF = CF(self.af)
        self.constraints_linear.extend(sCF.get_linear_constraints(ls))
        for node in self.all_nodes:
            node_parents = node.get_parents()
            if node_parents:
                node_full_assignments = asg.get_node_assignments(node, self.all_nodes)
                for attacker in node_parents:
                    attacker_parents: Set[Node] = attacker.get_parents()
                    if attacker_parents:
                        assignment = tuple([(defender, False) for defender in attacker_parents])
                        full_assignments = asg.sum_out(assignment, self.all_nodes)
                        row_1 = ls.assignments_to_row(node_full_assignments)
                        row_2 = ls.assignments_to_row(full_assignments)
                        # p_node <= 1 - p_attacker_parents
                        # p_node + p_attacker_parents <= 1
                        self.constraints_linear.append((row_1 + row_2, 1))
                    else:
                        c = ls.constraints_assignments_equal_value(node_full_assignments, 0)
                        self.constraints_linear.extend(c)
            else:
                pass  # minAdm enforces no constraint for initial arguments


class JntAdm(Semantics):
    """
    Joint-admissibility semantics: CF and for every argument C, P(C) <= P(AND_{B in Pre(C)} (OR Pre(B))) holds.
    """
    def generate_constraints(self, si: SolverInstance):
        sCF = CF(self.af)
        self.constraints.extend(sCF.get_constraints(si))
        for node in self.all_nodes:
            if node.is_initial():
                # for nodes without attackers, the constraint becomes P(C) <= 1, so we skip it
                continue
            node_symbol = si.get_node_symbol(node)
            # the positive cnf corresponding to AND_{B in Pre(C)} (OR Pre(B))
            cnf = [list(attacker.get_parents()) for attacker in node.get_parents()]
            if [] in cnf:
                # there is an attacker B which is not in turn attacked, thus P(AND_{B in Pre(C)} (OR Pre(B))) = 0
                self.add_constraint(Equals(node_symbol, Real(0)), node=node)
                continue
            cnf_assignments = asg.positive_cnf_assignments(cnf, self.all_nodes)
            symbols = [si.get_symbol(a) for a in cnf_assignments]
            self.add_constraint(LE(node_symbol, Plus(symbols)), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        sCF = CF(self.af)
        self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
        for node in self.all_nodes:
            if node.is_initial():
                # for nodes without attackers, the constraint becomes P(C) <= 1, so we skip it
                continue
            node_prob = z3i.get_node_prob_var(node)
            # the positive cnf corresponding to AND_{B in Pre(C)} (OR Pre(B))
            cnf = [list(attacker.get_parents()) for attacker in node.get_parents()]
            if [] in cnf:
                # there is an attacker B which is not in turn attacked, thus P(AND_{B in Pre(C)} (OR Pre(B))) = 0
                self.add_z3_constraint(node_prob == 0, node=node)
                continue
            cnf_assignments = asg.positive_cnf_assignments(cnf, self.all_nodes)
            prob_vars = [z3i.get_prob_var(a) for a in cnf_assignments]
            # self.add_z3_constraint(node_prob <= z3.Sum(prob_vars), node=node)
            self.add_z3_constraint(node_prob.__le__(z3.Sum(prob_vars)), node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        sCF = CF(self.af)
        self.constraints_linear.extend(sCF.get_linear_constraints(ls))
        for node in self.all_nodes:
            if node.is_initial():
                # for nodes without attackers, the constraint becomes P(C) <= 1, so we skip it
                continue
            # the positive cnf corresponding to AND_{B in Pre(C)} (OR Pre(B))
            cnf = [list(attacker.get_parents()) for attacker in node.get_parents()]
            if [] in cnf:
                # there is an attacker B which is not in turn attacked, thus P(AND_{B in Pre(C)} (OR Pre(B))) = 0
                self.constraints_linear.extend(ls.constraints_node_equals_value(node, 0))
                continue
            node_assignments = asg.get_node_assignments(node, self.all_nodes)
            cnf_assignments = asg.positive_cnf_assignments(cnf, self.all_nodes)
            c = ls.constraints_assignments_less_or_equal_assignments(node_assignments, cnf_assignments)
            self.constraints_linear.extend(c)


# Completeness

class WCmp(Semantics):
    """
    Weak completeness semantics: CF and P(A) = 1 if and only if A is almost-surely defended.
    """
    def generate_constraints(self, si: SolverInstance):
        sCF = CF(self.af)
        self.constraints.extend(sCF.get_constraints(si))
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            if node.is_initial():
                # every initial node is almost-surely defended
                self.add_constraint(Equals(node_symbol, Real(1)), node=node)
                continue
            as_defense_constraint = almost_sure_defense_constraint(si, node)
            self.add_constraint(Iff(Equals(node_symbol, Real(1)), as_defense_constraint), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        sCF = CF(self.af)
        self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            if node.is_initial():
                # every initial node is almost-surely defended
                self.add_z3_constraint(node_prob == 1, node=node)
                continue
            as_defense_constraint = almost_sure_defense_constraint_z3(z3i, node)
            self.add_z3_constraint(z3.Implies(node_prob == 1, as_defense_constraint, ctx=z3i.context), node=node)
            self.add_z3_constraint(z3.Implies(as_defense_constraint, node_prob == 1, ctx=z3i.context), node=node)


def add_prCmp_constraints(sem: Semantics, nodes: List[Node], si: SolverInstance):
    """
    Given a list of arguments, adds the constraints P(C) >= P(AND_{B in Pre(C)} (OR Pre(B))) for every argument C.
    """
    for node in nodes:
        node_symbol = si.get_node_symbol(node)
        if node.is_initial():
            # for nodes without attackers, the constraint becomes P(C) >= 1
            sem.add_constraint(Equals(node_symbol, Real(1)), node=node)
            continue
        # the positive cnf corresponding to AND_{B in Pre(C)} (OR Pre(B))
        cnf = [list(attacker.get_parents()) for attacker in node.get_parents()]
        if [] in cnf:
            # there is an attacker B which is not in turn attacked, thus P(AND_{B in Pre(C)} (OR Pre(B))) = 0
            # the constraint would be P(C) >= 0, so we skip it
            continue
        cnf_assignments = asg.positive_cnf_assignments(cnf, nodes)
        cnf_symbols = [si.get_symbol(a) for a in cnf_assignments]
        sem.add_constraint(GE(node_symbol, Plus(cnf_symbols)), node=node)


def add_prCmp_z3_constraints(sem: Semantics, nodes: List[Node], z3i: Z3Instance):
    """
    Given a list of arguments, adds the constraints P(C) >= P(AND_{B in Pre(C)} (OR Pre(B))) for every argument C.
    """
    for node in nodes:
        node_prob = z3i.get_node_prob_var(node)
        if node.is_initial():
            # for nodes without attackers, the constraint becomes P(C) >= 1
            sem.add_z3_constraint(node_prob == 1, node=node)
            continue
        # the positive cnf corresponding to AND_{B in Pre(C)} (OR Pre(B))
        cnf = [list(attacker.get_parents()) for attacker in node.get_parents()]
        if [] in cnf:
            # there is an attacker B which is not in turn attacked, thus P(AND_{B in Pre(C)} (OR Pre(B))) = 0
            # the constraint would be P(C) >= 0, so we skip it
            continue
        cnf_assignments = asg.positive_cnf_assignments(cnf, nodes)
        prob_vars = [z3i.get_prob_var(a) for a in cnf_assignments]
        sem.add_z3_constraint(node_prob >= z3.Sum(prob_vars), node=node)


def prCmp_linear_constraints(nodes: List[Node], ls: LinearSolver):
    """
    Given a list of arguments, returns the constraints P(C) >= P(AND_{B in Pre(C)} (OR Pre(B))) for every argument C.
    """
    constraints = []
    for node in nodes:
        node_assignments = asg.get_node_assignments(node, ls.af.get_nodes())
        if node.is_initial():
            # for nodes without attackers, the constraint becomes P(C) >= 1, and thus P(C) == 1
            constraints.extend(ls.constraints_assignments_equal_value(node_assignments, 1))
            continue
        # the positive cnf corresponding to AND_{B in Pre(C)} (OR Pre(B))
        cnf = [list(attacker.get_parents()) for attacker in node.get_parents()]
        if [] in cnf:
            # there is an attacker B which is not in turn attacked, thus P(AND_{B in Pre(C)} (OR Pre(B))) = 0
            # the constraint would be P(C) >= 0, so we skip it
            continue
        cnf_assignments = asg.positive_cnf_assignments(cnf, nodes)
        c = ls.constraints_assignments_greater_or_equal_assignments(node_assignments, cnf_assignments)
        constraints.extend(c)
    return constraints


class PrCmp(Semantics):
    """
    Probabilistic completeness semantics: Prob. admissible and P(C) >= P(AND_{B in Pre(C)} (OR Pre(B))) holds for all
    arguments C.
    """
    def generate_constraints(self, si: SolverInstance):
        prAdm = PrAdm(self.af)
        self.constraints.extend(prAdm.get_constraints(si))
        add_prCmp_constraints(self, self.all_nodes, si)

    def generate_z3_constraints(self, z3i: Z3Instance):
        prAdm = PrAdm(self.af)
        self.constraints_z3.extend(prAdm.get_z3_constraints(z3i))
        add_prCmp_z3_constraints(self, self.all_nodes, z3i)

    def generate_linear_constraints(self, ls: LinearSolver):
        prAdm = PrAdm(self.af)
        self.constraints_linear.extend(prAdm.get_linear_constraints(ls))
        self.constraints_linear.extend(prCmp_linear_constraints(self.all_nodes, ls))


class MinCmp(Semantics):
    """
    Min-complete semantics: Min-admissible and P(C) >= P(AND_{B in Pre(C)} (OR Pre(B))) holds for all arguments C.
    """
    def generate_constraints(self, si: SolverInstance):
        minAdm = MinAdm(self.af)
        self.constraints.extend(minAdm.get_constraints(si))
        add_prCmp_constraints(self, self.all_nodes, si)

    def generate_z3_constraints(self, z3i: Z3Instance):
        minAdm = MinAdm(self.af)
        self.constraints_z3.extend(minAdm.get_z3_constraints(z3i))
        add_prCmp_z3_constraints(self, self.all_nodes, z3i)

    def generate_linear_constraints(self, ls: LinearSolver):
        minAdm = MinAdm(self.af)
        self.constraints_linear.extend(minAdm.get_linear_constraints(ls))
        self.constraints_linear.extend(prCmp_linear_constraints(self.all_nodes, ls))


class JntCmp(Semantics):
    """
    Joint-complete semantics: CF and P(C) = P(AND_{B in Pre(C)} (OR Pre(B))) holds for all arguments C.
    """
    def generate_constraints(self, si: SolverInstance):
        sCF = CF(self.af)
        self.constraints.extend(sCF.get_constraints(si))
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            if node.is_initial():
                # for nodes without attackers, the constraint becomes P(C) == 1
                self.add_constraint(Equals(node_symbol, Real(1)), node=node)
                continue
            # the positive cnf corresponding to AND_{B in Pre(C)} (OR Pre(B))
            cnf = [list(attacker.get_parents()) for attacker in node.get_parents()]
            if [] in cnf:
                # there is an attacker B which is not in turn attacked, thus P(AND_{B in Pre(C)} (OR Pre(B))) = 0
                self.add_constraint(Equals(node_symbol, Real(0)), node=node)
                continue
            cnf_assignments = asg.positive_cnf_assignments(cnf, self.all_nodes)
            cnf_symbols = [si.get_symbol(a) for a in cnf_assignments]
            self.add_constraint(Equals(node_symbol, Plus(cnf_symbols)), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        sCF = CF(self.af)
        self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            if node.is_initial():
                # for nodes without attackers, the constraint becomes P(C) == 1
                self.add_z3_constraint(node_prob == 1, node=node)
                continue
            # the positive cnf corresponding to AND_{B in Pre(C)} (OR Pre(B))
            cnf = [list(attacker.get_parents()) for attacker in node.get_parents()]
            if [] in cnf:
                # there is an attacker B which is not in turn attacked, thus P(AND_{B in Pre(C)} (OR Pre(B))) = 0
                self.add_z3_constraint(node_prob == 0, node=node)
                continue
            cnf_assignments = asg.positive_cnf_assignments(cnf, self.all_nodes)
            prob_vars = [z3i.get_prob_var(a) for a in cnf_assignments]
            # self.add_z3_constraint(node_prob == z3.Sum(prob_vars), node=node)
            self.add_z3_constraint(node_prob.__eq__(z3.Sum(prob_vars)), node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        sCF = CF(self.af)
        self.constraints_linear.extend(sCF.get_linear_constraints(ls))
        for node in self.all_nodes:
            if node.is_initial():
                # for nodes without attackers, the constraint becomes P(C) == 1
                c = ls.constraints_node_equals_value(node, 1)
                self.constraints_linear.extend(c)
                continue
            # the positive cnf corresponding to AND_{B in Pre(C)} (OR Pre(B))
            cnf = [list(attacker.get_parents()) for attacker in node.get_parents()]
            if [] in cnf:
                # there is an attacker B which is not in turn attacked, thus P(AND_{B in Pre(C)} (OR Pre(B))) = 0
                c = ls.constraints_node_equals_value(node, 0)
                self.constraints_linear.extend(c)
                continue
            node_assignments = asg.get_node_assignments(node, self.all_nodes)
            cnf_assignments = asg.positive_cnf_assignments(cnf, self.all_nodes)
            c = ls.constraints_assignments_equal_assignments(node_assignments, cnf_assignments)
            self.constraints_linear.extend(c)


#################
# 0/1 Saturation
#################

class ZSat(Semantics):
    """
    0-saturation semantics: CF and P(B) = 0 implies P(A1 or ... or An) = 1 for Ai in Pre(B).
    """
    def generate_constraints(self, si: SolverInstance):
        sCF = CF(self.af)
        self.constraints.extend(sCF.get_constraints(si))
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            if node.is_initial():
                # for initial nodes the constraint would become 'p_B == 0 -> False', so we add 'p_B > 0'
                self.add_constraint(GT(node_symbol, Real(0)), node=node)
                continue
            # we use P(nA1 and ... and nAn) = 0 for Ai in Pre(B) instead of P(A1 or ... or An) = 1 for Ai in Pre(B)
            attacker_assignment = tuple([(attacker, False) for attacker in node.get_parents()])
            attacker_symbol = si.get_symbol(attacker_assignment)
            self.add_constraint(Implies(Equals(node_symbol, Real(0)), Equals(attacker_symbol, Real(0))), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        sCF = CF(self.af)
        self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            if node.is_initial():
                # for initial nodes the constraint would become 'p_B == 0 -> False', so we add 'p_B > 0'
                self.add_z3_constraint(node_prob > 0, node=node)
                continue
            # we use P(nA1 and ... and nAn) = 0 for Ai in Pre(B) instead of P(A1 or ... or An) = 1 for Ai in Pre(B)
            attacker_assignment = tuple([(attacker, False) for attacker in node.get_parents()])
            attacker_prob_var = z3i.get_prob_var(attacker_assignment)
            constraint = z3.Implies(node_prob == 0, attacker_prob_var == 0, ctx=z3i.context)
            self.add_z3_constraint(constraint, node=node)


class OSat(Semantics):
    """
    1-saturation semantics: CF and P(B) < 1 implies P(A1 or ... or An) > 0 for Ai in Pre(B).
    """
    def generate_constraints(self, si: SolverInstance):
        sCF = CF(self.af)
        self.constraints.extend(sCF.get_constraints(si))
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            if node.is_initial():
                # for initial nodes the constraint would become 'p_B < 1 -> False', so we add 'p_B == 1'
                self.add_constraint(Equals(node_symbol, Real(1)), node=node)
                continue
            # we use P(nA1 and ... and nAn) < 1 for Ai in Pre(B) instead of P(A1 or ... or An) > 0 for Ai in Pre(B)
            attacker_assignment = tuple([(attacker, False) for attacker in node.get_parents()])
            attacker_symbol = si.get_symbol(attacker_assignment)
            self.add_constraint(Implies(LE(node_symbol, Real(1)), LE(attacker_symbol, Real(1))), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        sCF = CF(self.af)
        self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            if node.is_initial():
                # for initial nodes the constraint would become 'p_B < 1 -> False', so we add 'p_B == 1'
                self.add_z3_constraint(node_prob == 1, node=node)
                continue
            # we use P(nA1 and ... and nAn) < 1 for Ai in Pre(B) instead of P(A1 or ... or An) > 0 for Ai in Pre(B)
            attacker_assignment = tuple([(attacker, False) for attacker in node.get_parents()])
            attacker_prob_var = z3i.get_prob_var(attacker_assignment)
            constraint = z3.Implies(node_prob < 1, attacker_prob_var < 1, ctx=z3i.context)
            self.add_z3_constraint(constraint, node=node)


class ZOSat(Semantics):
    """
    0/1-saturation semantics: intersection of 0-saturation (ZSat) and 1-saturation (OSat).
    """
    def generate_constraints(self, si: SolverInstance):
        zsat = ZSat(self.af)
        self.constraints.extend(zsat.get_constraints(si))
        osat = OSat(self.af)
        self.constraints.extend(osat.get_constraints(si))

    def generate_z3_constraints(self, z3i: Z3Instance) -> List:
        zsat = ZSat(self.af)
        self.constraints_z3.extend(zsat.get_z3_constraints(z3i))
        osat = OSat(self.af)
        self.constraints_z3.extend(osat.get_z3_constraints(z3i))


######################################################
# Element-wise lifted versions of classical semantics
######################################################

class ElmClassicalSemantics(Semantics):
    """
    Element-wise lifted classical semantics: If a probabilistic variable from the full joint distribution has positive
    probability, it needs to correspond to an extension of the classical semantics. That is, all prob vars
    corresponding to other extensions need to have probability zero.
    """
    def __init__(self, classical_semantics: Type[classical.ClassicalSemantics], af: DPGM, complemented=False):
        self.classical_semantics = classical_semantics
        super().__init__(af, complemented)

    def generate_constraints(self, si: SolverInstance):
        sem = self.classical_semantics(self.af)
        sem_extensions = sem.get_extensions()
        constraint_list = []
        for assignment in si.full_assignments:
            if asg.to_extension(assignment) not in sem_extensions:
                symbol = si.get_symbol(assignment)
                constraint_list.append(Equals(symbol, Real(0)))
        self.add_constraint(And(constraint_list))

    def generate_z3_constraints(self, z3i: Z3Instance):
        sem = self.classical_semantics(self.af)
        sem_extensions = sem.get_extensions()
        constraint_list = []
        for assignment in z3i.full_joint_assignments:
            if asg.to_extension(assignment) not in sem_extensions:
                prob_var = z3i.get_prob_var(assignment)
                constraint_list.append(prob_var == 0)
        self.add_z3_constraint(z3.And(constraint_list))

    def generate_linear_constraints(self, ls: LinearSolver):
        sem = self.classical_semantics(self.af)
        sem_extensions = sem.get_extensions()
        non_adm_assignments = []
        for assignment in asg.generate(self.all_nodes):
            if asg.to_extension(assignment) not in sem_extensions:
                non_adm_assignments.append(assignment)
        self.constraints_linear.extend(ls.constraints_assignments_equal_value(non_adm_assignments, 0))


class ElmCF(ElmClassicalSemantics):
    """
    Element-wise conflict-free semantics.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.CF, af, complemented)


class ElmAdm(ElmClassicalSemantics):
    """
    Element-wise admissible semantics.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.Admissible, af, complemented)


class ElmCmp(ElmClassicalSemantics):
    """
    Element-wise complete semantics.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.Complete, af, complemented)


class ElmGrn(ElmClassicalSemantics):
    """
    Element-wise grounded semantics.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.Grounded, af, complemented)


class ElmPrf(ElmClassicalSemantics):
    """
    Element-wise preferred semantics.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.Preferred, af, complemented)


class ElmSStl(ElmClassicalSemantics):
    """
    Element-wise semi-stable semantics.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.SemiStable, af, complemented)


class ElmStl(ElmClassicalSemantics):
    """
    Element-wise stable semantics.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.Stable, af, complemented)


################################################
# Experimental semantics generalizing labelings
################################################

# class LabAdm(Semantics):
#     def generate_z3_constraints(self, z3i: Z3Instance):
#         sCF = CF(self.af)
#         self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
#         for node in self.all_nodes:
#             node_prob = z3i.get_node_prob_var(node)
#             or_list = []
#             for parent_node in node.get_parents():
#                 parent_node_prob = z3i.get_node_prob_var(parent_node)
#                 or_list.append(parent_node_prob == 1)
#             self.add_z3_constraint(z3.Implies(node_prob == 0, z3.Or(or_list, z3i.context), z3i.context), node=node)
#
#
# class SLabAdm(Semantics):
#     def generate_z3_constraints(self, z3i: Z3Instance):
#         sCF = CF(self.af)
#         self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
#         for node in self.all_nodes:
#             node_prob = z3i.get_node_prob_var(node)
#             if node.is_initial():
#                 continue
#             or_list = []
#             for parent_node in node.get_parents():
#                 parent_node_prob = z3i.get_node_prob_var(parent_node)
#                 or_list.append(parent_node_prob == 1)
#             self.add_z3_constraint(z3.Implies(node_prob == 0, z3.Or(or_list, z3i.context), z3i.context), node=node)
#
#
# def open_interval_constraint(prob_var, context, low=0, high=1):
#     return z3.And(prob_var > low, prob_var < high, context)
#
#
# class LabCmp(Semantics):
#     def generate_z3_constraints(self, z3i: Z3Instance):
#         labAdm = LabAdm(self.af)
#         self.constraints_z3.extend(labAdm.get_z3_constraints(z3i))
#         for node in self.all_nodes:
#             node_prob = z3i.get_node_prob_var(node)
#             node_undec = open_interval_constraint(node_prob, z3i.context)
#             or_list = []
#             for parent_node in node.get_parents():
#                 parent_node_prob = z3i.get_node_prob_var(parent_node)
#                 self.add_z3_constraint(z3.Implies(node_undec, parent_node_prob < 1, z3i.context), node=node)
#                 parent_undec = open_interval_constraint(parent_node_prob, z3i.context)
#                 or_list.append(parent_undec)
#             self.add_z3_constraint(z3.Implies(node_undec, z3.Or(or_list, z3i.context), z3i.context), node=node)
#
#
# class SLabCmp(Semantics):
#     def generate_z3_constraints(self, z3i: Z3Instance):
#         sLabAdm = SLabAdm(self.af)
#         self.constraints_z3.extend(sLabAdm.get_z3_constraints(z3i))
#         for node in self.all_nodes:
#             node_prob = z3i.get_node_prob_var(node)
#             if node.is_initial():
#                 continue
#             node_undec = open_interval_constraint(node_prob, z3i.context)
#             or_list = []
#             for parent_node in node.get_parents():
#                 parent_node_prob = z3i.get_node_prob_var(parent_node)
#                 self.add_z3_constraint(z3.Implies(node_undec, parent_node_prob < 1, z3i.context), node=node)
#                 parent_undec = open_interval_constraint(parent_node_prob, z3i.context)
#                 or_list.append(parent_undec)
#             self.add_z3_constraint(z3.Implies(node_undec, z3.Or(or_list, z3i.context), z3i.context), node=node)


#####################
# semantics by Käfer
#####################

class WNorS(Semantics):
    """
    Weak not-or semantics without CF: Generates constraints P(A) <= P(-B1,-B2,...,-Bi) for every non-initial argument A
    with attackers B1, ..., Bi for some i > 0.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.all_nodes:
            if node.is_initial():
                continue  # for initial nodes, the constraint would be 'p_A <= 1' which already exists
            node_symbol = si.get_node_symbol(node)
            assignment = tuple([(attacker, False) for attacker in node.get_parents()])
            # noinspection PyTypeChecker
            attackers_symbol = si.get_symbol(assignment)
            self.add_constraint(LE(node_symbol, attackers_symbol), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.all_nodes:
            if node.is_initial():
                continue  # for initial nodes, the constraint would be 'p_A <= 1' which already exists
            node_prob = z3i.get_node_prob_var(node)
            assignment = tuple([(attacker, False) for attacker in node.get_parents()])
            # noinspection PyTypeChecker
            attackers_prob = z3i.get_prob_var(assignment)
            # self.add_z3_constraint(node_prob <= attackers_prob, node=node)
            self.add_z3_constraint(node_prob.__le__(attackers_prob), node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        raise NotImplementedError  # TODO


class NorS(Semantics):
    """
    Not-or semantics without CF: Generates constraints P(A) = P(-B1,-B2,...,-Bi) for every non-initial argument A with
    attackers B1, ..., Bi for some i > 0.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.all_nodes:
            if node.is_initial():
                continue  # for initial nodes, the constraint would be 'p_A <= 1' which already exists
            node_symbol = si.get_node_symbol(node)
            assignment = tuple([(attacker, False) for attacker in node.get_parents()])
            # noinspection PyTypeChecker
            attackers_symbol = si.get_symbol(assignment)
            self.add_constraint(Equals(node_symbol, attackers_symbol), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.all_nodes:
            if node.is_initial():
                continue
            node_prob = z3i.get_node_prob_var(node)
            assignment = tuple([(attacker, False) for attacker in node.get_parents()])
            # noinspection PyTypeChecker
            attackers_prob = z3i.get_prob_var(assignment)
            # self.add_z3_constraint(node_prob == attackers_prob, node=node)
            self.add_z3_constraint(node_prob.__eq__(attackers_prob), node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        raise NotImplementedError  # TODO


class SNorS(Semantics):
    """
    Strong not-or semantics without CF. Generates constraints P(A) = 1 for initial arguments and
    P(A) = P(-B1,-B2,...,-Bi) for every non-initial argument A with attackers B1, ..., Bi for some i>0.
    Also the intersection of Nor and Fou.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            if node.is_initial():
                self.add_constraint(Equals(node_symbol, Real(1)), node=node)
            else:
                assignment = tuple([(attacker, False) for attacker in node.get_parents()])
                # noinspection PyTypeChecker
                attackers_symbol = si.get_symbol(assignment)
                self.add_constraint(Equals(node_symbol, attackers_symbol), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            if node.is_initial():
                self.add_z3_constraint(node_prob == 1, node=node)
            else:
                assignment: List[Tuple[Node, bool]] = [(attacker, False) for attacker in node.get_parents()]
                attackers_prob = z3i.get_prob_var(tuple(assignment))
                # self.add_z3_constraint(node_prob == attackers_prob, node=node)
                self.add_z3_constraint(node_prob.__eq__(attackers_prob), node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        raise NotImplementedError  # TODO


class WNor(Semantics):
    """
    Weak not-or semantics: Generates constraints for conflict-freeness and P(A) <= P(-B1,-B2,...,-Bi) for every
    non-initial argument A with attackers B1, ..., Bi for some i > 0.
    """
    def generate_constraints(self, si: SolverInstance):
        sCF = CF(self.af)
        self.constraints.extend(sCF.get_constraints(si))
        sWNorS = WNorS(self.af)
        self.constraints.extend(sWNorS.get_constraints(si))

    def generate_z3_constraints(self, z3i: Z3Instance):
        sCF = CF(self.af)
        self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
        for node in self.all_nodes:
            if node.is_initial():
                continue  # for initial nodes, the constraint would be 'p_A <= 1' which already exists
            node_prob = z3i.get_node_prob_var(node)
            assignment: List[Tuple[Node, bool]] = [(attacker, False) for attacker in node.get_parents()]
            attackers_prob = z3i.get_prob_var(tuple(assignment))
            # self.add_z3_constraint(node_prob <= attackers_prob, node=node)
            self.add_z3_constraint(node_prob.__le__(attackers_prob), node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        sCF = CF(self.af)
        self.constraints_linear.extend(sCF.get_linear_constraints(ls))
        sWNorS = WNorS(self.af)
        self.constraints_linear.extend(sWNorS.get_linear_constraints(ls))


class Nor(Semantics):
    """
    Not-or semantics: Generates constraints for conflict-freeness and P(A) = P(-B1,-B2,...,-Bi) for every non-initial
    argument A with attackers B1, ..., Bi for some i > 0.
    """
    def generate_constraints(self, si: SolverInstance):
        sCF = CF(self.af)
        self.constraints.extend(sCF.get_constraints(si))
        sNorS = NorS(self.af)
        self.constraints.extend(sNorS.get_constraints(si))

    def generate_z3_constraints(self, z3i: Z3Instance):
        sCF = CF(self.af)
        self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
        for node in self.all_nodes:
            if node.is_initial():
                continue
            node_prob = z3i.get_node_prob_var(node)
            assignment: List[Tuple[Node, bool]] = [(attacker, False) for attacker in node.get_parents()]
            attackers_prob = z3i.get_prob_var(tuple(assignment))
            # self.add_z3_constraint(node_prob == attackers_prob, node=node)
            self.add_z3_constraint(node_prob.__eq__(attackers_prob), node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        sCF = CF(self.af)
        self.constraints_linear.extend(sCF.get_linear_constraints(ls))
        sNorS = NorS(self.af)
        self.constraints_linear.extend(sNorS.get_linear_constraints(ls))


class SNor(Semantics):
    """
    Strong not-or semantics: Generates constraints for conflict-freeness, P(A) = 1 for initial arguments and
    P(A) = P(-B1,-B2,...,-Bi) for every non-initial argument A with attackers B1, ..., Bi for some i>0.
    Also the intersection of Nor and Fou and CF.
    """
    def generate_constraints(self, si: SolverInstance):
        sCF = CF(self.af)
        self.constraints.extend(sCF.get_constraints(si))
        sSNorS = SNorS(self.af)
        self.constraints.extend(sSNorS.get_constraints(si))

    def generate_z3_constraints(self, z3i: Z3Instance):
        sCF = CF(self.af)
        self.constraints_z3.extend(sCF.get_z3_constraints(z3i))
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            if node.is_initial():
                self.add_z3_constraint(node_prob == 1, node=node)
            else:
                assignment: List[Tuple[Node, bool]] = [(attacker, False) for attacker in node.get_parents()]
                attackers_prob = z3i.get_prob_var(tuple(assignment))
                # self.add_z3_constraint(node_prob == attackers_prob, node=node)
                self.add_z3_constraint(node_prob.__eq__(attackers_prob), node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        sCF = CF(self.af)
        self.constraints_linear.extend(sCF.get_linear_constraints(ls))
        sSNorS = SNorS(self.af)
        self.constraints_linear.extend(sSNorS.get_linear_constraints(ls))


class AF(Semantics):
    """
    Special semantics to add constraints for probability values or intervals specified in the AF input file.
    """
    def generate_constraints(self, si: SolverInstance):
        for node in self.all_nodes:
            node_symbol = si.get_node_symbol(node)
            if node.value is not None:
                assert node.interval is None, "node with both value and interval set"
                value = nice_fraction(node.value)
                self.add_constraint(Equals(node_symbol, Real(value)), node=node)
            elif node.interval is not None:
                low, high = node.interval
                low = nice_fraction(low)
                high = nice_fraction(high)
                self.add_constraint(And(LE(node_symbol, Real(high)), GE(node_symbol, Real(low))), node=node)

    def generate_z3_constraints(self, z3i: Z3Instance):
        for node in self.all_nodes:
            node_prob = z3i.get_node_prob_var(node)
            if node.value is not None:
                assert node.interval is None, "node with both value and interval set"
                # self.add_z3_constraint(node_prob == node.value, node=node)
                self.add_z3_constraint(node_prob.__eq__(node.value), node=node)
            elif node.interval is not None:
                low, high = node.interval
                # self.add_z3_constraint(node_prob >= low, node=node)
                # self.add_z3_constraint(node_prob <= high, node=node)
                self.add_z3_constraint(node_prob.__ge__(low), node=node)
                self.add_z3_constraint(node_prob.__le__(high), node=node)

    def generate_linear_constraints(self, ls: LinearSolver):
        for node in self.all_nodes:
            node_full_assignments = asg.get_node_assignments(node, self.all_nodes)
            # node_prob = z3i.get_node_prob_var(node)
            if node.value is not None:
                assert node.interval is None, "node with both value and interval set"
                c = ls.constraints_assignments_equal_value(node_full_assignments, node.value)
                self.constraints_linear.extend(c)
            elif node.interval is not None:
                low, high = node.interval
                c1 = ls.constraints_assignments_greater_or_equal_value(node_full_assignments, low)
                c2 = ls.constraints_assignments_less_or_equal_value(node_full_assignments, high)
                self.constraints_linear.extend(c1)
                self.constraints_linear.extend(c2)


class NNor(Semantics):
    """
    Noisy not-or semantics:  TODO
    per default without prior probabilities
    p_A_nB_nC = 1 * p_nB_nC
    p_A_nB_C  = (1 - t) * p_nB_C
    p_A_B_nC  = (1 - s) * p_B_nC
    p_A_B_C   = (1 - s ) * (1 - t) * p_B_C
    """
    def __init__(self, af: DPGM, use_prior_probs=False, complemented=False):
        self.use_prior_probs = use_prior_probs
        super().__init__(af, complemented)

    def generate_z3_constraints(self, z3i: Z3Instance):
        # we use attack strength, so a prob_var should be created for each edge
        z3i.generate_edge_vars()

        for node in self.all_nodes:

            node_prior_prob_var = z3i.create_real_var("pr_" + node.name)  # e.g. pr_A
            if self.use_prior_probs:
                if node.value is not None:
                    # self.add_z3_constraint(node_prior_prob_var == node.value, node=node)
                    self.add_z3_constraint(node_prior_prob_var.__eq__(node.value), node=node)
                elif node.interval is not None:
                    i_min, i_max = node.interval
                    constraint = z3.And(node_prior_prob_var >= i_min, node_prior_prob_var <= i_max)
                    self.add_z3_constraint(constraint, node=node)
                else:
                    self.add_z3_constraint(z3.And(node_prior_prob_var >= 0, node_prior_prob_var <= 1), node=node)
            else:
                self.add_z3_constraint(node_prior_prob_var == 1, node=node)

            if node.is_initial():
                node_prob = z3i.get_node_prob_var(node)
                # self.add_z3_constraint(node_prob == node_prior_prob_var, node=node)
                self.add_z3_constraint(node_prob.__eq__(node_prior_prob_var), node=node)
                continue

            for parent_assignment in asg.generate(node.get_parents()):
                parent_prob_var = z3i.get_prob_var(parent_assignment)  # e.g. p_nB_C
                assignment = tuple(sorted(list(parent_assignment) + [(node, True)]))
                prob_var = z3i.get_prob_var(assignment)  # e.g. p_A_nB_C

                product = node_prior_prob_var * parent_prob_var
                for (parent, status) in parent_assignment:
                    if status:
                        edge = node.get_parent_edge(parent)
                        edge_var = z3i.get_edge_var(edge)
                        product *= (1 - edge_var)
                # self.add_z3_constraint(prob_var == product, node=node)
                self.add_z3_constraint(prob_var.__eq__(product), node=node)


class NNorAF(NNor):
    """
    Noisy not-or semantics:  TODO
    with prior probabilities
    p_A_nB_nC = prA * p_nB_nC
    p_A_nB_C  = prA * (1 - t) * p_nB_C
    p_A_B_nC  = prA * (1 - s) * p_B_nC
    p_A_B_C   = prA * (1 - s ) * (1 - t) * p_B_C
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(af, use_prior_probs=True, complemented=complemented)


class CFs(Semantics):
    """
    Conflict-freeness semantics with attack strengths: P(A,B) <= 1-s for all attacks A -s-> B.
    """
    def generate_z3_constraints(self, z3i: Z3Instance):
        # we use attack strength, so a prob_var should be created for each edge
        z3i.generate_edge_vars()

        for edge in self.af.get_edges():
            edge_var = z3i.get_edge_var(edge)
            assignment: List[Tuple[Node, bool]] = [(edge.node_from, True), (edge.node_to, True)]
            prob_var = z3i.get_prob_var(tuple(assignment))
            self.add_z3_constraint(prob_var <= 1 - edge_var, edge=edge)


class StrengthCF(Semantics):
    """
    Alternative conflict-freeness semantics with attack strengths: "P(A,B) <= (1-s) * P(A)" for all attacks A -s-> B.
    """
    def generate_z3_constraints(self, z3i: Z3Instance):
        # we use attack strength, so a prob_var should be created for each edge
        z3i.generate_edge_vars()

        for edge in self.af.get_edges():
            edge_var = z3i.get_edge_var(edge)
            assignment: List[Tuple[Node, bool]] = [(edge.node_from, True), (edge.node_to, True)]
            prob_var = z3i.get_prob_var(tuple(assignment))
            node_to_prob = z3i.get_node_prob_var(edge.node_to)
            self.add_z3_constraint(prob_var <= (1 - edge_var) * node_to_prob, edge=edge)


########################################
# Strength and Support
########################################

class StrengthSupportCF(Semantics):
    """
    Treats arrows as support with strengths: "P(A,B) >= s * P(A)" for all supports A -s-> B.
    """
    def generate_z3_constraints(self, z3i: Z3Instance):
        # we use attack strength, so a prob_var should be created for each edge
        z3i.generate_edge_vars()

        for edge in self.af.get_edges():
            edge_var = z3i.get_edge_var(edge)
            assignment: List[Tuple[Node, bool]] = [(edge.node_from, True), (edge.node_to, True)]
            prob_var = z3i.get_prob_var(tuple(assignment))
            node_to_prob = z3i.get_node_prob_var(edge.node_to)
            # self.add_z3_constraint(prob_var >= edge_var * node_to_prob, edge=edge)
            self.add_z3_constraint(prob_var.__ge__(edge_var * node_to_prob), edge=edge)


########################################
# Dirac versions of classical semantics
########################################

class DiracClassicalSemantics(Semantics):
    """
    Lifts classical semantics into probabilistic semantics by admitting the Dirac-distributions corresponding to the
    classical semantics' extensions.
    E.g., a distribution P is Dirac-admissible if it is a Dirac distribution and P(beta) = 1 for some assignment beta
    implies that the set of arguments holding in beta is an admissible set.

    This is implemented by adding a constraint "P(beta_1) = 1 OR P(beta_2) = 1 OR ... OR P(beta_n) = 1" where beta_i are
    the assignments corresponding to the respective semantics' extensions. Note that this constraint also ensures that
    distributions satisfying it are Dirac distributions, so no additional Dirac constraints are added.
    """
    def __init__(self, classical_semantics: Type[classical.ClassicalSemantics], af: DPGM, complemented=False):
        self.classical_semantics = classical_semantics
        super().__init__(af, complemented)

    def generate_constraints(self, si: SolverInstance):
        cs = self.classical_semantics(self.af)
        or_list = []
        for extension in cs.get_extensions():
            assignment = asg.from_extension(extension, self.all_nodes)
            symbol = si.get_symbol(assignment)
            or_list.append(Equals(symbol, Real(1)))
        self.add_constraint(Or(or_list))

    def generate_z3_constraints(self, z3i: Z3Instance):
        cs = self.classical_semantics(self.af)
        or_list = []
        for extension in cs.get_extensions():
            assignment = asg.from_extension(extension, self.all_nodes)
            prob_var = z3i.get_prob_var(assignment)
            or_list.append(prob_var == 1)
        if or_list:
            self.add_z3_constraint(z3.Or(or_list))
        else:
            self.add_z3_constraint(z3.BoolVal(False, ctx=z3i.context))


class DiracCF(DiracClassicalSemantics):
    """
    Dirac-conflict-free semantics: Only allows Dirac-distributions corresponding to conflict-free extensions.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.CF, af, complemented)


class DiracAdm(DiracClassicalSemantics):
    """
    Dirac-admissible semantics: Only allows Dirac-distributions corresponding to admissible extensions.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.Admissible, af, complemented)


class DiracCmp(DiracClassicalSemantics):
    """
    Dirac-complete semantics: Only allows Dirac-distributions corresponding to complete extensions.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.Complete, af, complemented)


class DiracGrn(DiracClassicalSemantics):
    """
    Dirac-grounded semantics: Only allows Dirac-distributions corresponding to grounded extensions.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.Grounded, af, complemented)


class DiracPrf(DiracClassicalSemantics):
    """
    Dirac-preferred semantics: Only allows Dirac-distributions corresponding to preferred extensions.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.Preferred, af, complemented)


class DiracSStl(DiracClassicalSemantics):
    """
    Dirac-semi-stable semantics: Only allows Dirac-distributions corresponding to semi-stable extensions.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.SemiStable, af, complemented)


class DiracStl(DiracClassicalSemantics):
    """
    Dirac-stable semantics: Only allows Dirac-distributions corresponding to stable extensions.
    """
    def __init__(self, af: DPGM, complemented=False):
        super().__init__(classical.Stable, af, complemented)


###################
# Helper functions
###################

def get_semantics_class_by_name(name: str):
    """
    By dark magic, get the semantics class given its name as string, e.g. "wNor" to yield the class WNor.

    :param name: the name of the semantics (case insensitive)
    :return: The semantics class corresponding to the name
    """
    queue = Semantics.__subclasses__().copy()
    while queue:
        semantics_class = queue.pop()
        if name.lower() == semantics_class.__name__.lower():
            return semantics_class
        queue.extend(semantics_class.__subclasses__())
    return None


def all_semantics_names():
    """
    :return: A list of the names of all semantics declared in this file
    """
    # helper classes which do not form semantics themselves
    exceptions = ["ElmClassicalSemantics", "DiracClassicalSemantics"]

    names = []
    # use a queue to recursively also get the names of subclasses
    queue = Semantics.__subclasses__().copy()
    while queue:
        semantics_class = queue.pop()
        queue.extend(semantics_class.__subclasses__())
        if semantics_class.__name__ not in exceptions:
            names.append(semantics_class.__name__)
    return names


def nice_fraction(x, max_fraction_denominator=MAX_FRACTION_DENOMINATOR) -> Fraction:
    """

    >>> Fraction(0.7)
    Fraction(3152519739159347, 4503599627370496)
    >>> nice_fraction(0.7)
    Fraction(7, 10)

    """
    return Fraction(x).limit_denominator(max_fraction_denominator)
