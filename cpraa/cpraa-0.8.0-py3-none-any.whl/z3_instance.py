from typing import Dict, List, Tuple
from fractions import Fraction

import z3

from assignments import Assignment
import assignments as asg
from DPGM import DPGM, Node, Edge
from distribution import Distribution


class Z3Instance:
    """Class to bundle the declared probabilistic variables, the underlying full joint distribution."""

    def __init__(self, af: DPGM, assume_independence=False):
        self.af = af
        self.assume_independence = assume_independence  # when this flag is True, no full joint probability is built

        self.full_joint_prob_vars: Dict[str, z3.ArithRef] = dict()
        self.full_joint_assignments: List[Assignment] = []
        self.other_prob_vars: Dict[str, z3.ArithRef] = dict()
        self.real_vars: Dict[str, z3.ArithRef] = dict()
        self.constraints = set()

        self.edge_prob_vars: Dict[Edge, z3.ArithRef] = dict()
        self.edge_constraints = set()
        self.edge_prob_vars_generated = False

        # create a z3 solver
        self.context = z3.Context()
        self.solver = z3.Solver(ctx=self.context)

        if not self.assume_independence:
            self._generate_full_prob_vars()
            # # serialize the constraints for the full joint distribution
            # path = os.path.splitext(self.af.path)[0]  # strip the .tgf extension
            # path1 = path + "_full-joint-probvars.py"
            # with open(path1, "w") as f:
            #     f.write(repr(self.full_joint_prob_vars))
            # print("Written to", path1)
            # path2 = path + "_constraints.py"
            # with open(path2, "w") as f:
            #     f.write(repr(self.constraints))

        # workaround to have the prob vars corresponding to the nodes' marginal probabilities in the models
        # returned by z3
        for node in self.af.get_nodes():
            self.get_node_prob_var(node)

    def generate_edge_vars(self):
        """
        Generates a probabilistic variable for each edge. If an edge has a value or interval given, those are added as
        constraints.
        """
        if self.edge_prob_vars_generated:
            # There might be several calls to generate_edge_vars, but we want to add the constraints only once.
            return
        for edge in self.af.get_edges():
            self.edge_prob_vars[edge] = z3.Real(edge.label, self.context)
            edge_prob_var = self.edge_prob_vars[edge]
            if edge.value is not None:
                self.edge_constraints.add(edge_prob_var == edge.value)
                assert edge.interval is None, "both edge.value and edge.interval where given"
            elif edge.interval is not None:
                (val_min, val_max) = edge.interval
                self.edge_constraints.add(z3.And(edge_prob_var >= val_min, edge_prob_var <= val_max, self.context))
            else:
                self.edge_constraints.add(edge_prob_var >= 0)
                self.edge_constraints.add(edge_prob_var <= 1)
        self.edge_prob_vars_generated = True

    def get_edge_var(self, edge: Edge):
        if not self.edge_prob_vars_generated:
            self.generate_edge_vars()
        return self.edge_prob_vars[edge]

    def _generate_full_prob_vars(self):
        """Adds variables for the full joint distribution to the context. Adds the constraint that they sum to one."""
        constraint = 0
        if not self.full_joint_assignments:
            self.full_joint_assignments = asg.generate(sorted(self.af.get_nodes()))
        for assignment in self.full_joint_assignments:
            assignment_prob_name = prob_name(assignment)

            prob_var = z3.Real(assignment_prob_name, self.context)
            self.full_joint_prob_vars[assignment_prob_name] = prob_var
            self.constraints.add(prob_var >= 0)
            self.constraints.add(prob_var <= 1)
            constraint += prob_var

        constraint = 1 == constraint
        self.constraints.add(constraint)

    def get_node_prob_var(self, node: Node):
        return self.get_prob_var(tuple([(node, True)]))

    def get_prob_var(self, assignment: Assignment):
        """
        Get the z3 variable corresponding to a full or partial assignment.
        If it does not exist yet, it is created along with the constraints 'new_var >= 0', 'new_var <= 1' and the
        representation of new_var as sum of the full joint variables.
        """
        assert assignment, "empty assignment given"

        prob_var_name = prob_name(assignment)
        if prob_var_name in self.other_prob_vars:
            return self.other_prob_vars[prob_var_name]
        if prob_var_name in self.full_joint_prob_vars:
            return self.full_joint_prob_vars[prob_var_name]

        prob_var = z3.Real(prob_var_name, self.context)
        self.other_prob_vars[prob_var_name] = prob_var
        self.constraints.add(prob_var >= 0)
        self.constraints.add(prob_var <= 1)
        if not self.assume_independence:
            self.constraints.add(self.sum_out(assignment, prob_var))
        return prob_var

    def get_node_value(self, node: Node, model: z3.ModelRef):
        """
        Get the value assigned to a node's probabilistic variable by the given model.
        :return: The value as float
        """
        return get_prob_var_value(self.get_node_prob_var(node), model)

    def create_real_var(self, name: str):
        """
        Creates and returns an auxiliary z3 real variable.
        """
        if name in self.real_vars:
            raise ValueError("A real var with name '" + name + "' already exists.")
        real_var = z3.Real(name, self.context)
        self.real_vars[name] = real_var
        return real_var

    def sum_out(self, part_assignment: Assignment, part_assignment_prob_var):
        """[(A,True),(B,False)], [A,B,C] -> p_A_nB = p_A_nB_C + p_A_nB_nC"""
        full_assignments = asg.sum_out(part_assignment, self.af.get_nodes())
        sum_list = []
        for assignment in full_assignments:
            assignment_name = prob_name(assignment)
            prob_var = self.full_joint_prob_vars[assignment_name]
            sum_list.append(prob_var)
        constraint = part_assignment_prob_var == z3.Sum(sum_list)
        return constraint
    
    def add_constraints(self, constraints):
        for cons in constraints:
            self.constraints.add(cons)

    def check_satisfiability(self, prob_constraints) -> z3.CheckSatResult:
        """
        Add internal and given constraints to the solver and check for a satisfying model.

        :param prob_constraints: a list of constraints
        :return: A z3 CheckSatResult, i.e. sat, unsat or unknown
        """
        self.solver.reset()
        self.solver.add(self.constraints)
        # print("self.constraints:", self.constraints)
        self.solver.add(self.edge_constraints)
        # print("self.edge_constraints", self.edge_constraints)
        self.solver.add(prob_constraints)
        # print("prob_constraints", prob_constraints)

        result = self.solver.check()
        # print(self.solver.to_smt2())
        # print(result)
        # if result == z3.sat:
        #     model = self.solver.model()
        return result

    # def print_distribution(self, model: z3.ModelRef, nodes=None, only_positive=False):
    #     """
    #     Print distribution given by the model over the assignments of the given nodes.
    #     If no list of nodes is given, the distributions over all nodes in the AF is used.
    #     """
    #     if not nodes:
    #         nodes = self.af.get_nodes()
    #     node_assignments = asg.generate(nodes)
    #     for assignment in node_assignments:
    #         prob_var = self.get_prob_var(assignment)
    #         value = get_prob_var_value(prob_var, model)
    #         if not only_positive or value > 0:
    #             asg.print_assignment_prob(assignment, value)
    #             # print(prob_var, "=", value)

    def generate_independence_constraints(self, a: List[Node], b: List[Node], c: List[Node]):
        """
        Generate constraints stating that the nodes in A are independent of the nodes in B given the nodes in C.
        For each assignment a_A, a_B and a_C, we have
                 P(a_A | a_BC) = P(a_A | a_C)
        <=> P(a_ABC) / P(a_BC) = P(a_A | a_C)
        <=>           P(a_ABC) = P(a_BC) * P(a_A | a_C)   (this would suffice if P(a_A | a_C) is known from a CPT)
        <=>           P(a_ABC) = P(a_BC) * P(a_AC) / P(a_C)
        <=>  P(a_C) * P(a_ABC) = P(a_BC) * P(a_AC)
        """
        all_nodes = sorted(a + b + c)
        constraints = []
        for assignment in asg.generate(all_nodes):
            a_ABC = assignment
            p_ABC = self.get_prob_var(a_ABC)
            a_BC: List[Tuple[Node, bool]] = [(node, v) for (node, v) in assignment if node in b or node in c]
            p_BC = self.get_prob_var(tuple(a_BC))
            a_C: List[Tuple[Node, bool]] = [(node, v) for (node, v) in assignment if node in c]
            if a_C:
                p_C = self.get_prob_var(tuple(a_C))
                a_AC: List[Tuple[Node, bool]] = [(node, v) for (node, v) in assignment if node in a or node in c]
                p_AC = self.get_prob_var(tuple(a_AC))
                constraints.append(p_C * p_ABC == p_BC * p_AC)
            else:
                # a_C is empty, i.e., the constraint is an unconditional independence constraint
                a_A: List[Tuple[Node, bool]] = [(node, v) for (node, v) in assignment if node in a]
                p_A = self.get_prob_var(tuple(a_A))
                constraints.append(p_ABC == p_BC * p_A)
        return constraints

    def distribution_from_model(self, model: z3.ModelRef) -> Distribution:
        """
        Get a distribution object from a z3 model.
        """
        distribution_dict = dict()
        for assignment in self.full_joint_assignments:
            prob_var = self.get_prob_var(assignment)
            distribution_dict[tuple(assignment)] = get_prob_var_value(prob_var, model)
        distribution = Distribution(distribution_dict, self.af.get_nodes())
        distribution.z3_model = model
        return distribution


