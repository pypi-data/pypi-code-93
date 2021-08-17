from typing import List, Tuple, Any, Set

from DPGM import Node

Assignment = Tuple[Tuple[Node, bool]]  # type alias


# class Assignment:
#     def __init__(self, collection):
#
#         # self.assignment_dict = dict()
#         # for (node, b) in collection:
#         #     self.assignment_dict[node] = b
#
#         self.assignment = tuple(sorted(list(collection)))
#
#     def update(self, node: Node, b: bool):
#         self.assignment_dict[node] = b
#
#     def get_nodes(self) -> List[Node]:
#         return [node for (node, _) in self.assignment]
#
#     def __hash__(self):
#         return self.assignment.__hash__()
#
#     def __eq__(self, other):
#         return self.assignment == other.assignment
#
#     def __repr__(self):
#         return repr(self.assignment)


def generate(ar: list, br: list = (False, True)) -> List[Assignment]:
    """
    Generates all possible assignments of the elements in list 'ar' to elements of list 'br'.
    E.g. ar = [x,y], br = [0,1] -> [[(x,0),(y,0)], [(x,0),(y,1)], [(x,1),(y,0)], [(x,1),(y,1)]]
    """
    combinations: List[List[Tuple[Node, bool]]] = [[]]

    for a in ar:
        next_combinations = []
        for c in combinations:
            for b in br:
                new_c = c.copy()
                new_c.append((a, b))
                next_combinations.append(new_c)
        combinations = next_combinations
    assignments = []
    for c in combinations:
        assignments.append(tuple(c))
    return assignments


def repr_assignment(a: Assignment) -> str:
    strings = []
    for (node, b) in a:
        strings.append((" " if b else "-") + str(node))
    return ",".join(strings)


def to_id(assignment: Assignment):
    """
    Given an assignment like [("A", False), ("B", True), ("C", False)], converts the assignment to a binary string "010"
    and returns the decimal value of it.
    """
    return int("".join(["1" if b else "0" for (_, b) in assignment]), 2)


def from_id(assignment_id: int, nodes: List[Node]) -> Assignment:
    """
    Reverse function of to_id(), i.e., given ID 2 and nodes "ABC", we yield
    [("A", False), ("B", True), ("C", False)].
    """
    assert assignment_id < 2**len(nodes)
    assignment: List[Tuple[Node, bool]] = \
        [(node, c == "1") for (node, c) in zip(nodes, format(assignment_id, "0" + str(len(nodes)) + "b"))]
    return tuple(assignment)


def to_extension(assignment: Assignment):
    """
    [(A,True),(B,False),(C,True)] -> {A,C}
    """
    return set([node for (node, b) in assignment if b])


def from_extension(extension, nodes: List[Node]) -> Assignment:
    """
    Extension {A,C} and nodes [A,B,C] yield [(A,True),(B,False),(C,True)].
    """
    return tuple([(node, node in extension) for node in nodes])


def sum_out(part_assignment: Assignment, all_nodes: List[Node]) -> List[Assignment]:
    """
    Given a partial assignment over some subset of all_nodes, return all full assignments agreeing with the given one.
    E.g., [(A,True),(B,False)], [A,B,C] -> [[(A,True),(B,False),(C,False)], [(A,True),(B,False)(C,True)].

    :param part_assignment: the partial assignment
    :param all_nodes: the list of all nodes
    :returns: the list of all full assignments agreeing with part_assignment
    """
    part_assignment = list(part_assignment)
    part_assignment_args = [arg for (arg, _) in part_assignment]
    remaining_args = [arg for arg in all_nodes if arg not in part_assignment_args]
    assignments_list = []
    for assignment in generate(remaining_args):
        full_assignment = part_assignment + list(assignment)
        full_assignment.sort()
        assignments_list.append(tuple(full_assignment))
    return assignments_list


def get_node_assignments(node: Node, nodes: List[Node], node_assignment=True) -> List[Assignment]:
    """
    Return the list of all assignments over `nodes` under which the given node has the given node assignment.
    """
    return sum_out(((node, node_assignment),), nodes)


def positive_cnf_assignments(clauses: List[List[Any]], all_nodes: List[Any]) -> List[Assignment]:
    """
    Given a positive CNF (i.e. without any negation in front of literals), return all full assignments which satisfy the
    CNF. E.g., for  (A OR B) AND (B OR C), given as [[A, B], [B, C]], return (A B C), (A B -C), (-A B C), -(A B -C) and
    (A -B C).

    :param clauses: A list of the conjunctive clauses of the positive CNF
    :param all_nodes: all nodes to be considered, i.e. all nodes of the AF in most cases
    :return: A list of all full assignments which satisfy the CNF
    """
    candidates: List[Set[Tuple[Node, bool]]] = [set()]
    given_arguments = set()
    for clause in clauses:
        given_arguments.update(clause)
        clause_assignments = generate(clause, [False, True])
        # Clauses contain disjunctive literals, so a true assignment is any assignment which assigns true at least
        # once. Filter out the first result from 'assignments' function because this assigns False to all literals.
        true_clause_assignments = clause_assignments[1:]

        new_candidates = []
        for candidate in candidates:
            # e.g. candidate = [(A, True), (B, False)]
            for true_clause_assignment in true_clause_assignments:
                # e.g. true_clause_assignment = [(B, False), (C, True)]
                # check whether the arguments appearing in both assignments are assigned the same value
                skip = False
                for (node, b) in true_clause_assignment:
                    if (node, not b) in candidate:
                        skip = True
                        break
                # if so, add the new arguments to the candidate
                if not skip:
                    new_candidate = candidate.copy()
                    new_candidate.update(true_clause_assignment)
                    new_candidates.append(new_candidate)
        candidates = new_candidates

    # arguments not present in the cnf can take on any value, so each previous candidate is extended by all possible
    # assignments of the remaining arguments
    remaining_arguments = set(all_nodes).difference(given_arguments)
    remaining_assignments = generate(list(remaining_arguments))
    final_candidates: List[Assignment] = []
    for candidate in candidates:
        for remaining_assignment in remaining_assignments:
            final_candidate = candidate.copy()
            final_candidate.update(remaining_assignment)
            final_candidates.append(tuple(sorted(list(final_candidate))))
    return final_candidates
