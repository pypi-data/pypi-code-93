import logging
import treedecomp
import networkx as nx

from partialedge.structure.data_structure import FULL_LENGTH_TUPLE
from partialedge.graph import graph_creation as gc

FULL_LENGTH_BONUS = True
FULL_LENGTH_BONUS_FACTOR = 0.001

DEFAULT_LOGGER_NAME = "ped"
VERBOSITY_LEVEL_GENERAL_BAG = logging.INFO - 4
VERBOSITY_LEVEL_NODE_INFORMATION = logging.INFO - 7
VERBOSITY_LEVEL_RECORD_IN = logging.INFO - 6
VERBOSITY_LEVEL_RECORD_OUT = logging.INFO - 5

logging.basicConfig(format="%(message)s\n", level=logging.INFO)


class Record:
    """
    Class managing a valid combination of stub lengths and contains the ink value resulting from them.
    It distinguishes between combination stubs, which are introduced but not yet forgotten,
    and fixed stubs, which have already been determined optimal for the current combination as they have gone through an forget process.
    """

    def __init__(self, combination_set, fixed_set):
        self.combination_stubset = combination_set
        self.fixed_stubset = fixed_set
        self.ink_value = None

    def get_ink_value(self):
        if self.ink_value is None:
            self.ink_value = self.calculate_ink_value()
        return self.ink_value

    def calculate_ink_value(self):
        """
        Ink value is determined by the sum of the two stubsets.
        :return: ink value of record
        """
        return self.combination_stubset.calculate_ink() + self.fixed_stubset.calculate_ink()

    def calculate_ink_with_bonus(self):
        return self.combination_stubset.calculate_ink_with_bonus() + \
               self.fixed_stubset.calculate_ink_with_bonus()

    def __str__(self):
        return "Ink: {:8.5f}\t Candidate Stubs: [{}]\t Optimal Stubs: [{}]".format(self.get_ink_value(), str(self.combination_stubset), str(self.fixed_stubset))

    def generate_valid_records_with_new_node(self, content_node):
        """
        Test if the stub combinations of the new node do not lead to crossings with the current stubs
        and create new records with the valid combinations.
        :param content_node: node being introduced
        :return: list of valid records
        """
        stub_combinations = content_node.get_stub_combinations()
        records = []
        for stub_tuple in stub_combinations:
            if self.combination_stubset.check_valid_with_new_node(content_node, stub_tuple):
                new_record = \
                    Record(
                        combination_set=StubSet(
                            dict({**self.combination_stubset.stub_dict,
                                  **{content_node.intersection_node.index:
                                         (content_node, stub_tuple)}})),
                        fixed_set=StubSet(dict(self.fixed_stubset.stub_dict)))
                records.append(new_record)

        return records


