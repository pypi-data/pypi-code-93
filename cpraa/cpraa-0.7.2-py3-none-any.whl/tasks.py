from typing import List, Set

import z3
import pysmt.shortcuts as smt

from DPGM import Node
from distribution import Distribution
from labeling import Labeling
from labeling_scheme import LabelingScheme
from linear_solver import LinearSolver, LinearConstraintError
from semantics import Semantics
from solver_instance import SolverInstance
from timer import Timer
from z3_instance import Z3Instance


def ls_constraints(ls: LinearSolver, semantics: List[Semantics]):
    semantics_constraints_timer = Timer(output_string="Generating constraints for all semantics took")
    constraints = []
    for sem in semantics:
        try:
            constraints.extend(sem.get_linear_constraints(ls))
        except NotImplementedError:
            raise LinearConstraintError("No linear constraints available (or implemented) for semantics '"
                                        + str(sem) + "'") from None
    semantics_constraints_timer.stop()
    return constraints


def get_model_z3(z3i: Z3Instance, semantics: List[Semantics], constraints=None):
    """
    Check if a distribution satisfying the constraints of all semantics plus potential additional constraints exists.
    If so, return it as a model.

    :param z3i: the underlying z3 instance with the AF
    :param semantics: a list of semantics
    :param constraints: optional list of additional constraints
    :return: A model if one exists, None otherwise
    """
    if not constraints:
        constraints = []

    semantics_constraints_timer = Timer(output_string="Generating constraints for all semantics took")
    for sem in semantics:
        # print(sem.__class__.__name__, sem.get_z3_constraints(z3i))
        constraints.extend(sem.get_z3_constraints(z3i))
    semantics_constraints_timer.stop()

    result = z3i.check_satisfiability(constraints)
    if result == z3.sat:
        return z3i.solver.model()
    else:
        return None


def get_model(si: SolverInstance, semantics: List[Semantics], constraints=None):
    """
    Check if a distribution satisfying the constraints of all semantics plus potential additional constraints exists.
    If so, return it as a model.

    :param si: the interface to the smt solvers
    :param semantics: a list of semantics
    :param constraints: optional list of additional constraints
    :return: A model if one exists, None otherwise
    """
    if not constraints:
        constraints = []

    semantics_constraints_timer = Timer(output_string="Generating constraints for all semantics took")
    for sem in semantics:
        # print(str(sem) + ":", sem.get_constraints(si))
        constraints.extend(sem.get_constraints(si))
    semantics_constraints_timer.stop()

    return si.get_model(constraints)


def get_one_distribution(si: SolverInstance, semantics: List[Semantics]) -> Distribution:
    """
    Return one distribution satisfying all constraints if one exists.

    :param si: the interface to the smt solvers
    :param semantics: a list of semantics
    :return: one distribution if one exists
    """
    model = get_model(si, semantics)
    if model:
        return si.distribution_from_model(model)


def get_one_distribution_z3(z3i: Z3Instance, semantics: List[Semantics]) -> Distribution:
    """
    Return one distribution satisfying all constraints if one exists.

    :param z3i: the underlying z3 instance with the AF
    :param semantics: a list of semantics
    :return: one distribution if one exists
    """
    model = get_model_z3(z3i, semantics)
    if model:
        return z3i.distribution_from_model(model)


def get_one_distribution_linear(ls: LinearSolver, semantics: List[Semantics]) -> Distribution:
    """
    Return one distribution satisfying all constraints if one exists.
    Semantics that do not admit linear constraints are skipped.

    :param ls: the linear solver instance
    :param semantics: a list of semantics
    :return: one distribution if one exists
    """
    constraints = ls_constraints(ls, semantics)
    return ls.any_solution(constraints)


