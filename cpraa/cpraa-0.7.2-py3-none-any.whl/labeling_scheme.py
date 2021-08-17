from typing import NewType

import z3
from pysmt.shortcuts import GE, LE, Real, And, GT, LT, Equals, Or

from DPGM import Node
from distribution import Distribution
from solver_instance import SolverInstance
from z3_instance import Z3Instance

# label constants
Label = NewType("Label", str)
l_in = Label("in")
l_out = Label("out")
l_undec = Label("undec")


class LabelingScheme:

    num_args = 0  # The number of arguments each labeling scheme takes

    def get_label(self, argument: Node, distribution: Distribution) -> Label:
        """
        Get the label of the given argument according the given model and the labeling approach.
        :return: l_in, l_out or l_undec
        """
        # implemented by subclasses
        pass

    def get_constraints(self, node: Node, si: SolverInstance):
        """
        Return a list of constraints on the probabilistic variable of the node where each constraint corresponds to a
        different label. I.e. for cautious labeling and node A, return [p_A == 1, p_A == 0, And(p_A < 1, p_A > 0)].
        Used to compute all labelings.
        """
        # implemented by subclasses
        return []

    def get_constraints_z3(self, node: Node, z3i: Z3Instance):
        """
        Return a list of constraints on the probabilistic variable of the node where each constraint corresponds to a
        different label. I.e. for cautious labeling and node A, return [p_A == 1, p_A == 0, And(p_A < 1, p_A > 0)].
        Used to compute all labelings.
        """
        # implemented by subclasses
        return []


class Threshold(LabelingScheme):
    """
    Given two thresholds t_in and t_out, all nodes with probability
     - greater equal t_in are labeled 'in',
     - less than or equal to t_out are labeled 'out',
     - and between t_in and t_out are labeled 'undec'.
     """
    num_args = 2

    def __init__(self, t_in: float, t_out: float):
        self.t_in = t_in
        self.t_out = t_out

    def get_label(self, node: Node, distribution: Distribution):
        prob = distribution.get_marginal_probability(node)
        if prob >= self.t_in:
            return l_in
        elif prob <= self.t_out:
            return l_out
        else:
            return l_undec

    def get_constraints(self, node: Node, si: SolverInstance):
        node_prob = si.get_node_symbol(node)
        in_constraint = GE(node_prob, Real(self.t_in))
        out_constraint = LE(node_prob, Real(self.t_out))
        undec_constraint = And(LT(node_prob, Real(self.t_in)), GT(node_prob, Real(self.t_out)))
        return [in_constraint, out_constraint, undec_constraint]

    def get_constraints_z3(self, node: Node, z3i: Z3Instance):
        node_prob = z3i.get_node_prob_var(node)
        in_constraint = node_prob >= self.t_in
        out_constraint = node_prob <= self.t_out
        undec_constraint = z3.And(node_prob < self.t_in, node_prob > self.t_out, z3i.context)
        return [in_constraint, out_constraint, undec_constraint]


class Cautious(Threshold):
    """
    Arguments with probability 1 are labeled 'in', those with probability 0 are labeled 'out' and all others are
    labeled 'undec'.
    """
    num_args = 0

    def __init__(self):
        super().__init__(1.0, 0.0)


class Firm(LabelingScheme):
    """
    Arguments with probability 0.5 are labeled 'undec', those with probability >0.5 are labeled 'in' and all those with
    probability <0.5 are labeled 'out'.
    """
    def get_label(self, node: Node, distribution: Distribution):
        prob = distribution.get_marginal_probability(node)
        if prob > 0.5:
            return l_in
        elif prob < 0.5:
            return l_out
        else:
            return l_undec

    def get_constraints(self, node: Node, si: SolverInstance):
        node_prob = si.get_node_symbol(node)
        in_constraint = GT(node_prob, Real(0.5))
        out_constraint = LT(node_prob, Real(0.5))
        undec_constraint = Equals(node_prob, Real(0.5))
        return [undec_constraint, in_constraint, out_constraint]
        # undec first because checking for equality is probably easier than inequalities

    def get_constraints_z3(self, node: Node, z3i: Z3Instance):
        node_prob = z3i.get_node_prob_var(node)
        in_constraint = node_prob > 0.5
        out_constraint = node_prob < 0.5
        undec_constraint = node_prob == 0.5
        return [undec_constraint, in_constraint, out_constraint]
        # undec first because checking for equality is probably easier than inequalities