class StubSet:
    """
    Collection containing at most one stub length tuple for one edge.
    The dictionary uses the indexes of intersection nodes as keys and the tuple (content_node, [stub_left, stub_right]) as value.
    Since a particular combination of stubs can be used as dictionary key, it is made hashable.
    """

    def __init__(self, stub_dict):
        self.stub_dict = stub_dict

    def __eq__(self, other):
        return self.stub_dict == other.stub_dict

    def __hash__(self):
        h = 0
        for index, (node, stubs) in self.stub_dict.items():
            h ^= hash((index, node, *stubs))
        return h

    def __str__(self):
        return ", ".join(["({:d}, [{:.5f}, {:.5f}])".format(index, *stubs) for (index, (_, stubs)) in self.stub_dict.items()])

    def calculate_ink(self):
        """
        Sums up all stub lengths in set
        :return: ink value of current stub configuration
        """
        ink_sum = 0
        for node, stub_factors in self.stub_dict.values():
            length = node.intersection_node.get_length()
            ink_value1 = length * stub_factors[0]
            ink_value2 = length * stub_factors[1]
            ink_sum += ink_value1 + ink_value2
        return ink_sum

    def calculate_ink_with_bonus(self):
        """
        Sums up all stub lengths while creating a preference for full length edges
        :return: ink value of stub configuration with bonus
        """
        ink_sum = 0
        for node, stub_factors in self.stub_dict.values():
            length = node.intersection_node.get_length()
            ink_value1 = length * stub_factors[0]
            ink_value2 = length * stub_factors[1]
            ink_sum += ink_value1 + ink_value2
            if stub_factors == FULL_LENGTH_TUPLE:
                ink_sum += length * FULL_LENGTH_BONUS_FACTOR
        return ink_sum

    def check_valid_with_new_node(self, content_node, stub_tuple):
        """
        Test a new stub length tuple for crossings with current stubs
        :param content_node: node being introduced
        :param stub_tuple: stub tuple of new node being tested
        :return: True if cut creates no new crossing else False
        """
        for index, (node, stubs) in self.stub_dict.items():
            new_stub_cross = False
            old_stub_cross = False
            if content_node.intersection_node.index in node.intersections:
                new_stub_cross = stub_tuple[0] > \
                                 content_node.intersections[index][0] or\
                                 stub_tuple[1] > \
                                 content_node.intersections[index][1]
                old_stub_cross = stubs[0] > \
                                 node.intersections[content_node.intersection_node.index][0] or\
                                 stubs[1] > \
                                 node.intersections[content_node.intersection_node.index][1]

            if new_stub_cross and old_stub_cross:
                return False
        return True


class Bag:
    """
    Base class for bag of the nice tree decomposition.
    """

    def __init__(self, index, logger):
        self.index = index
        self.nodes = []
        self.children = None
        self.logger = logger

    def calculate_records(self):
        records = []
        for child in self.children:
            child_records = child.calculate_records()
            records.extend(child_records)

        return records

    def __str__(self):
        return ""


class JoinBag(Bag):
    """
    Performs Join operation of nice tree decomposition
    """

    def __init__(self, index, logger=logging.getLogger()):
        super(JoinBag, self).__init__(index, logger)

    def calculate_records(self):
        record_lists = [child.calculate_records() for child in self.children]

        self.logger.log(VERBOSITY_LEVEL_GENERAL_BAG, "Bag {:d} - Join Bag record calculation".format(self.index))
        for i in range(len(record_lists)):
            self.logger.log(VERBOSITY_LEVEL_RECORD_IN, "Join Child Bag {:d} - available records\n{}".format(self.children[i].index, "\n".join(str(record) for record in record_lists[i])))
        self.logger.log(VERBOSITY_LEVEL_NODE_INFORMATION, "Join Bag {:d} joining nodes {}".format(self.index, str([node.intersection_node.index for node in self.nodes])))

        record_dict = {record.combination_stubset: record for record in record_lists[0]}
        for i in range(1, len(record_lists)):
            for record in record_lists[i]:
                record_dict[record.combination_stubset].fixed_stubset.\
                    stub_dict.update(record.fixed_stubset.stub_dict)

        new_records = record_dict.values()
        for record in new_records:
            record.ink_value = None

        self.logger.log(VERBOSITY_LEVEL_RECORD_OUT, "Join Bag result records\n{}\n".format("\n".join(str(record) for record in new_records)))
        return new_records


class IntroduceBag(Bag):
    """
    Performs Introduce operation of nice tree decomposition
    """

    def __init__(self, index, introduce_node, logger=logging.getLogger()):
        super(IntroduceBag, self).__init__(index, logger)
        self.introduce_node = introduce_node

    def calculate_records(self):
        records = super(IntroduceBag, self).calculate_records()

        self.logger.log(VERBOSITY_LEVEL_GENERAL_BAG, "Bag {:d} - Introduce Bag record calculation".format(self.index))
        self.logger.log(VERBOSITY_LEVEL_RECORD_IN, "Introduce Child Bag {:d} - available records\n{}".format(self.children[0].index, "\n".join(str(record) for record in records)))
        self.logger.log(VERBOSITY_LEVEL_NODE_INFORMATION, "Introduce Bag {:d} introducing node {:d}".format(self.index, self.introduce_node.intersection_node.index))

        introduced_records = []
        for record in records:
            introduced_records.extend(
                record.generate_valid_records_with_new_node(self.introduce_node)
            )

        self.logger.log(VERBOSITY_LEVEL_RECORD_OUT, "Introduce Bag result records\n{}\n".format("\n".join(str(record) for record in introduced_records)))
        return introduced_records

    def __str__(self):
        return "Introduce " + str(self.introduce_node.intersection_node.index)