def get_corner_distributions(ls: LinearSolver, semantics: List[Semantics]) -> List[Distribution]:
    """
    Compute the corner distribution of the convex hull of the solution space using a linear solver. The infinite set of
    all solutions is then given by the convex combinations of these distributions.

    Semantics that do not admit linear constraints are skipped.

    :param ls: the linear solver instance
    :param semantics: a list of semantics
    :return: the distributions forming corners of the convex solution space
    """
    constraints = ls_constraints(ls, semantics)
    return ls.corner_distributions(constraints)


def get_satisfying_labeling_z3(z3i: Z3Instance, lab: LabelingScheme, semantics: List[Semantics]) -> Labeling:
    """
    Get a labeling satisfying the given semantics under the given labeling scheme. Returns None if no such labeling
    exists.

    :param z3i: the underlying z3 instance with the AF
    :param lab: a labeling scheme
    :param semantics: a list of semantics
    :return: A labeling or None
    """
    model = get_model_z3(z3i, semantics)
    if model:
        return Labeling(lab, z3i.distribution_from_model(model), z3i.af)


def get_all_satisfying_labelings(si: SolverInstance, lab: LabelingScheme, semantics: List[Semantics]) -> Set[Labeling]:
    """
    Compute all labelings under the given labeling scheme that satisfy the given semantics.

    :param si: the interface to the smt solvers
    :param lab: a labeling scheme
    :param semantics: a list of semantics
    :return: a list of labelings
    """
    semantics_constraints_timer = Timer(output_string="Generating constraints for all semantics took")
    constraints = []
    for sem in semantics:
        constraints.extend(sem.get_constraints(si))
    semantics_constraints_timer.stop()

    solver = si.get_solver()
    solver.add_assertion(smt.And(constraints))

    # test overall satisfiability
    sat = solver.solve()
    # print("Overall satisfiability:", sat)
    if not sat:
        return set()

    candidate_constraints = [[]]
    labelings = set()
    num_of_checks = 1
    num_remaining_nodes = len(si.af.get_nodes())
    for node in si.af.get_nodes():
        num_remaining_nodes -= 1
        # print(node.name)
        next_candidate_constraints = []
        for candidate_constraint in candidate_constraints:
            for const in lab.get_constraints(node, si):
                new_candidate_constraint = candidate_constraint.copy()
                new_candidate_constraint.append(const)

                result = solver.is_sat(smt.And(new_candidate_constraint))
                num_of_checks += 1
                if result:
                    # print("new_candidate_constraint", new_candidate_constraint)
                    next_candidate_constraints.append(new_candidate_constraint)
                    # add labelings if we are at the leaves of the search tree
                    if num_remaining_nodes == 0:
                        model = solver.get_model()
                        distribution = si.distribution_from_model(model)
                        labeling = Labeling(lab, distribution, si.af)
                        # assert labeling not in labelings, "Labeling found twice: " + str(labeling)
                        labelings.add(labeling)
        candidate_constraints = next_candidate_constraints

    # # How many constraints do we have for each node? Usually as many as there are labelings, though for some labeling
    # # schemes there are fewer
    # branching = len(lab.get_constraints(list(si.af.get_nodes())[0], si))
    # # number of nodes in a perfect k-ary tree of depth n = number of nodes and k = branching,
    # # i.e., wc = (k**(n+1) - 1) // (k-1)
    # worst_case_checks = (branching**(len(si.af.get_nodes()) + 1) - 1) // (branching - 1)
    #
    # print("Finished. Performed {} checks (worst case: {}) and found {} labelings.".format(
    #     num_of_checks, worst_case_checks, len(labelings)))
    return labelings


