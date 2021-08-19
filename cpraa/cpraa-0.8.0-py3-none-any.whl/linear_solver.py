from typing import List, Tuple

import numpy as np
import pypoman
import pypoman.polyhedron
import cvxopt

from DPGM import Node
import DPGM as AF
from assignments import Assignment
import assignments as asg
from distribution import Distribution
from timer import Timer


# TODO:
#  - also handle equalities as constraints
#  - sparse matrix representation of constraints?


Constraint = Tuple[np.array, float]

DEFAULT_SOLVER = "glpk"


class LinearConstraintError(Exception):
    pass


def config_solver(solver: str):
    if solver is None:
        return config_solver(DEFAULT_SOLVER)
    if solver == "cvxopt":
        return solver
    if solver == "mosek":
        import mosek
        # suppress output of mosek solver
        cvxopt.solvers.options['mosek'] = {mosek.iparam.log: 0}
        return solver
    if solver == "glpk":
        # suppress output of glpk solver
        cvxopt.solvers.options['glpk'] = {'msg_lev': 'GLP_MSG_OFF'}
        return solver
    raise ValueError("Unknown solver: " + solver)


class LinearSolver:

    def __init__(self, af: AF, solver=DEFAULT_SOLVER):
        self.af = af
        self.solver = config_solver(solver)
        self.all_nodes: List[Node] = sorted(list(af.get_nodes()))
        self.dimension = 2**len(self.all_nodes)

        self.prob_dist_constraints: List[Constraint] = self.generate_prob_dist_constraints()

    def generate_prob_dist_constraints(self):
        constraints = []
        # each entry in the solution vector needs to be larger than zero
        for i in range(self.dimension):
            row = [0] * self.dimension
            row[i] = -1
            constraints.append((row, 0))
        # overall sum equals one
        constraints.append(([1] * self.dimension, 1))
        constraints.append(([-1] * self.dimension, -1))
        return constraints

    def constraint_matrix(self, constraints: List[Constraint]):
        matrix_A_list = []
        vector_b_list = []
        for (row, value) in self.prob_dist_constraints + constraints:
            matrix_A_list.append(row)
            vector_b_list.append(value)

        A = np.array(matrix_A_list)
        b = np.array(vector_b_list)

        # print("\nSystem of linear inequalities:")
        # print("A: \n" + str(A))
        # print("b:", b)
        # print("Solving: A x <= b")

        return A, b

    def constraint_matrix2(self, constraints: List[Constraint]):
        # build matrix directly without using self.prob_dist_constraints
        A = - np.identity(self.dimension)
        b = np.zeros(self.dimension)

        a1 = np.ones(self.dimension)
        a2 = - a1

        print("num constraints:", len(constraints))
        a_list, b_list = list(zip(*constraints))

        A = np.concatenate((A, [a1, a2], a_list))
        b = np.concatenate((b, [1, -1], b_list))

        return A, b

    def constraint_matrix_sparse(self, constraints: List[Constraint]):
        # build matrix directly without using self.prob_dist_constraints

        # sparse representation of diagonal matrix
        # [-1 0] x <= 0
        # [0 -1] x <= 0
        column_indices = list(range(self.dimension))
        row_indices = list(range(self.dimension))
        values = [-1] * self.dimension
        b = [0] * self.dimension
        current_row = self.dimension

        # [1 1] x <= 1
        values.extend([1] * self.dimension)
        column_indices.extend(range(self.dimension))
        row_indices.extend([current_row] * self.dimension)
        b.append(1)
        current_row += 1

        # [-1 -1 x <= -1
        values.extend([-1] * self.dimension)
        column_indices.extend(range(self.dimension))
        row_indices.extend([current_row] * self.dimension)
        b.append(-1)
        current_row += 1

        for (row, value) in constraints:
            if all([x == 0 for x in row]) and value == 0:
                # skip all-zero constraints like [0 0] x <= 0
                continue
            for i in range(self.dimension):
                if row[i] != 0:
                    values.append(int(row[i]))  # conversion to int necessary because the values originate from numpy
                    column_indices.append(i)
                    row_indices.append(current_row)
            b.append(value)
            current_row += 1

        A = cvxopt.spmatrix(values, row_indices, column_indices, tc='d')
        b = cvxopt.matrix(b, tc='d')
        return A, b

    def any_solution(self, constraints: List[Constraint]):
        c = [0] * self.dimension
        return self.optimal_distribution(c, constraints)

    def chebyshev_center(self, constraints: List[Constraint]):
        A, b = self.constraint_matrix(constraints)
        b = cvxopt.matrix(b, tc="d")
        try:
            x = pypoman.polyhedron.compute_chebyshev_center(A, b)
        except Exception as ex:
            if str(ex).startswith("Polytope is empty"):  # thrown by pypoman library
                return None
            else:
                raise ex
        return self.vector_to_distribution(x)

    def corner_distributions(self, constraints: List[Constraint]) -> List[Distribution]:
        A, b = self.constraint_matrix(constraints)

        # computes corners of solution space with A * x <= b
        vertices = pypoman.compute_polytope_vertices(A, b)

        # print("Simplified system:")
        # A, b = pypoman.compute_polytope_halfspaces(vertices)
        # print("A: \n" + str(A))
        # print("b:", b)

        # print("Vertices:", vertices)
        distributions = []
        for vector in vertices:
            distributions.append(self.vector_to_distribution(vector))
        return distributions

    def optimal_distribution(self, cost_vector, constraints: List[Constraint]):
        assert len(cost_vector) == self.dimension

        # A, b = self.constraint_matrix(constraints)
        # A = cvxopt.matrix(A, tc="d")
        # b = cvxopt.matrix(b, tc="d")
        A, b = self.constraint_matrix_sparse(constraints)
        c = cvxopt.matrix(cost_vector, tc="d")

        t = Timer(output_string=self.solver + " solver took")
        # x = pypoman.solve_lp(c, A, b, solver=solver)
        result = cvxopt.solvers.lp(c, A, b, solver=self.solver)
        t.stop()
        status = result['status']
        if status == "optimal":
            x = result['x']
            # print("sum:", sum(x))
            return self.vector_to_distribution(x)
        else:
            # print("Status:", status)
            return None

    def optimize_marginal_prob(self, nodes: List[Node], constraints: List[Constraint], mode="min") -> Distribution:
        """
        Compute the optimal distribution which minimizes (or maximizes) the marginal probability of one or more given
        arguments while observing the given constraints.

        :param nodes: a list of arguments
        :param constraints: a list of linear constraints
        :param mode: "min" (default) or "max"
        :return: a optimal distribution if the constraints are satisfiable
        """
        if mode == "min":
            sign = 1
        elif mode == "max":
            sign = -1
        else:
            raise ValueError("Unknown mode '" + mode + "'. Expected 'min' or 'max'.")
        assignments = []
        for node in nodes:
            assignments.extend(asg.get_node_assignments(node, self.all_nodes))
        cost_vector = sign * self.assignments_to_row(assignments)
        return self.optimal_distribution(cost_vector, constraints)

    def adm_degree(self):
        # todo: this does not completely follow the write-up as all nodes are considered, and not only those whose
        # marginal prob is positive. then again, this is probably not realizable as linear constraints
        rows = []
        for node in self.all_nodes:
            intersection_list = []
            for attacker in node.get_parents():
                union_set = set()
                for defender in attacker.get_parents():
                    if node != defender:
                        # noinspection PyTypeChecker
                        assignment: Assignment = ((node, True), (defender, True))
                    else:
                        assignment = ((node, True),)
                    defender_assignments = asg.sum_out(assignment, self.all_nodes)
                    union_set.update(defender_assignments)
                intersection_list.append(union_set)
            if intersection_list:
                assignments = list(set.intersection(*intersection_list))
                rows.append(self.assignments_to_row(assignments))
        return (1/len(self.all_nodes)) * sum(rows)

    def assignments_to_row(self, assignments: List[Assignment]):
        """
        [((A,False),(B,False)), ((A,True),(B,False))] -> (1 0 1 0)
        """
        row = np.array([0] * self.dimension)
        for assignment in assignments:
            row[asg.to_id(assignment)] = 1.0
        return row

    def constraints_assignments_less_or_equal_value(
            self, assignments: List[Assignment], value) -> List[Constraint]:
        """
        Generate constraints such that the sum of the given assignments is less or equal to the given value.
        """
        row = self.assignments_to_row(assignments)
        return [(row, value)]

    def constraints_assignments_greater_or_equal_value(
            self, assignments: List[Assignment], value) -> List[Constraint]:
        """
        Generate constraints such that the sum of the given assignments is greater or equal to the given value.
        """
        row = -1 * self.assignments_to_row(assignments)
        return [(row, -value)]

    def constraints_assignments_equal_value(
            self, assignments: List[Assignment], value) -> List[Constraint]:
        """
        Generate constraints such that the sum of the given assignments equals the given value.
        """
        return self.constraints_assignments_less_or_equal_value(assignments, value) + \
            self.constraints_assignments_greater_or_equal_value(assignments, value)

    def constraints_assignments_less_or_equal_assignments(
            self, assignments_a: List[Assignment], assignments_b: List[Assignment]) -> List[Constraint]:
        """
        Generate constraints such that the sum of the first assignments is less or equal to the sum of the second
        assignments.
        """
        row_a = self.assignments_to_row(assignments_a)
        row_b = self.assignments_to_row(assignments_b)
        return [(row_a - row_b, 0)]

    def constraints_assignments_greater_or_equal_assignments(
            self, assignments_a: List[Assignment], assignments_b: List[Assignment]) -> List[Constraint]:
        """
        Generate constraints such that the sum of the first assignments is greater or equal to the sum of the second
        assignments.
        """
        row_a = self.assignments_to_row(assignments_a)
        row_b = self.assignments_to_row(assignments_b)
        return [(row_b - row_a, 0)]

    def constraints_assignments_equal_assignments(
            self, assignments_a: List[Assignment], assignments_b: List[Assignment]) -> List[Constraint]:
        """
        Generate constraints such that the sum of the first assignments equals the sum of the second assignments.
        """
        return self.constraints_assignments_less_or_equal_assignments(assignments_a, assignments_b) + \
            self.constraints_assignments_greater_or_equal_assignments(assignments_a, assignments_b)

    def constraints_node_less_or_equal_value(self, node: Node, value) -> List[Constraint]:
        node_full_assignments = asg.get_node_assignments(node, self.all_nodes)
        return self.constraints_assignments_less_or_equal_value(node_full_assignments, value)

    def constraints_node_greater_or_equal_value(self, node: Node, value) -> List[Constraint]:
        node_full_assignments = asg.get_node_assignments(node, self.all_nodes)
        return self.constraints_assignments_greater_or_equal_value(node_full_assignments, value)

    def constraints_node_equals_value(self, node: Node, value) -> List[Constraint]:
        node_full_assignments = asg.get_node_assignments(node, self.all_nodes)
        return self.constraints_assignments_equal_value(node_full_assignments, value)

    def get_node_value(self, node: Node, distribution_vector):
        """
        Return the marginal probability of the given node under the distribution.
        """
        prob_sum = 0
        for a in asg.get_node_assignments(node, self.all_nodes):
            prob_sum += distribution_vector[asg.to_id(a)]
        return prob_sum

    def vector_to_distribution(self, distribution_vector):
        distribution = dict()
        for i in range(self.dimension):
            value = distribution_vector[i]
            distribution[asg.from_id(i, self.all_nodes)] = value
        return Distribution(distribution, self.all_nodes)