class ThresholdClassicalOld(LabelingScheme):
    """
    Requires two thresholds t_in and t_min_attack_out. A node is labeled
     - 'in' if its probability is greater or equal t_in,
     - 'out' if it is not labeled 'in' and one of its attackers has probability greater or equal t_min_attack_out, and
     - 'undec' in all other cases.

     Uses old implementation of get_constraints_z3 which does not necessarily produce unique labelings, though might be
     faster in some cases.
     """
    num_args = 2

    def __init__(self, t_in: float, t_min_attack_out: float):
        self.t_in = t_in
        self.t_att_out = t_min_attack_out

    def get_label(self, node: Node, distribution: Distribution):
        node_prob = distribution.get_marginal_probability(node)
        if node_prob >= self.t_in:
            return l_in
        else:
            label = l_undec
            for attacker in node.get_parents():
                attacker_prob = distribution.get_marginal_probability(attacker)
                if attacker_prob >= self.t_att_out:
                    label = l_out
                    break
            return label

    def get_constraints(self, node: Node, si: SolverInstance):
        node_prob = si.get_node_symbol(node)
        if self.t_in == self.t_att_out:
            in_constraint = GE(node_prob, Real(self.t_in))
            not_in_constraint = LT(node_prob, Real(self.t_in))
            return [in_constraint, not_in_constraint]
        else:
            t_max = max(self.t_in, self.t_att_out)
            t_min = min(self.t_in, self.t_att_out)
            first_constraint = GE(node_prob, Real(t_max))
            second_constraint = LT(node_prob, Real(t_min))
            third_constraint = And(LT(node_prob, Real(t_max)), GE(node_prob, Real(t_min)))
            return [first_constraint, second_constraint, third_constraint]

    def get_constraints_z3(self, node: Node, z3i: Z3Instance):
        node_prob = z3i.get_node_prob_var(node)
        if self.t_in == self.t_att_out:
            in_constraint = node_prob >= self.t_in
            not_in_constraint = node_prob < self.t_in
            return [in_constraint, not_in_constraint]
        else:
            t_max = max(self.t_in, self.t_att_out)
            t_min = min(self.t_in, self.t_att_out)
            first_constraint = node_prob >= t_max
            second_constraint = node_prob < t_min
            third_constraint = z3.And(node_prob < t_max, node_prob >= t_min, z3i.context)
            return [first_constraint, second_constraint, third_constraint]


class ClassicalOld(ThresholdClassicalOld):
    """
    A node is labeled
     - 'in' if it holds with probability 1,
     - 'out' if it is not labeled 'in' and one of its attackers holds with probability 1, and
     - 'undec' in all other cases.

     Uses old implementation of get_constraints_z3 which does not necessarily produce unique labelings, though might be
     faster in some cases.
    """
    num_args = 0

    def __init__(self):
        super().__init__(1.0, 1.0)