def get_all_satisfying_labelings_z3(z3i: Z3Instance, lab: LabelingScheme, semantics: List[Semantics]) -> Set[Labeling]:
    """
    Compute all labelings under the given labeling scheme that satisfy the given semantics.

    :param z3i: the underlying z3 instance with the AF
    :param lab: a labeling scheme
    :param semantics: a list of semantics
    :return: a list of labelings
    """
    semantics_constraints_timer = Timer(output_string="Generating constraints for all semantics took")
    semantics_constraints = []
    for sem in semantics:
        # print(sem.__class__.__name__, sem.get_z3_constraints(z3i))
        semantics_constraints.extend(sem.get_z3_constraints(z3i))
    semantics_constraints_timer.stop()

    z3i.solver.reset()
    z3i.solver.add(z3i.constraints)
    z3i.solver.add(z3i.edge_constraints)
    z3i.solver.add(semantics_constraints)

    # test overall satisfiability
    result = z3i.solver.check()
    # print("Overall satisfiability:", result)
    if result != z3.sat:
        return set()

    candidate_constraints = [[]]
    labelings = set()
    num_of_checks = 1
    num_remaining_nodes = len(z3i.af.get_nodes())

    for node in z3i.af.get_nodes():
        num_remaining_nodes -= 1
        # print(node.name)
        next_candidate_constraints = []
        for candidate_constraint in candidate_constraints:
            for const in lab.get_constraints_z3(node, z3i):
                new_candidate_constraint = candidate_constraint.copy()
                new_candidate_constraint.append(const)
                # add candidate constraints to solver
                z3i.solver.push()  # this adds an backtracking point
                # print(z3i.solver)
                z3i.solver.add(new_candidate_constraint)
                # print(z3i.solver)
                result = z3i.solver.check()
                num_of_checks += 1
                if result == z3.sat:
                    # print("new_candidate_constraint", new_candidate_constraint)
                    next_candidate_constraints.append(new_candidate_constraint)
                    # add labelings if we are at the leaves of the search tree
                    if num_remaining_nodes == 0:
                        model = z3i.solver.model()
                        labeling = Labeling(lab, z3i.distribution_from_model(model), z3i.af)
                        # assert labeling not in labelings, "Labeling found twice: " + str(labeling)
                        labelings.add(labeling)
                #  remove candidate constraints from solver
                z3i.solver.pop()  # go back to the backtracking point
        candidate_constraints = next_candidate_constraints

    # # How many constraints do we have for each node? Usually as many as there are labelings, though for some labeling
    # # schemes there are fewer
    # branching = len(lab.get_constraints_z3(list(z3i.af.get_nodes())[0], z3i))
    # # number of nodes in a perfect k-ary tree of depth n = number of nodes and k = branching,
    # # i.e., wc = (k**(n+1) - 1) // (k-1)
    # worst_case_checks = (branching**(len(z3i.af.get_nodes()) + 1) - 1) // (branching - 1)
    #
    # print("Finished. Performed {} checks (worst case: {}) and found {} labelings.".format(
    #     num_of_checks, worst_case_checks, len(labelings)))
    return labelings


def compare_semantics_by_labelings_z3(z3i: Z3Instance, lab: LabelingScheme, semantics_a: List[Semantics],
                                      semantics_b: List[Semantics]):
    """

    :param z3i: the underlying z3 instance
    :param lab: the labeling scheme
    :param semantics_a: the first set of semantics
    :param semantics_b: the second set of semantics
    :return: three sets of labelings for `A u B`, `A - B` and `B - A`
    """

    labelings_a = set(get_all_satisfying_labelings_z3(z3i, lab, semantics_a))
    labelings_b = set(get_all_satisfying_labelings_z3(z3i, lab, semantics_b))

    labelings_both = labelings_a.union(labelings_b)
    labelings_only_a = labelings_a.difference(labelings_b)
    labelings_only_b = labelings_b.difference(labelings_a)
    return labelings_both, labelings_only_a, labelings_only_b