class ForgetBag(Bag):
    """
    Performs Forget operation of nice tree decomposition.
    """

    def __init__(self, index, forget_node, logger=logging.getLogger()):
        super(ForgetBag, self).__init__(index, logger)
        self.forget_node = forget_node

    def calculate_records(self):
        records = super(ForgetBag, self).calculate_records()

        self.logger.log(VERBOSITY_LEVEL_GENERAL_BAG, "Bag {:d} - Forget Bag record calculation".format(self.index))
        self.logger.log(VERBOSITY_LEVEL_RECORD_IN, "Forget Child Bag {:d} - available records\n{}".format(self.children[0].index, "\n".join(str(record) for record in records)))
        self.logger.log(VERBOSITY_LEVEL_NODE_INFORMATION, "Forget Bag {:d} forgetting node {:d}".format(self.index, self.forget_node.intersection_node.index))

        set_dict = dict()
        forgotten_index = self.forget_node.intersection_node.index
        for record in records:
            stub_combination = record.combination_stubset
            stub_tuple = stub_combination.stub_dict.pop(forgotten_index)
            record.fixed_stubset.stub_dict[self.forget_node.intersection_node.index] = stub_tuple
            if stub_combination not in set_dict:
                set_dict[stub_combination] = record
            elif set_dict[stub_combination].get_ink_value() < record.get_ink_value():
                set_dict[stub_combination] = record
            elif set_dict[stub_combination].get_ink_value() == record.get_ink_value() and\
                    set_dict[stub_combination].calculate_ink_with_bonus() < \
                    record.calculate_ink_with_bonus():
                set_dict[stub_combination] = record

        self.logger.log(VERBOSITY_LEVEL_RECORD_OUT, "Forget Bag result records\n{}\n".format("\n".join(str(record) for record in set_dict.values())))
        return set_dict.values()

    def __str__(self):
        return "Forget " + str(self.forget_node.intersection_node.index)


class LeafBag(Bag):
    """
    Initiates data structures for parents in nice tree decomposition
    """

    def __init__(self, index, logger=logging.getLogger()):
        super(LeafBag, self).__init__(index, logger)

    def calculate_records(self):
        self.logger.log(VERBOSITY_LEVEL_GENERAL_BAG, "Bag {:d} - Leaf Bag record calculation".format(self.index))

        record_list = [Record(combination_set=StubSet(dict()), fixed_set=StubSet(dict()))]

        self.logger.log(VERBOSITY_LEVEL_RECORD_OUT, "Leaf Bag result records\n{}\n".format(record_list[0]))
        return record_list

    def __str__(self):
        return "Leaf"


def determine_treewidth(graph):
    """
    Calls htd tree decomposition and uses the result to create a custom ped bag data structure
    :param graph: intersection graph used for tree decomposition
    :return: treewidth of tree decomposition
    """
    nb_nodes = len(graph.nodes)
    edges = [[edge.nodes[0].index, edge.nodes[1].index] for edge in graph.edges]
    decomposition = treedecomp.TreeDecompositionFactory(maxdiffsize=1).create(nb_nodes, edges)
    return decomposition.treewidth()