def prob_name(assignment: Assignment) -> str:
    """
    Generates a fixed name for any assignment.
    Expects a list of tuples of nodes matched to True or False, i.e. [(node_B, False), (node_C, True)].
    Generates a name for the probability of the conjunction of the nodes, i.e. 'p_nB_C'.
    The order is determined by node IDs.
    """
    # assert list(assignment) == sorted(list(assignment))  # enforce sortedness as invariant?
    assignment = sorted(list(assignment))
    name = "p"
    for (arg, b) in assignment:
        name += "_"
        if not b:
            name += "n"
        name += arg.name.upper()  # make the name uppercase to avoid conflicts with the "n" used as prefix
    return name


def get_prob_var_value(prob_var, model: z3.ModelRef):
    """
    Get the value assigned to a probabilistic variable by the given model.
    :return: The value as float
    """
    # Based on https://stackoverflow.com/a/12600208/6620204
    value = model.eval(prob_var)
    if z3.is_int_value(value):
        return value.as_long()
    elif z3.is_rational_value(value):
        return float(value.numerator_as_long())/float(value.denominator_as_long())
    elif z3.is_algebraic_value(value):
        approx_value = value.approx(20)  # an approximation with precision 1/10^20
        return float(approx_value.numerator_as_long())/float(approx_value.denominator_as_long())
    else:
        raise ValueError("Unable to convert to float: " + str(value))


def get_prob_var_value_as_fraction(prob_var, model: z3.ModelRef) -> Fraction:
    """
    Get the value assigned to a probabilistic variable by the given model.
    :return: The value as a Fraction object
    """
    # Based on https://stackoverflow.com/a/12600208/6620204
    value = model.eval(prob_var)
    if z3.is_int_value(value):
        return Fraction(value.as_long())
    elif z3.is_rational_value(value):
        return Fraction(value.numerator_as_long(), value.denominator_as_long())
    elif z3.is_algebraic_value(value):
        approx_value = value.approx(20)
        return Fraction(approx_value.numerator_as_long(), approx_value.denominator_as_long())
    else:
        raise ValueError("Unable to convert to float: " + str(value))