class ThresholdClassical(LabelingScheme):
    """
    Requires two thresholds t_in and t_min_attack_out. A node is labeled
     - 'in' if its probability is greater or equal t_in,
     - 'out' if it is not labeled 'in' and one of its attackers has probability greater or equal t_min_attack_out, and
     - 'undec' in all other cases.
     """
    num_args = 2

    def __init__(self, t_in: float, t_min_attack_out: float):
        self.t_in = t_in
        self.t_att_out = t_min_attack_out

    def get_label(self, node: Node, distribution: Distribution):
        node_prob = distribution.get_marginal_probability(node)
        if node_prob >= self.t_in:
            return l_in
        else:
            label = l_undec
            for attacker in node.get_parents():
                attacker_prob = distribution.get_marginal_probability(attacker)
                if attacker_prob >= self.t_att_out:
                    label = l_out
                    break
            return label

    def get_constraints(self, node: Node, si: SolverInstance):
        node_prob = si.get_node_symbol(node)
        in_constraint = GE(node_prob, Real(self.t_in))
        parent_out_constraint = Or(
            [GE(si.get_node_symbol(parent), Real(self.t_att_out)) for parent in node.get_parents()])
        out_constraint = And(GT(node_prob, Real(self.t_in)), parent_out_constraint)
        parent_undec_constraint = And(
            [LT(si.get_node_symbol(parent), Real(self.t_att_out)) for parent in node.get_parents()])
        undec_constraint = And(LT(node_prob, Real(self.t_in)), parent_undec_constraint)
        return [in_constraint, out_constraint, undec_constraint]

    def get_constraints_z3(self, node: Node, z3i: Z3Instance):
        node_prob = z3i.get_node_prob_var(node)
        in_constraint = node_prob >= self.t_in
        parent_out_constraint = z3.Or(
            [z3i.get_node_prob_var(parent) >= self.t_att_out for parent in node.get_parents()])
        out_constraint = z3.And(node_prob < self.t_in, parent_out_constraint)
        parent_undec_constraint = z3.And(
            [z3i.get_node_prob_var(parent) < self.t_att_out for parent in node.get_parents()])
        undec_constraint = z3.And(node_prob < self.t_in, parent_undec_constraint)

        return [in_constraint, out_constraint, undec_constraint]


class Classical(ThresholdClassical):
    """
    A node is labeled
     - 'in' if it holds with probability 1,
     - 'out' if it is not labeled 'in' and one of its attackers holds with probability 1, and
     - 'undec' in all other cases.
    """
    num_args = 0

    def __init__(self):
        super().__init__(1.0, 1.0)


class Optimistic(LabelingScheme):
    """
    A node is labeled
     - 'in' if it holds with probability larger than 0, and
     - 'out' otherwise.
     """

    def get_label(self, node: Node, distribution: Distribution):
        prob = distribution.get_marginal_probability(node)
        if prob > 0.0:
            return l_in
        else:
            return l_out

    def get_constraints(self, node: Node, si: SolverInstance):
        node_prob = si.get_node_symbol(node)
        in_constraint = GT(node_prob, Real(0))
        out_constraint = Equals(node_prob, Real(0))
        return [in_constraint, out_constraint]

    def get_constraints_z3(self, node: Node, z3i: Z3Instance):
        node_prob = z3i.get_node_prob_var(node)
        in_constraint = node_prob > 0
        out_constraint = node_prob == 0
        return [in_constraint, out_constraint]


class Pessimistic(LabelingScheme):
    """
    A node is labeled
     - 'in' if it holds with probability 1, and
     - 'out' otherwise.
     """

    def get_label(self, node: Node, distribution: Distribution):
        prob = distribution.get_marginal_probability(node)
        if prob == 1.0:
            return l_in
        else:
            return l_out

    def get_constraints(self, node: Node, si: SolverInstance):
        node_prob = si.get_node_symbol(node)
        in_constraint = Equals(node_prob, Real(1))
        out_constraint = LT(node_prob, Real(1))
        return [in_constraint, out_constraint]

    def get_constraints_z3(self, node: Node, z3i: Z3Instance):
        node_prob = z3i.get_node_prob_var(node)
        in_constraint = node_prob == 1
        out_constraint = node_prob < 1
        return [in_constraint, out_constraint]


###################
# Helper functions
###################

def get_labeling_scheme_class(name: str):
    """
    By dark magic, get the labeling scheme class given its name as string, e.g. "firm" to yield the class 'Firm'.

    :param name: the name of the labeling scheme class (case insensitive)
    :return: the labeling scheme class corresponding to the name, or None if no match was found
    """
    name = name.lower()
    queue = LabelingScheme.__subclasses__().copy()
    while queue:
        labeling_class = queue.pop()
        if name == labeling_class.__name__.lower():
            return labeling_class
        queue.extend(labeling_class.__subclasses__())
    return None


def get_all_labeling_scheme_names():
    """
    :return: a list of the names of all available labeling schemes
    """
    names = []
    queue = LabelingScheme.__subclasses__().copy()
    while queue:
        labeling_class = queue.pop()
        queue.extend(labeling_class.__subclasses__())
        names.append(labeling_class.__name__)
    return names