def form_tree_decomposition(intersection_graph, symmetric, logger=logging.getLogger(DEFAULT_LOGGER_NAME)):
    """
    Creates a data structure of ped bag classes based on the htd tree decomposition
    :param intersection_graph: graph used for tree decomposition
    :param symmetric: determines if content is prepared for SPED or PED
    :return: root bag of tree decomposition
    """

    content_nodes = gc.create_content_nodes(intersection_graph, symmetric=symmetric)
    nb_nodes = len(intersection_graph.nodes)
    edges = [[edge.nodes[0].index, edge.nodes[1].index] for edge in intersection_graph.edges]
    decomposition = treedecomp.TreeDecompositionFactory(maxdiffsize=1).create(nb_nodes, edges)
    bags = decomposition.get_bags()
    decomp_edges = decomposition.get_edges()
    nx_tree = nx.Graph()
    nx_tree.add_edges_from(decomposition.get_edges())
    new_bag_index = max(nx_tree.nodes) + 1

    isolated_nodes = []

    # create bag objects from tree decomposition while making resulting bag structure nice
    def set_bags(root, parent=None):
        nonlocal new_bag_index

        children = list(nx_tree.neighbors(root))
        if parent is not None:
            children.remove(parent)

        def connect_bags(new_nodes, old_nodes, child_bag, parent_bag):
            nonlocal new_bag_index
            to_introduce = set(new_nodes) - set(old_nodes)
            if to_introduce:
                introduce = next(iter(to_introduce))
                introduce_bag = IntroduceBag(new_bag_index, content_nodes[introduce], logger)
                new_bag_index += 1
                introduce_bag.nodes = [content_nodes[node_index] for node_index in new_nodes]
                introduce_bag.children = [connect_bags(set(new_nodes) - {introduce}, old_nodes, child_bag, parent_bag)]
                return introduce_bag

            to_forget = set(old_nodes) - set(new_nodes)
            if to_forget:
                forget = next(iter(to_forget))
                forget_bag = ForgetBag(new_bag_index, content_nodes[forget], logger)
                new_bag_index += 1
                forget_bag.nodes = [content_nodes[node_index] for node_index in set(new_nodes) - {forget}]
                forget_bag.children = [connect_bags(set(new_nodes) | {forget}, old_nodes, child_bag, parent_bag)]
                return forget_bag

            if not old_nodes:
                if isolated_nodes:
                    bag_index = isolated_nodes.pop()

                    forget = next(iter(bags[bag_index]))
                    forget_bag = ForgetBag(new_bag_index, content_nodes[forget], logger)
                    new_bag_index += 1
                    forget_bag.nodes = []
                    forget_bag.children = [connect_bags({forget}, [], None, parent_bag)]
                    return forget_bag

                leaf_bag = LeafBag(new_bag_index, logger)
                new_bag_index += 1
                return leaf_bag

            return set_bags(child_bag, parent_bag)

        def join_reduce(join_children, parent_bag):
            nonlocal new_bag_index

            if len(join_children) == 1:
                join_child = next(iter(join_children))
                return connect_bags(bags[parent_bag], bags[join_child], join_child, parent_bag)

            join_reduce_bag = JoinBag(new_bag_index, logger)
            new_bag_index += 1
            join_reduce_bag.nodes = [content_nodes[node_index] for node_index in bags[parent_bag]]
            join_reduce_bag.children = [connect_bags(bags[parent_bag], bags[join_children[0]], join_children[0], parent_bag), join_reduce(join_children[1:], parent_bag)]
            return join_reduce_bag

        if not children:
            return connect_bags(bags[root], [], None, root)

        elif len(children) == 1:
            child = next(iter(children))
            return connect_bags(bags[root], bags[child], child, root)

        elif len(children) > 1:
            isolated = []
            full = []

            for child in children:
                if len(bags[child]) == 1 and len(list(nx_tree.neighbors(child))) <= 1 and not (next(iter(bags[child])) in bags[root]):
                    isolated.append(child)
                else:
                    full.append(child)
            while len(full) < 2:
                full.append(isolated.pop())

            isolated_nodes.extend(isolated)

            join_bag = JoinBag(root, logger)
            join_bag.nodes = [content_nodes[node_index] for node_index in bags[root]]
            join_bag.children = [connect_bags(bags[root], bags[full[0]], full[0], root), join_reduce(full[1:], root)]
            return join_bag

    root_bag = set_bags(0, None)
    return root_bag, decomposition.treewidth()