def check_credulous_acceptance(si: SolverInstance, semantics: List[Semantics], argument: Node, threshold: float = 1):
    """
    Check if the given argument is credulously accepted, i.e. there exists at least one distribution satisfying the
    given semantics that assigns the argument a probability greater or equal to the threshold (equal to 1 by default).

    :param si: the interface to the smt solvers
    :param semantics: a list of semantics
    :param argument: an argument from the AF
    :param threshold: optional: a float from the interval [0,1]
    :return: True + a model if one exists, False otherwise
    """
    argument_symbol = si.get_node_symbol(argument)
    constraints = [smt.GE(argument_symbol, smt.Real(threshold))]
    model = get_model(si, semantics, constraints)
    if model:
        distribution = si.distribution_from_model(model)
        return True, distribution
    else:
        return False, None


def check_credulous_acceptance_z3(z3i: Z3Instance, semantics: List[Semantics], argument: Node, threshold: float = 1):
    """
    Check if the given argument is credulously accepted, i.e. there exists at least one distribution satisfying the
    given semantics that assigns the argument a probability greater or equal to the threshold (equal to 1 by default).

    :param z3i: the underlying z3 instance with the AF
    :param semantics: a list of semantics
    :param argument: an argument from the AF
    :param threshold: optional: a float from the interval [0,1]
    :return: True + a model if one exists, False otherwise
    """
    argument_prob = z3i.get_node_prob_var(argument)
    constraints = [argument_prob >= threshold]
    model = get_model_z3(z3i, semantics, constraints)
    if model:
        distribution = z3i.distribution_from_model(model)
        return True, distribution
    else:
        return False, None


def check_skeptical_acceptance(si: SolverInstance, semantics: List[Semantics], argument: Node, threshold: float = 1):
    """
    Check if the given argument is skeptically accepted, i.e. all distributions that satisfy the given semantics assign
    the argument a probability greater or equal to the threshold (equal to 1 by default).

    :param si: the interface to the smt solvers
    :param semantics: a list of semantics
    :param argument: an argument from the AF
    :param threshold: optional: a float from the interval [0,1]
    :return: True or False + counter example distribution
    """
    # "check if for all satisfying distributions, P(A) >= t holds"
    # <=> not "check if for one satisfying distribution, P(A) < t holds"
    argument_symbol = si.get_node_symbol(argument)
    constraints = [smt.LT(argument_symbol, smt.Real(threshold))]
    model = get_model(si, semantics, constraints)
    if model:
        distribution = si.distribution_from_model(model)
        return False, distribution
    else:
        return True, None


def check_skeptical_acceptance_z3(z3i: Z3Instance, semantics: List[Semantics], argument: Node, threshold: float = 1):
    """
    Check if the given argument is skeptically accepted, i.e. all distributions that satisfy the given semantics assign
    the argument a probability greater or equal to the threshold (equal to 1 by default).

    :param z3i: the underlying z3 instance with the AF
    :param semantics: a list of semantics
    :param argument: an argument from the AF
    :param threshold: optional: a float from the interval [0,1]
    :return: True or False + counter example distribution
    """
    # "check if for all satisfying distributions, P(A) >= t holds"
    # <=> not "check if for one satisfying distribution, P(A) < t holds"
    argument_prob = z3i.get_node_prob_var(argument)
    constraints = [argument_prob < threshold]
    model = get_model_z3(z3i, semantics, constraints)
    if model:
        distribution = z3i.distribution_from_model(model)
        return False, distribution
    else:
        return True, None


def maximize_marginal_probabilities(ls: LinearSolver, nodes: List[Node], semantics: List[Semantics]):
    """
    Compute the optimal distribution which maximizes the marginal probability of the given arguments while observing
    the given semantics' constraints.
    """
    constraints = ls_constraints(ls, semantics)
    return ls.optimize_marginal_prob(nodes, constraints, mode="max")


def minimize_marginal_probabilities(ls: LinearSolver, nodes: List[Node], semantics: List[Semantics]):
    """
    Compute the optimal distribution which minimizes the marginal probability of the given arguments while observing
    the given semantics' constraints.
    """
    constraints = ls_constraints(ls, semantics)
    return ls.optimize_marginal_prob(nodes, constraints, mode="min")
